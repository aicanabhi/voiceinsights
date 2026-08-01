import os
import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media
from app.repositories.media_repository import MediaRepository


class MediaService:

    @staticmethod
    async def upload_audio(
        db: AsyncSession,
        file: UploadFile,
        organization_id: int,
        uploaded_by: int
    ):

        os.makedirs("uploads", exist_ok=True)

        filename = f"{uuid.uuid4()}_{file.filename}"

        filepath = os.path.join(
            "uploads",
            filename
        )

        content = await file.read()

        with open(filepath, "wb") as f:
            f.write(content)

        media = Media(
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            original_filename=file.filename,
            stored_filename=filename,
            file_path=filepath,
            file_size=len(content),
            content_type=file.content_type,
            upload_status="UPLOADED"
        )

        return await MediaRepository.create(
            db,
            media
        )