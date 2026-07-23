from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media


class MediaRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        media: Media
    ):
        db.add(media)
        await db.commit()
        await db.refresh(media)
        return media

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        media_id: int
    ):
        result = await db.execute(
            select(Media).where(
                Media.id == media_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):
        result = await db.execute(
            select(Media)
        )

        return result.scalars().all()