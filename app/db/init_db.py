from app.db.database import engine
from app.db.base import Base

# Import all models
from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User

import asyncio


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())