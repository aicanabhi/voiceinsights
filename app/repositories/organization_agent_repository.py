from bson import ObjectId

from app.db.mongo import organization_agents_collection


class OrganizationAgentRepository:

    @staticmethod
    async def create(agent_data: dict):
        result = await organization_agents_collection.insert_one(agent_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_by_organization(organization_id: int):

        print("========== Mongo Search ==========")
        print("Organization ID:", organization_id)

        agent = await organization_agents_collection.find_one(
            {
                "organization_id": organization_id
            }
        )

        print("Agent Found:", agent)
        print("==================================")

        if agent:
            agent["_id"] = str(agent["_id"])

        return agent

    @staticmethod
    async def get_all():

        cursor = organization_agents_collection.find()

        agents = await cursor.to_list(length=None)

        for agent in agents:
            agent["_id"] = str(agent["_id"])

        return agents

    @staticmethod
    async def update(
        agent_id: str,
        data: dict
    ):

        await organization_agents_collection.update_one(
            {
                "_id": ObjectId(agent_id)
            },
            {
                "$set": data
            }
        )

        updated_agent = await organization_agents_collection.find_one(
            {
                "_id": ObjectId(agent_id)
            }
        )

        if updated_agent:
            updated_agent["_id"] = str(updated_agent["_id"])

        return updated_agent

    @staticmethod
    async def delete(
        agent_id: str
    ):

        await organization_agents_collection.delete_one(
            {
                "_id": ObjectId(agent_id)
            }
        )

        return {
            "message": "Organization Agent deleted successfully"
        }