from app.models import transcript
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.repositories.organization_agent_repository import (
    OrganizationAgentRepository
)

from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.media_repository import MediaRepository
from app.services.groq_service import GroqService
from app.repositories.transcript_repository import TranscriptRepository


groq_service = GroqService()


class AnalysisService:

    @staticmethod
    async def analyze_media(
        db: AsyncSession,
        media_id: int
    ):

        media = await MediaRepository.get_by_id(
            db,
            media_id
        )

        if media is None:
            raise Exception("Media not found.")

        transcript = await TranscriptRepository.get_by_media_id(
            db,
            media.id
       )

        if transcript is None:
            raise Exception("Transcript not found.")

        agent = await OrganizationAgentRepository.get_by_organization(
            media.organization_id
        )

        if agent is None:
            raise Exception(
                f"No AI Agent found for organization {media.organization_id}"
        )
        print(agent)

        ai_result = groq_service.analyze_transcript(
            transcript=transcript.transcript,
            system_prompt=agent["system_prompt"]
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

        saved_analysis = await AnalysisRepository.create(
            db,
            analysis
        )

        print("Analysis saved in PostgreSQL")

        return saved_analysis

    @staticmethod
    async def get_analysis(
        db: AsyncSession,
        analysis_id: int
    ):
        return await AnalysisRepository.get_by_id(
            db,
            analysis_id
        )

    @staticmethod
    async def get_all_analysis(
        db: AsyncSession
    ):
        return await AnalysisRepository.get_all(db)