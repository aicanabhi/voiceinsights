import os
import uuid

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media
from app.repositories.media_repository import MediaRepository

from app.services.deepgram_service import DeepgramService
from app.services.transcript_service import TranscriptService


UPLOAD_DIR = "uploads"

deepgram_service = DeepgramService()
transcript_service = TranscriptService()

class MediaService:

    @staticmethod
    async def upload_file(
        db: AsyncSession,
        organization_id: int,
        uploaded_by: int,
        file: UploadFile
    ):

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        extension = os.path.splitext(file.filename)[1]

        stored_filename = f"{uuid.uuid4()}{extension}"

        file_path = os.path.join(
            UPLOAD_DIR,
            stored_filename
        )

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        media = Media(
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            content_type=file.content_type,
            upload_status="UPLOADED"
        )

        media = await MediaRepository.create(db, media)
        deepgram = DeepgramService()
        response = deepgram.transcribe(media.file_path)
        print(response)
        return media
    @staticmethod
    async def get_all_files(
        db: AsyncSession
    ):
        return await MediaRepository.get_all(db)