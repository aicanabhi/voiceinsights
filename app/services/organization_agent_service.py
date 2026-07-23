from app.repositories.organization_agent_repository import (
    OrganizationAgentRepository
)


class OrganizationAgentService:


    @staticmethod
    async def create_agent(data):

        agent = {

            "organization_id": data.organization_id,

            "agent_name": data.agent_name,

            "description": data.description,

            "system_prompt": data.system_prompt,

            "rules": data.rules.model_dump(),

            "status": "ACTIVE"
        }


        return await OrganizationAgentRepository.create(
            agent
        )



    @staticmethod
    async def get_agent(
        organization_id: int
    ):

        return await OrganizationAgentRepository.get_by_organization(
            organization_id
        )