from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.transcript import TranscriptResponse
from app.services.transcript_service import TranscriptService

router = APIRouter(
    prefix="/transcripts",
    tags=["Transcripts"]
)


@router.post(
    "/{media_id}",
    response_model=TranscriptResponse
)
async def create_transcript(
    media_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await TranscriptService.create_dummy_transcript(
        db,
        media_id
    )


@router.get(
    "/",
    response_model=list[TranscriptResponse]
)
async def get_all_transcripts(
    db: AsyncSession = Depends(get_db)
):
    return await TranscriptService.get_all_transcripts(
        db
    )