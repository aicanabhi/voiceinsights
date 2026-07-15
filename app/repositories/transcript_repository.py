from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript


class TranscriptRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        transcript: Transcript
    ):
        db.add(transcript)
        await db.commit()
        await db.refresh(transcript)
        return transcript

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        transcript_id: int
    ):
        result = await db.execute(
            select(Transcript).where(
                Transcript.id == transcript_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_media_id(
        db: AsyncSession,
        media_id: int
    ):
        result = await db.execute(
            select(Transcript).where(
                Transcript.media_id == media_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):
        result = await db.execute(
            select(Transcript)
        )

        return result.scalars().all()

    @staticmethod
    async def delete(
        db: AsyncSession,
        transcript: Transcript
    ):
        await db.delete(transcript)
        await db.commit()