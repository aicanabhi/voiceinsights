from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import ensure_team_access, ensure_user_access
from app.models.user import User
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository


class DashboardService:

    @staticmethod
    async def get_super_admin_dashboard(
        db: AsyncSession
    ):
        return await DashboardRepository.get_super_admin_dashboard(db)

    @staticmethod
    async def get_organization_dashboard(
        db: AsyncSession,
        organization_id: int
    ):
        return await DashboardRepository.get_organization_dashboard(
            db,
            organization_id
        )    

    @staticmethod
    async def get_team_dashboard(
        db: AsyncSession,
        team_id: int,
        current_user: User
    ):
        team = await TeamRepository.get_by_id(db, team_id)

        if team is None:
            raise HTTPException(
                status_code=404,
                detail="Team not found."
            )

        ensure_team_access(current_user, team, "dashboard")

        return await DashboardRepository.get_team_dashboard(
            db,
            team_id
        )

    @staticmethod
    async def get_agent_dashboard(
        db: AsyncSession,
        agent_id: int,
        current_user: User
    ):
        agent = await UserRepository.get_by_id(db, agent_id)

        if agent is None:
            raise HTTPException(
                status_code=404,
                detail="Agent not found."
            )

        ensure_user_access(current_user, agent, "dashboard")

        return await DashboardRepository.get_agent_dashboard(
            db,
            agent_id
        )
