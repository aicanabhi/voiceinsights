from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.transcript import TranscriptResponse
from app.services.transcript_service import TranscriptService

router = APIRouter(
    prefix="/transcripts",
    tags=["Transcripts"]
)


# Seeds fake transcript text -- a testing aid, so keep it off limits.
@router.post(
    "/{media_id}",
    response_model=TranscriptResponse,
    dependencies=[
        Depends(
            require_roles(UserRole.SUPER_ADMIN)
        )
    ]
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await TranscriptService.get_all_transcripts(
        db,
        current_user
    )
