from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)

database = client.voiceinsights

transcript_collection = database.transcripts

organization_agents_collection = database.organization_agents