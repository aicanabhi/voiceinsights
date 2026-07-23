import os
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media
from app.models.analysis import Analysis

from app.repositories.media_repository import MediaRepository
from app.repositories.analysis_repository import AnalysisRepository

from app.services.deepgram_service import DeepgramService
from app.services.elevenlabs_service import ElevenLabsService
from app.services.cartesia_service import CartesiaService
from app.services.groq_service import GroqService

from app.models.enums import TranscriptProvider
from app.repositories.mongo_repository import MongoRepository
from app.repositories.organization_agent_repository import (
    OrganizationAgentRepository
)


UPLOAD_DIR = "uploads"

deepgram_service = DeepgramService()
elevenlabs_service = ElevenLabsService()
cartesia_service = CartesiaService()
groq_service = GroqService()


class MediaService:

    @staticmethod
    async def upload_file(
        db: AsyncSession,
        organization_id: int,
        uploaded_by: int,
        agent_id: int,
        provider: TranscriptProvider,
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
            agent_id=agent_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            content_type=file.content_type,
            upload_status="UPLOADED"
        )

        media = await MediaRepository.create(db, media)

        if provider == TranscriptProvider.DEEPGRAM:

            transcript_result = deepgram_service.transcribe(
                media.file_path
            )

        elif provider == TranscriptProvider.ELEVENLABS:
            transcript_result = elevenlabs_service.transcribe(
                media.file_path
            )


        elif provider == TranscriptProvider.CARTESIA:
                
            transcript_result = cartesia_service.transcribe(
                media.file_path
            ) 
              

        else:
            raise Exception("Invalid Provider")

        await MongoRepository.save_transcript(
            media_id=media.id,
            organization_id=organization_id,
            agent_id=agent_id,
            provider=provider.value,
            transcript=transcript_result["transcript"],
            language=transcript_result["language"],
            speaker_segments=transcript_result["speaker_segments"]
        )
        


       

            
        agent = await OrganizationAgentRepository.get_by_organization(
            organization_id
        )

        if agent is None:
            raise Exception(
                "Organization AI Agent not found"
            )


        ai_result = groq_service.analyze_transcript(
            transcript=transcript_result["transcript"],
            system_prompt=agent["system_prompt"],
            rules=agent["rules"]
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

        await MongoRepository.save_analysis(
            media_id=media.id,
            analysis={
                "summary": ai_result["summary"],
                "sentiment": ai_result["sentiment"],
                "compliance_score": ai_result["compliance_score"],
                "professionalism_score": ai_result["professionalism_score"],
                "empathy_score": ai_result["empathy_score"],
                "overall_score": ai_result["overall_score"],
                "greeting_followed": ai_result["greeting_followed"],
                "closing_followed": ai_result["closing_followed"],
                "violations": ai_result["violations"],
                "recommendations": ai_result["recommendations"],
                "ai_feedback": ai_result["ai_feedback"]
            }
        )

        print("Analysis saved in MongoDB")


        return media

    @staticmethod
    async def get_all_files(
        db: AsyncSession
    ):
        return await MediaRepository.get_all(db)