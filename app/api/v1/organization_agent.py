from fastapi import APIRouter

from app.schemas.organization_agent import OrganizationAgentCreate
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