from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import TranscriptProvider, UserRole
from app.models.user import User
from app.schemas.organization_agent import (
    OrganizationAgentCreate,
    OrganizationAgentResponse,
    OrganizationAgentUpdate,
)
from app.services.organization_agent_service import (
    OrganizationAgentService,
)

router = APIRouter(
    prefix="/organization-agents",
    tags=["Organization Agents"]
)

super_admin_only = Depends(
    require_roles(UserRole.SUPER_ADMIN)
)


# ---------------------------------------
# Create agent for an organization+provider
# Only Super Admin
# ---------------------------------------
@router.post(
    "/",
    response_model=OrganizationAgentResponse,
    dependencies=[super_admin_only]
)
async def create_organization_agent(
    data: OrganizationAgentCreate,
    db: AsyncSession = Depends(get_db)
):
    return await OrganizationAgentService.create_agent(
        db=db,
        data=data
    )


# ---------------------------------------
# List every organization's agents
# Only Super Admin
# ---------------------------------------
@router.get(
    "/",
    response_model=list[OrganizationAgentResponse],
    dependencies=[super_admin_only]
)
async def get_all_organization_agents():
    return await OrganizationAgentService.get_all_agents()


# ---------------------------------------
# All agents of one organization
# Super Admin + that organization's Org Admin
# ---------------------------------------
@router.get(
    "/{organization_id}",
    response_model=list[OrganizationAgentResponse]
)
async def get_organization_agents(
    organization_id: int,
    current_user: User = Depends(get_current_user)
):
    return await OrganizationAgentService.get_agents_for_organization(
        organization_id=organization_id,
        current_user=current_user
    )


# ---------------------------------------
# One organization's agent for a provider
# Super Admin + that organization's Org Admin
# ---------------------------------------
@router.get(
    "/{organization_id}/{provider}",
    response_model=OrganizationAgentResponse
)
async def get_organization_agent(
    organization_id: int,
    provider: TranscriptProvider,
    current_user: User = Depends(get_current_user)
):
    return await OrganizationAgentService.get_agent(
        organization_id=organization_id,
        provider=provider,
        current_user=current_user
    )


# ---------------------------------------
# Update an agent
# Only Super Admin
# ---------------------------------------
@router.put(
    "/{organization_id}/{provider}",
    response_model=OrganizationAgentResponse,
    dependencies=[super_admin_only]
)
async def update_organization_agent(
    organization_id: int,
    provider: TranscriptProvider,
    data: OrganizationAgentUpdate
):
    return await OrganizationAgentService.update_agent(
        organization_id=organization_id,
        provider=provider,
        data=data
    )


# ---------------------------------------
# Delete an agent
# Only Super Admin
# ---------------------------------------
@router.delete(
    "/{organization_id}/{provider}",
    dependencies=[super_admin_only]
)
async def delete_organization_agent(
    organization_id: int,
    provider: TranscriptProvider
):
    return await OrganizationAgentService.delete_agent(
        organization_id=organization_id,
        provider=provider
    )
