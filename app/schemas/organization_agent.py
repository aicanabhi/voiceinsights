from typing import Optional
from pydantic import BaseModel

from app.models.enums import TranscriptProvider, Language


class OrganizationAgentCreate(BaseModel):
    organization_id: int
    agent_name: str

    provider: TranscriptProvider
    model: str
    language: Language

    system_prompt: str
    security_key: str

    status: str = "ACTIVE"


class OrganizationAgentUpdate(BaseModel):
    agent_name: Optional[str] = None

    provider: Optional[TranscriptProvider] = None
    model: Optional[str] = None
    language: Optional[Language] = None

    system_prompt: Optional[str] = None
    security_key: Optional[str] = None

    status: Optional[str] = None