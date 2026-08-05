from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript

from app.repositories.transcript_repository import TranscriptRepository
from app.services.transcript_segment_service import TranscriptSegmentService


class TranscriptService:

    @staticmethod
    async def create_dummy_transcript(
        db: AsyncSession,
        media_id: int
    ):
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
        db: AsyncSession
    ):
        return await TranscriptRepository.get_all(db)

    @staticmethod
    async def create_transcript(
        db: AsyncSession,
        media_id: int,
        transcript_text: str,
        language: str = "en",
        status: str = "COMPLETED",
        audio_base64: str = None,
        segments: list = None
    ):
        transcript = Transcript(
            media_id=media_id,
            transcript=transcript_text,
            language=language,
            status=status,
            audio_base64=audio_base64
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