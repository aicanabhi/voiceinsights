from datetime import datetime
from pydantic import BaseModel


class TranscriptResponse(BaseModel):
    id: int
    media_id: int
    transcript: str
    language: str
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }