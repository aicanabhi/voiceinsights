from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.access import apply_media_scope
from app.models.analysis import Analysis
from app.models.media import Media
from app.models.user import User


class AnalysisRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        analysis: Analysis
    ):
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        return analysis

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        analysis_id: int
    ):
        result = await db.execute(
            select(Analysis).where(
                Analysis.id == analysis_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_media(
        db: AsyncSession,
        media_id: int
    ):
        result = await db.execute(
            select(Analysis).where(
                Analysis.media_id == media_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):
        result = await db.execute(
            select(Analysis)
        )

        return result.scalars().all()

    @staticmethod
    async def get_by_id_for_user(
        db: AsyncSession,
        analysis_id: int,
        current_user: User
    ):
        result = await db.execute(
            apply_media_scope(
                select(Analysis)
                .join(Media, Analysis.media_id == Media.id)
                .where(Analysis.id == analysis_id),
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
                select(Analysis)
                .join(Media, Analysis.media_id == Media.id),
                current_user
            )
        )

        return result.scalars().all()

    @staticmethod
    async def update(
        db: AsyncSession,
        analysis: Analysis
    ):
        await db.commit()
        await db.refresh(analysis)
        return analysis

    @staticmethod
    async def delete(
        db: AsyncSession,
        analysis: Analysis
    ):
        await db.delete(analysis)
        await db.commit()