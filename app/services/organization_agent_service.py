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

    @staticmethod
    async def get_all_agents():
        return await OrganizationAgentRepository.get_all()

    @staticmethod
    async def update_agent(
        agent_id: str,
        data
    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "rules" in update_data:
            update_data["rules"] = (
                update_data["rules"].model_dump()
            )

        return await OrganizationAgentRepository.update(
            agent_id,
            update_data
        )

    @staticmethod
    async def delete_agent(
        agent_id: str
    ):

        return await OrganizationAgentRepository.delete(
            agent_id
        )