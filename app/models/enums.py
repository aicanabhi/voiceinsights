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