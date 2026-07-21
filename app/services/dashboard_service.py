from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    @staticmethod
    async def get_super_admin_dashboard(
        db: AsyncSession
    ):
        return await DashboardRepository.get_super_admin_dashboard(db)

    @staticmethod
    async def get_organization_dashboard(
        db,
        organization_id: int
    ):
        return await DashboardRepository.get_organization_dashboard(
            db,
            organization_id
        )    

    @staticmethod
    async def get_team_dashboard(
        db: AsyncSession,
        team_id: int
    ):
        return await DashboardRepository.get_team_dashboard(
            db,
            team_id
        )

    @staticmethod
    async def get_agent_dashboard(
        db: AsyncSession,
        agent_id: int
    ):
        return await DashboardRepository.get_agent_dashboard(
            db,
            agent_id
        )