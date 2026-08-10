from datetime import datetime
from typing import Optional

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


class TranscriptSegmentResponse(BaseModel):
    """One speaker turn. start_time/end_time drive click-to-seek and the
    highlight that follows audio playback."""

    id: int
    speaker: int
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    confidence: Optional[float] = None

    model_config = {
        "from_attributes": True
    }