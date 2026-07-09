from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript


class TranscriptRepository:

    @staticmethod
    async def create(db: AsyncSession, transcript: Transcript):
        db.add(transcript)
        await db.commit()
        await db.refresh(transcript)
        return transcript

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(select(Transcript))
        return result.scalars().all()