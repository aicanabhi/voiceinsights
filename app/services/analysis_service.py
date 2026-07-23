from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.repositories.organization_agent_repository import (
    OrganizationAgentRepository
)

from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.media_repository import MediaRepository
from app.repositories.mongo_repository import MongoRepository

from app.services.groq_service import GroqService


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

        transcript_doc = await MongoRepository.get_transcript_by_media_id(
            media.id
        )

        if transcript_doc is None:
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
            transcript_doc["transcript"],
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

        saved_analysis = await AnalysisRepository.create(
            db,
            analysis
        )

        print("Analysis saved in PostgreSQL")

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

        print("Mongo update completed")

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