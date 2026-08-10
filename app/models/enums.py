from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    TEAM_LEAD = "TEAM_LEAD"
    AGENT = "AGENT"

class TranscriptProvider(str, Enum):
    DEEPGRAM = "DEEPGRAM"
    ELEVENLABS = "ELEVENLABS"
    CARTESIA = "CARTESIA"

class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    HINGLISH = "hinglish"

class AgentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class Sentiment(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"

    @classmethod
    def normalize(cls, raw) -> str | None:
        """LLM output is free text -- map it onto one of the three buckets so
        dashboards can count it. Anything unrecognised is kept verbatim rather
        than silently dropped."""

        if raw is None:
            return None

        text = str(raw).strip()

        if not text:
            return None

        lowered = text.lower()

        for member in cls:
            if lowered == member.value.lower():
                return member.value

        # "slightly negative", "very positive", ...
        for member in cls:
            if member.value.lower() in lowered:
                return member.value

        return text

class MediaStatus(str, Enum):
    """Lifecycle of one uploaded recording. PENDING rows are the work queue."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    TRANSCRIBED = "TRANSCRIBED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"