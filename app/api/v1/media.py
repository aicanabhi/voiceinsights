from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status as http_status,
)
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.upload import MAX_FILES_PER_REQUEST
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.enums import TranscriptProvider
from app.models.user import User
from app.schemas.media import (
    CallResultResponse,
    MediaResponse,
    UploadBatchResponse,
)
from app.services.media_service import MediaService

router = APIRouter(
    prefix="/media",
    tags=["Media"]
)


@router.post(
    "/upload",
    response_model=UploadBatchResponse,
    status_code=http_status.HTTP_202_ACCEPTED
)
async def upload_media(
    calling_agent_id: int,
    provider: TranscriptProvider,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Queue one or more recordings.

    Returns as soon as the files are stored -- transcription runs in the
    worker. Poll GET /media/{id} for status. organization_id and uploaded_by
    come from the token; model and language come from the organization's agent
    config for the chosen provider.
    """

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files uploaded."
        )

    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=(
                f"At most {MAX_FILES_PER_REQUEST} files per request "
                f"(got {len(files)})."
            )
        )

    return await MediaService.enqueue_uploads(
        db,
        current_user,
        calling_agent_id,
        provider,
        files
    )


@router.get(
    "/",
    response_model=list[MediaResponse]
)
async def get_all_media(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await MediaService.get_all_files(db, current_user)


@router.get(
    "/{media_id}",
    response_model=MediaResponse
)
async def get_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Status of one recording: PENDING / PROCESSING / TRANSCRIBED /
    COMPLETED / FAILED, plus error_message and attempts when it failed."""

    return await MediaService.get_media(db, media_id, current_user)


@router.get(
    "/{media_id}/result",
    response_model=CallResultResponse
)
async def get_call_result(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Everything one call produced: status, transcript, speaker segments,
    analysis and the audio link -- in a single request."""

    return await MediaService.get_call_result(
        db,
        media_id,
        current_user
    )


@router.get("/{media_id}/audio")
async def get_media_audio(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Streams the audio straight from disk. FileResponse honours Range
    requests, so players can seek without pulling the whole file."""

    media = await MediaService.get_audio_file(
        db,
        media_id,
        current_user
    )

    return FileResponse(
        path=media.file_path,
        media_type=media.content_type or "application/octet-stream",
        filename=media.original_filename
    )
