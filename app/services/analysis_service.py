import asyncio

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
        media_id: int,
        current_user
    ):

        # Scoped fetch: media the caller may not see reads as "not found".
        media = await MediaRepository.get_by_id_for_user(
            db,
            media_id,
            current_user
        )

        if media is None:
            raise Exception("Media not found.")

        transcript = await TranscriptRepository.get_by_media_id(
            db,
            media.id
       )

        if transcript is None:
            raise Exception("Transcript not found.")

        # Use the agent the transcript was actually produced with, so the
        # analysis prompt matches the provider stored on the media row.
        agent = await OrganizationAgentRepository.get_by_organization_provider(
            media.organization_id,
            media.provider
        )

        if agent is None:
            raise Exception(
                f"No {media.provider} agent found for organization "
                f"{media.organization_id}"
            )

        # Blocking LLM call -- keep it off the event loop.
        ai_result = await asyncio.to_thread(
            groq_service.analyze_transcript,
            transcript.transcript,
            agent["system_prompt"]
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


        return saved_analysis

    @staticmethod
    async def get_analysis(
        db: AsyncSession,
        analysis_id: int,
        current_user
    ):
        return await AnalysisRepository.get_by_id_for_user(
            db,
            analysis_id,
            current_user
        )

    @staticmethod
    async def get_all_analysis(
        db: AsyncSession,
        current_user
    ):
        return await AnalysisRepository.get_all_for_user(
            db,
            current_user
        )