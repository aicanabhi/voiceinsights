from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript

from app.repositories.media_repository import MediaRepository
from app.repositories.transcript_repository import TranscriptRepository
from app.services.transcript_segment_service import TranscriptSegmentService


class TranscriptService:

    @staticmethod
    async def create_dummy_transcript(
        db: AsyncSession,
        media_id: int
    ):
        # Without this the FK violation surfaces as a 500 instead of a 404.
        media = await MediaRepository.get_by_id(db, media_id)

        if media is None:
            raise HTTPException(
                status_code=404,
                detail="Media not found."
            )

        transcript = Transcript(
            media_id=media_id,
            transcript="Hello, this is a dummy transcript generated for testing.",
            language="en",
            status="COMPLETED"
        )

        return await TranscriptRepository.create(
            db,
            transcript
        )

    @staticmethod
    async def get_all_transcripts(
        db: AsyncSession,
        current_user
    ):
        return await TranscriptRepository.get_all_for_user(
            db,
            current_user
        )

    @staticmethod
    async def create_transcript(
        db: AsyncSession,
        media_id: int,
        transcript_text: str,
        language: str = "en",
        status: str = "COMPLETED",
        segments: list = None
    ):
        # Audio itself is served from disk by GET /media/{id}/audio -- it is
        # deliberately not duplicated into the transcripts table.
        transcript = Transcript(
            media_id=media_id,
            transcript=transcript_text,
            language=language,
            status=status
        )

        transcript_obj = await TranscriptRepository.create(
            db,
            transcript
        )

        if segments:
            await TranscriptSegmentService.create_segments(
                db=db,
                transcript_id=transcript_obj.id,
                segments=segments
           )


        return transcript_obj