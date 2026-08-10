from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript_segment import TranscriptSegment


class TranscriptSegmentRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        segment: TranscriptSegment
    ):
        db.add(segment)
        await db.commit()
        await db.refresh(segment)
        return segment

    @staticmethod
    async def get_by_transcript(
        db: AsyncSession,
        transcript_id: int
    ):
        # Ordered by start time -- a transcript UI reads them top to bottom.
        result = await db.execute(
            select(TranscriptSegment)
            .where(
                TranscriptSegment.transcript_id == transcript_id
            )
            .order_by(
                TranscriptSegment.start_time,
                TranscriptSegment.id
            )
        )

        return result.scalars().all()