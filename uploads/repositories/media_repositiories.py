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