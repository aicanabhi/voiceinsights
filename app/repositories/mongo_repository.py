from datetime import datetime

from app.db.mongo import transcript_collection


class MongoRepository:

    @staticmethod
    async def save_transcript(
        media_id: int,
        organization_id: int,
        agent_id: int,
        provider: str,
        transcript: str,
        language: str,
        speaker_segments: list,
    ):

        document = {
            "media_id": media_id,
            "organization_id": organization_id,
            "agent_id": agent_id,
            "provider": provider,
            "language": language,
            "transcript": transcript,
            "speaker_segments": speaker_segments,
            "created_at": datetime.utcnow()
        }

        result = await transcript_collection.insert_one(
            document
        )

        return result.inserted_id

    @staticmethod
    async def get_transcript(
        media_id: int
    ):

        document = await transcript_collection.find_one(
            {
                "media_id": media_id
            }
        )

        return document

    @staticmethod
    async def get_transcript_by_media_id(
        media_id: int
    ):

        document = await transcript_collection.find_one(
            {
                "media_id": media_id
            }
        )

        return document

    @staticmethod
    async def save_analysis(
        media_id: int,
        analysis: dict
    ):

        print("Saving analysis for media:", media_id)

        result = await transcript_collection.update_one(
            {
                "media_id": media_id
            },
            {
                "$set": {
                    "analysis": analysis
                }
            }
        )

        print("Matched:", result.matched_count)
        print("Modified:", result.modified_count)

   