from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User
from app.models.media import Media
from app.models.analysis import Analysis


class DashboardRepository:

    @staticmethod
    async def get_super_admin_dashboard(db: AsyncSession):

        organizations = await db.scalar(
            select(func.count(Organization.id))
        )

        teams = await db.scalar(
            select(func.count(Team.id))
        )

        users = await db.scalar(
            select(func.count(User.id))
        )

        media = await db.scalar(
            select(func.count(Media.id))
        )

        analysis = await db.scalar(
            select(func.count(Analysis.id))
        )

        return {
            "organizations": organizations,
            "teams": teams,
            "users": users,
            "uploaded_calls": media,
            "completed_analysis": analysis
        }

    @staticmethod
    async def get_organization_dashboard(
        db,
        organization_id: int
    ): 

        organization = await db.scalar(
            select(Organization).where(
                Organization.id == organization_id
            )
        )

        teams = await db.scalar(
            select(func.count(Team.id)).where(
                Team.organization_id == organization_id
            )
        )

        agents = await db.scalar(
            select(func.count(User.id)).where(
                User.organization_id == organization_id
            )
        )

        uploaded_calls = await db.scalar(
            select(func.count(Media.id)).where(
                Media.organization_id == organization_id
            )
        )

        media_ids = select(Media.id).where(
            Media.organization_id == organization_id
        )

        completed_analysis = await db.scalar(
            select(func.count(Analysis.id)).where(
                Analysis.media_id.in_(media_ids)
            )
        )


        return {
            "organization": organization.name,
            "teams": teams,
            "agents": agents,
            "uploaded_calls": uploaded_calls,
            "completed_analysis": completed_analysis
        }

    @staticmethod
    async def get_team_dashboard(
        db: AsyncSession,
        team_id: int
    ):

        team = await db.scalar(
            select(Team).where(
                Team.id == team_id
            )
        )

        agents = await db.scalar(
            select(func.count(User.id)).where(
                User.team_id == team_id
            )
        )

        uploaded_calls = await db.scalar(
            select(func.count(Media.id)).where(
                Media.agent_id.in_(
                    select(User.id).where(User.team_id == team_id)
                )
            )
        )

        return {
            "team": team.name,
            "agents": agents,
            "uploaded_calls": uploaded_calls
        }
    @staticmethod
    async def get_agent_dashboard(
        db: AsyncSession,
        agent_id: int
    ):

        agent = await db.scalar(
            select(User).where(
                User.id == agent_id
            )
        )

        if not agent:
            raise HTTPException(
                status_code=404,
                detail="User not Found"
            )

        if agent.role != "AGENT":
            raise HTTPException(
                status_code=400,
                detail="This dashboard is only for agents."
            )
         
        media_ids = select(Media.id).where(
            Media.agent_id == agent_id
        )

        uploaded_calls = await db.scalar(
            select(func.count(Media.id)).where(
                Media.agent_id == agent_id
            )
        )

        completed_analysis = await db.scalar(
            select(func.count(Analysis.id)).where(
                Analysis.media_id.in_(media_ids)
            )
        )

        avg_score = await db.scalar(
            select(func.avg(Analysis.overall_score)).where(
                Analysis.media_id.in_(media_ids)
            )
        )

        avg_compliance = await db.scalar(
            select(func.avg(Analysis.compliance_score)).where(
                Analysis.media_id.in_(media_ids)
            )
        )

        avg_professionalism = await db.scalar(
            select(func.avg(Analysis.professionalism_score)).where(
                Analysis.media_id.in_(media_ids)
            )
        )

        avg_empathy = await db.scalar(
            select(func.avg(Analysis.empathy_score)).where(
                Analysis.media_id.in_(media_ids)
            ) 
        )

        positive = await db.scalar(
            select(func.count(Analysis.id)).where(
                Analysis.media_id.in_(media_ids),
                Analysis.sentiment == "Positive"
            )
        ) 

        neutral = await db.scalar(
            select(func.count(Analysis.id)).where(
                Analysis.media_id.in_(media_ids),
                Analysis.sentiment == "Neutral"
            )
        )

        negative = await db.scalar(
            select(func.count(Analysis.id)).where(
                Analysis.media_id.in_(media_ids),
                Analysis.sentiment == "Negative"
            )
        )

        return {
            "agent": agent.full_name,
            "uploaded_calls": uploaded_calls or 0,
            "completed_analysis": completed_analysis or 0,
            "average_score": round(avg_score or 0, 2),
            "average_compliance": round(avg_compliance or 0, 2),
            "average_professionalism": round(avg_professionalism or 0, 2),
            "average_empathy": round(avg_empathy or 0, 2),
            "positive_calls": positive or 0,
            "neutral_calls": neutral or 0,
            "negative_calls": negative or 0,
        }

