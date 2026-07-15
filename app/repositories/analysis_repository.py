from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis


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
    async def get_by_transcript(
        db: AsyncSession,
        transcript_id: int
    ):
        result = await db.execute(
            select(Analysis).where(
                Analysis.transcript_id == transcript_id
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