from app.repositories.organization_agent_repository import (
    OrganizationAgentRepository
)


class OrganizationAgentService:


    @staticmethod
    async def create_agent(data):

        agent = {

            "organization_id": data.organization_id,

            "agent_name": data.agent_name,

            "provider": data.provider.value,

            "model": data.model,

            "language": data.language.value,

            "system_prompt": data.system_prompt,

            "security_key": data.security_key,

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
        organization_id: int,
        data
    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "provider" in update_data:
            update_data["provider"] = update_data["provider"].value

        if "language" in update_data:
            update_data["language"] = update_data["language"].value

        return await OrganizationAgentRepository.update(
            organization_id,
            update_data
        )

    @staticmethod
    async def delete_agent(
        organization_id: int
    ):

        return await OrganizationAgentRepository.delete(
            organization_id
        )