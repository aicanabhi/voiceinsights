import os
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media
from app.models.transcript import Transcript
from app.models.analysis import Analysis

from app.repositories.media_repository import MediaRepository
from app.repositories.transcript_repository import TranscriptRepository
from app.repositories.analysis_repository import AnalysisRepository

from app.services.deepgram_service import DeepgramService
from app.services.groq_service import GroqService

from app.models.transcript_segment import TranscriptSegment
from app.repositories.transcript_segment_repository import TranscriptSegmentRepository


UPLOAD_DIR = "uploads"

deepgram_service = DeepgramService()
groq_service = GroqService()


class MediaService:

    @staticmethod
    async def upload_file(
        db: AsyncSession,
        organization_id: int,
        uploaded_by: int,
        file: UploadFile
    ):

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        extension = os.path.splitext(file.filename)[1]
        stored_filename = f"{uuid.uuid4()}{extension}"

        file_path = os.path.join(
            UPLOAD_DIR,
            stored_filename
        )

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        media = Media(
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            content_type=file.content_type,
            upload_status="UPLOADED"
        )

        media = await MediaRepository.create(db, media)

        # -----------------------------
        # Deepgram Transcription
        # -----------------------------
        deepgram_result = deepgram_service.transcribe(
            media.file_path
        )

        transcript = Transcript(
            media_id=media.id,
            transcript=deepgram_result["transcript"],
            language=deepgram_result["language"],
            status="COMPLETED"
        )

        transcript = await TranscriptRepository.create(
            db,
            transcript
        )

        # -----------------------------
        # Save Transcript Segments
        # -----------------------------
        for seg in deepgram_result["speaker_segments"]:
            transcript_segment = TranscriptSegment(
                transcript_id=transcript.id,
                speaker=seg["speaker"],
                start_time=seg["start"],
                end_time=seg["end"],
                text=seg["text"],
                confidence=seg["confidence"]
            )

            db.add(transcript_segment)

            
        # -----------------------------
        # AI Analysis
        # -----------------------------
        ai_result = groq_service.analyze_transcript(
            transcript.transcript
        )

        analysis = Analysis(
            transcript_id=transcript.id,
            summary=ai_result["summary"],
            sentiment=ai_result["sentiment"],
            compliance_score=ai_result["compliance_score"],
            professionalism_score=ai_result["professionalism_score"],
            empathy_score=ai_result["empathy_score"],
            overall_score=ai_result["overall_score"],
            greeting_followed=ai_result["greeting_followed"],
            closing_followed=ai_result["closing_followed"],
            violations=ai_result["violations"],
            recommendations=ai_result["recommendations"],
            ai_feedback=ai_result["ai_feedback"]
        )

        await AnalysisRepository.create(
            db,
            analysis
        )

        return media