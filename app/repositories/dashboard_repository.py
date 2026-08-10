from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import NOT_DELETED
from app.models.analysis import Analysis
from app.models.enums import MediaStatus, Sentiment, UserRole
from app.models.media import Media
from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User


def _sentiment_is(value: str):
    """Stored values are normalised now, but rows written before that could be
    'positive' or ' Negative '. Match case- and whitespace-insensitively."""

    return func.lower(func.trim(Analysis.sentiment)) == value.lower()


class DashboardRepository:
    """One query for the media/job counts, one for the analysis aggregates.

    Everything here excludes soft-deleted media.
    """

    @staticmethod
    async def _media_stats(db: AsyncSession, scope=None) -> dict:

        statement = select(
            func.count(Media.id).label("total"),
            func.count(Media.id).filter(
                Media.status == MediaStatus.PENDING
            ).label("pending"),
            func.count(Media.id).filter(
                Media.status == MediaStatus.PROCESSING
            ).label("processing"),
            func.count(Media.id).filter(
                Media.status == MediaStatus.COMPLETED
            ).label("completed"),
            func.count(Media.id).filter(
                Media.status == MediaStatus.FAILED
            ).label("failed"),
        ).where(NOT_DELETED)

        if scope is not None:
            statement = statement.where(scope)

        row = (await db.execute(statement)).one()

        return {
            "uploaded_calls": row.total or 0,
            "pending_calls": row.pending or 0,
            "processing_calls": row.processing or 0,
            "completed_calls": row.completed or 0,
            "failed_calls": row.failed or 0,
        }

    @staticmethod
    async def _analysis_stats(db: AsyncSession, scope=None) -> dict:

        statement = (
            select(
                func.count(Analysis.id).label("total"),
                func.avg(Analysis.overall_score).label("avg_score"),
                func.avg(Analysis.compliance_score).label("avg_compliance"),
                func.avg(Analysis.professionalism_score).label("avg_prof"),
                func.avg(Analysis.empathy_score).label("avg_empathy"),
                func.count(Analysis.id).filter(
                    _sentiment_is(Sentiment.POSITIVE.value)
                ).label("positive"),
                func.count(Analysis.id).filter(
                    _sentiment_is(Sentiment.NEUTRAL.value)
                ).label("neutral"),
                func.count(Analysis.id).filter(
                    _sentiment_is(Sentiment.NEGATIVE.value)
                ).label("negative"),
            )
            .select_from(Analysis)
            .join(Media, Analysis.media_id == Media.id)
            .where(NOT_DELETED)
        )

        if scope is not None:
            statement = statement.where(scope)

        row = (await db.execute(statement)).one()

        total = row.total or 0
        positive = row.positive or 0
        neutral = row.neutral or 0
        negative = row.negative or 0

        return {
            "completed_analysis": total,
            "average_score": round(row.avg_score or 0, 2),
            "average_compliance": round(row.avg_compliance or 0, 2),
            "average_professionalism": round(row.avg_prof or 0, 2),
            "average_empathy": round(row.avg_empathy or 0, 2),
            "positive_calls": positive,
            "neutral_calls": neutral,
            "negative_calls": negative,
            # keeps the buckets reconciling with completed_analysis instead of
            # letting unrecognised sentiment values vanish
            "other_sentiment_calls": max(
                total - positive - neutral - negative, 0
            ),
        }

    @staticmethod
    async def get_super_admin_dashboard(db: AsyncSession):

        organizations = await db.scalar(select(func.count(Organization.id)))
        teams = await db.scalar(select(func.count(Team.id)))
        users = await db.scalar(select(func.count(User.id)))

        return {
            "organizations": organizations or 0,
            "teams": teams or 0,
            "users": users or 0,
            **await DashboardRepository._media_stats(db),
            **await DashboardRepository._analysis_stats(db),
        }

    @staticmethod
    async def get_organization_dashboard(
        db: AsyncSession,
        organization_id: int
    ):

        organization = await db.scalar(
            select(Organization).where(
                Organization.id == organization_id
            )
        )

        if organization is None:
            raise HTTPException(
                status_code=404,
                detail="Organization not found."
            )

        teams = await db.scalar(
            select(func.count(Team.id)).where(
                Team.organization_id == organization_id
            )
        )

        agents = await db.scalar(
            select(func.count(User.id)).where(
                User.organization_id == organization_id,
                User.role == UserRole.AGENT,
            )
        )

        scope = Media.organization_id == organization_id

        return {
            "organization": organization.name,
            "teams": teams or 0,
            "agents": agents or 0,
            **await DashboardRepository._media_stats(db, scope),
            **await DashboardRepository._analysis_stats(db, scope),
        }

    @staticmethod
    async def get_team_dashboard(
        db: AsyncSession,
        team_id: int
    ):

        team = await db.scalar(
            select(Team).where(Team.id == team_id)
        )

        if team is None:
            raise HTTPException(
                status_code=404,
                detail="Team not found."
            )

        agents = await db.scalar(
            select(func.count(User.id)).where(
                User.team_id == team_id,
                User.role == UserRole.AGENT,
            )
        )

        team_members = select(User.id).where(User.team_id == team_id)

        # Calls are attributed to the agent who handled them.
        scope = Media.calling_agent_id.in_(team_members)

        return {
            "team": team.name,
            "agents": agents or 0,
            **await DashboardRepository._media_stats(db, scope),
            **await DashboardRepository._analysis_stats(db, scope),
        }

    @staticmethod
    async def get_agent_dashboard(
        db: AsyncSession,
        agent_id: int
    ):

        agent = await db.scalar(
            select(User).where(User.id == agent_id)
        )

        if agent is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        if agent.role != UserRole.AGENT:
            raise HTTPException(
                status_code=400,
                detail="This dashboard is only for agents."
            )

        scope = Media.calling_agent_id == agent_id

        return {
            "agent": agent.full_name,
            **await DashboardRepository._media_stats(db, scope),
            **await DashboardRepository._analysis_stats(db, scope),
        }
