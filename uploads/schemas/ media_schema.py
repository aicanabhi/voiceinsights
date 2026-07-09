from datetime import datetime
from pydantic import BaseModel


class MediaResponse(BaseModel):
    id: int
    organization_id: int
    uploaded_by: int
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int | None = None
    content_type: str | None = None
    upload_status: str
    created_at: datetime

    class Config:
        from_attributes = True