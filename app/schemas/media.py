from datetime import datetime

from pydantic import BaseModel

from app.models.enums import MediaStatus
from app.schemas.analysis import AnalysisResponse
from app.schemas.transcript import (
    TranscriptResponse,
    TranscriptSegmentResponse,
)


class MediaResponse(BaseModel):
    id: int
    organization_id: int
    uploaded_by: int
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int | None = None
    content_type: str | None = None

    status: MediaStatus
    error_message: str | None = None
    attempts: int
    started_at: datetime | None = None
    completed_at: datetime | None = None

    provider: str
    model: str
    language: str
    is_deleted: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class MediaCreate(BaseModel):
    calling_agent_id: int


class AcceptedUpload(BaseModel):
    media_id: int
    filename: str
    status: MediaStatus


class RejectedUpload(BaseModel):
    filename: str | None = None
    reason: str


class UploadBatchResponse(BaseModel):
    """Per-file outcome: a bad file in the batch does not fail the good ones."""

    accepted: list[AcceptedUpload]
    rejected: list[RejectedUpload]


class SpeakerStats(BaseModel):
    speaker: int
    talk_seconds: float | None = None
    talk_percent: float | None = None
    words: int
    words_per_minute: float | None = None
    longest_turn_seconds: float | None = None


class Interruption(BaseModel):
    at_seconds: float | None = None
    by_speaker: int
    overlap_seconds: float | None = None


class CallMetrics(BaseModel):
    """Derived from the stored segments -- no provider or LLM call involved."""

    duration_seconds: float | None = None
    speech_seconds: float | None = None
    silence_seconds: float | None = None
    longest_silence_seconds: float | None = None
    longest_silence_at: float | None = None

    segments: int
    turns: int

    interruptions: int
    interruption_details: list[Interruption] = []

    avg_response_latency_seconds: float | None = None
    max_response_latency_seconds: float | None = None

    speakers: list[SpeakerStats] = []
    talk_ratio: float | None = None

    low_confidence_segments: int | None = None
    average_confidence: float | None = None


class CallResultResponse(BaseModel):
    """Everything one call produced, in a single request.

    transcript/analysis are null while the job is still PENDING or PROCESSING,
    so the same endpoint works as a poll target and as the detail view.
    """

    media: MediaResponse
    transcript: TranscriptResponse | None = None
    segments: list[TranscriptSegmentResponse] = []
    analysis: AnalysisResponse | None = None

    metrics: CallMetrics | None = None

    audio_url: str
    has_diarization: bool
