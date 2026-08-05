from fastapi import APIRouter

from app.schemas.organization_agent import OrganizationAgentCreate
from app.services.organization_agent_service import (
    OrganizationAgentService,
)
from app.schemas.organization_agent import (
    OrganizationAgentCreate,
    OrganizationAgentUpdate
)
from app.services.organization_agent_service import (
    OrganizationAgentService,
)

router = APIRouter(
    prefix="/organization-agents",
    tags=["Organization Agents"]
)


@router.post("/")
async def create_organization_agent(
    data: OrganizationAgentCreate
):

    agent_id = await OrganizationAgentService.create_agent(
        data
    )

    return {
        "message": "Organization Agent created successfully",
        "agent_id": agent_id
    }


@router.get("/{organization_id}")
async def get_organization_agent(
    organization_id: int
):

    return await OrganizationAgentService.get_agent(
        organization_id
    )

@router.get("/")
async def get_all_organization_agents():

    return await OrganizationAgentService.get_all_agents()

@router.put("/{organization_id}")
async def update_organization_agent(
    organization_id: int,
    data: OrganizationAgentUpdate
):

    return await OrganizationAgentService.update_agent(
        organization_id,
        data
    )

@router.delete("/{organization_id}")
async def delete_organization_agent(
    organization_id: int
):

    return await OrganizationAgentService.delete_agent(
        organization_id
    )