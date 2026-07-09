from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.media import MediaResponse
from app.services.media_service import MediaService

router = APIRouter(
    prefix="/media",
    tags=["Media"]
)


@router.post(
    "/upload",
    response_model=MediaResponse
)
async def upload_media(
    organization_id: int,
    uploaded_by: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await MediaService.upload_file(
        db,
        organization_id,
        uploaded_by,
        file
    )


@router.get(
    "/",
    response_model=list[MediaResponse]
)
async def get_all_media(
    db: AsyncSession = Depends(get_db)
):
    return await MediaService.get_all_files(db)