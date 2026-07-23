from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.dashboard import (
    SuperAdminDashboardResponse,
    OrganizationDashboardResponse,
    TeamDashboardResponse,
    AgentDashboardResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/super-admin",
    response_model=SuperAdminDashboardResponse
)
async def super_admin_dashboard(
    db: AsyncSession = Depends(get_db)
):
    return await DashboardService.get_super_admin_dashboard(db)

@router.get(
    "/organization/{organization_id}",
    response_model=OrganizationDashboardResponse
)
async def organization_dashboard(
    organization_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await DashboardService.get_organization_dashboard(
        db,
        organization_id
    )

@router.get(
    "/team/{team_id}",
    response_model=TeamDashboardResponse
)
async def team_dashboard(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await DashboardService.get_team_dashboard(
        db,
        team_id
    )
@router.get(
    "/agent/{agent_id}",
    response_model=AgentDashboardResponse
)
async def agent_dashboard(
    agent_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await DashboardService.get_agent_dashboard(
        db,
        agent_id
    )