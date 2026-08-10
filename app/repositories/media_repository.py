from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import apply_media_scope
from app.models.enums import MediaStatus
from app.models.media import Media
from app.models.user import User


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

    @staticmethod
    async def get_by_id_for_user(
        db: AsyncSession,
        media_id: int,
        current_user: User
    ):
        result = await db.execute(
            apply_media_scope(
                select(Media).where(Media.id == media_id),
                current_user
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_for_user(
        db: AsyncSession,
        current_user: User
    ):
        result = await db.execute(
            apply_media_scope(
                select(Media),
                current_user
            )
        )

        return result.scalars().all()

    @staticmethod
    async def claim_next_pending(
        db: AsyncSession
    ):
        """Take the oldest PENDING row and mark it PROCESSING, atomically.

        SKIP LOCKED lets several workers poll the same table without ever
        handing the same row to two of them, and without blocking each other.
        """

        result = await db.execute(
            select(Media)
            .where(Media.status == MediaStatus.PENDING)
            .order_by(Media.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        )

        media = result.scalar_one_or_none()

        if media is None:
            return None

        media.status = MediaStatus.PROCESSING
        media.attempts = (media.attempts or 0) + 1
        media.started_at = datetime.now(timezone.utc)
        media.error_message = None

        await db.commit()
        await db.refresh(media)

        return media

    @staticmethod
    async def mark_status(
        db: AsyncSession,
        media: Media,
        status: MediaStatus,
        error_message: str | None = None
    ):
        media.status = status
        media.error_message = error_message

        if status in (MediaStatus.COMPLETED, MediaStatus.FAILED):
            media.completed_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(media)

        return media