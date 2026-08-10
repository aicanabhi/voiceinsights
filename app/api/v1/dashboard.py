from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import ensure_organization_access
from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
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
    response_model=SuperAdminDashboardResponse,
    dependencies=[
        Depends(
            require_roles(UserRole.SUPER_ADMIN)
        )
    ]
)
async def super_admin_dashboard(
    db: AsyncSession = Depends(get_db)
):
    return await DashboardService.get_super_admin_dashboard(db)


@router.get(
    "/organization/{organization_id}",
    response_model=OrganizationDashboardResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.ORG_ADMIN,
            )
        )
    ]
)
async def organization_dashboard(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_organization_access(
        current_user,
        organization_id,
        "dashboard"
    )

    return await DashboardService.get_organization_dashboard(
        db,
        organization_id
    )


@router.get(
    "/team/{team_id}",
    response_model=TeamDashboardResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN,
                UserRole.ORG_ADMIN,
                UserRole.TEAM_LEAD,
            )
        )
    ]
)
async def team_dashboard(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await DashboardService.get_team_dashboard(
        db,
        team_id,
        current_user
    )


@router.get(
    "/agent/{agent_id}",
    response_model=AgentDashboardResponse
)
async def agent_dashboard(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await DashboardService.get_agent_dashboard(
        db,
        agent_id,
        current_user
    )
