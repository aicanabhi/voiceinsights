import os
import uuid
import base64
from app.models import transcript
from app.services.transcript_segment_service import TranscriptSegmentService
from fastapi import HTTPException
from app.constants.provider_models import PROVIDER_MODELS

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transcript import Transcript
from app.repositories.transcript_repository import TranscriptRepository

from app.models.media import Media
from app.models.analysis import Analysis
from app.services.transcript_service import TranscriptService

from app.repositories.media_repository import MediaRepository
from app.repositories.analysis_repository import AnalysisRepository

from app.services.deepgram_service import DeepgramService
from app.services.elevenlabs_service import ElevenLabsService
from app.services.cartesia_service import CartesiaService
from app.services.groq_service import GroqService

from app.models.enums import TranscriptProvider,Language
from app.repositories.organization_agent_repository import (
    OrganizationAgentRepository
)
from app.core.config import settings


UPLOAD_DIR = "uploads"
groq_service = GroqService()



class MediaService:

    @staticmethod
    async def upload_file(
        db: AsyncSession,
        organization_id: int,
        uploaded_by: int,
        calling_agent_id: int,
        provider: TranscriptProvider,
        model: str,
        language: Language,
        file: UploadFile
    ):
        provider_name = provider.value
        if provider_name not in PROVIDER_MODELS:
            raise HTTPException(
                status_code=400,
                detail="Invalid provider"
            )
        if model not in PROVIDER_MODELS[provider_name]:
            raise HTTPException(
                status_code=400,
                detail=f"{model} is not a valid model for {provider_name}"
            )

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
            calling_agent_id=calling_agent_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            content_type=file.content_type,
            upload_status="UPLOADED",
            provider=provider.value,
            model=model,
            language=language.value
        )

        media = await MediaRepository.create(db, media)

        with open(media.file_path, "rb") as audio_file:
            audio_base64 = base64.b64encode(
            audio_file.read()
            ).decode("utf-8")

        agent = await OrganizationAgentRepository.get_by_organization_provider(
            organization_id=organization_id,
            provider=provider.value
        )
        if agent is None:
            raise Exception(
                "Organization AI Agent not found"
            )

        if not agent.get("security_key"):
            raise Exception(
                f"No {provider.value} agent configured for this organization."
            )


        if provider == TranscriptProvider.DEEPGRAM:

            api_key = (
                agent.get("security_key")
                or settings.DEEPGRAM_API_KEY
            )

            print("KEY:", settings.DEEPGRAM_API_KEY)
            deepgram_service = DeepgramService(api_key)

            transcript_result = deepgram_service.transcribe(
                media.file_path,
                model,
                language.value
            )


        elif provider == TranscriptProvider.ELEVENLABS:

            api_key = (
                agent.get("security_key")
                or settings.ELEVENLABS_API_KEY
            )

            elevenlabs_service = ElevenLabsService(
                api_key
            )

            transcript_result = elevenlabs_service.transcribe(
                media.file_path,
                model
            )


        elif provider == TranscriptProvider.CARTESIA:

            api_key = (
                agent.get("security_key")
                or settings.CARTESIA_API_KEY
            )

            cartesia_service = CartesiaService(
                api_key
            )

            transcript_result = cartesia_service.transcribe(
                media.file_path,
                model
            )


        else:
            raise Exception("Invalid Provider")

        transcript_obj=await TranscriptService.create_transcript(
            db=db,
            media_id=media.id,
            transcript_text=transcript_result["transcript"],
            language=transcript_result["language"],
            status="COMPLETED",
            audio_base64=audio_base64,
            segments=transcript_result["speaker_segments"]
        )
        await TranscriptSegmentService.create_segments(
            db,
            transcript_obj.id,
            transcript_result["speaker_segments"]
        )


        ai_result = groq_service.analyze_transcript(
            transcript=transcript_result["transcript"],
            system_prompt=agent["system_prompt"],
            
        )
        

        analysis = Analysis(
            media_id=media.id,
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

        print("Analysis saved in MongoDB")


        return media

    @staticmethod
    async def get_all_files(
        db: AsyncSession
    ):
        return await MediaRepository.get_all(db)