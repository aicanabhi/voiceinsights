from typing import Optional

from pymongo import ReturnDocument

from app.db.mongo import organization_agents_collection


class OrganizationAgentRepository:
    """An agent is keyed by (organization_id, provider) -- one configuration
    per provider per organization."""

    @staticmethod
    async def create(agent_data: dict) -> str:
        result = await organization_agents_collection.insert_one(agent_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_by_organization(organization_id: int) -> list[dict]:

        cursor = organization_agents_collection.find(
            {
                "organization_id": organization_id
            }
        )

        return await cursor.to_list(length=None)

    @staticmethod
    async def get_by_organization_provider(
        organization_id: int,
        provider: str
    ) -> Optional[dict]:

        return await organization_agents_collection.find_one(
            {
                "organization_id": organization_id,
                "provider": provider
            }
        )

    @staticmethod
    async def get_all() -> list[dict]:

        cursor = organization_agents_collection.find()

        return await cursor.to_list(length=None)

    @staticmethod
    async def update(
        organization_id: int,
        provider: str,
        data: dict
    ) -> Optional[dict]:

        return await organization_agents_collection.find_one_and_update(
            {
                "organization_id": organization_id,
                "provider": provider
            },
            {
                "$set": data
            },
            return_document=ReturnDocument.AFTER
        )

    @staticmethod
    async def delete(
        organization_id: int,
        provider: str
    ) -> int:

        result = await organization_agents_collection.delete_one(
            {
                "organization_id": organization_id,
                "provider": provider
            }
        )

        return result.deleted_count

    @staticmethod
    async def delete_by_organization(organization_id: int) -> int:

        result = await organization_agents_collection.delete_many(
            {
                "organization_id": organization_id
            }
        )

        return result.deleted_count
