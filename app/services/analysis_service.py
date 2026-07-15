from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis

from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.transcript_repository import TranscriptRepository

from app.services.groq_service import GroqService


groq_service = GroqService()


class AnalysisService:

    @staticmethod
    async def analyze_transcript(
        db: AsyncSession,
        transcript_id: int
    ):

        transcript = await TranscriptRepository.get_by_id(
            db,
            transcript_id
        )

        if transcript is None:
            raise Exception("Transcript not found.")

        # AI Analysis using Groq
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

        return await AnalysisRepository.create(
            db,
            analysis
        )

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
        return await AnalysisRepository.get_all(
            db
        )