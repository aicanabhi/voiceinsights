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

        return agent