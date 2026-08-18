from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import apply_media_scope
from app.models.analysis import Analysis
from app.models.media import Media
from app.models.user import User
from app.models.organization import Organization
from app.models.team import Team


class ReportRepository:

    @staticmethod
    async def get_analysis_data(
        db: AsyncSession,
        current_user: User,
        start_date: date,
        end_date: date,
        organization_id: int | None = None,
        team_id: int | None = None,
        calling_agent_id: int | None = None,
    ):
        """
        Fetch analyzed calls visible to the current user.

        Optional filters:
        - organization_id
        - team_id
        - calling_agent_id

        Each row contains:
        Analysis
        Media
        Calling Agent
        Organization
        Team
        """

        start_datetime = datetime.combine(
            start_date,
            time.min,
        )

        end_datetime = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        )

        statement = (
            select(
                Analysis,
                Media,
                User,
                Organization,
                Team,
            )
            .join(
                Media,
                Analysis.media_id == Media.id,
            )
            .outerjoin(
                User,
                Media.calling_agent_id == User.id,
            )
            .outerjoin(
                Organization,
                Media.organization_id == Organization.id,
            )
            .outerjoin(
                Team,
                User.team_id == Team.id,
            )
            .where(
                Media.created_at >= start_datetime,
                Media.created_at < end_datetime,
                Media.is_deleted.is_not(True),
            )
        )

        # Existing role-based access control.
        statement = apply_media_scope(
            statement,
            current_user,
        )

        # ---------------------------------------------------------
        # OPTIONAL REPORT FILTERS
        # ---------------------------------------------------------

        if organization_id is not None:
            statement = statement.where(
                Media.organization_id == organization_id
            )

        if team_id is not None:
            statement = statement.where(
                User.team_id == team_id
            )

        if calling_agent_id is not None:
            statement = statement.where(
                Media.calling_agent_id == calling_agent_id
            )

        result = await db.execute(statement)

        return result.all()