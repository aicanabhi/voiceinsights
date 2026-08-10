from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)

database = client.voiceinsights

organization_agents_collection = database.organization_agents


async def init_mongo_indexes():
    """One agent per (organization, provider). Enforced in the database so a
    race between two creates cannot slip a duplicate through."""

    await organization_agents_collection.create_index(
        [
            ("organization_id", 1),
            ("provider", 1),
        ],
        unique=True,
        name="uniq_organization_provider",
    )
