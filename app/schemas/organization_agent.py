from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants.provider_models import PROVIDER_MODELS
from app.models.enums import AgentStatus, Language, TranscriptProvider


def _validate_model_for_provider(
    provider: TranscriptProvider,
    model: str
) -> str:

    allowed = PROVIDER_MODELS.get(provider.value, [])

    if model not in allowed:
        raise ValueError(
            f"'{model}' is not a valid {provider.value} model. "
            f"Allowed: {', '.join(allowed)}"
        )

    return model


class OrganizationAgentCreate(BaseModel):
    organization_id: int
    agent_name: str = Field(min_length=1, max_length=150)

    provider: TranscriptProvider
    model: str
    language: Language

    system_prompt: str = Field(min_length=1)
    security_key: str = Field(min_length=1)

    status: AgentStatus = AgentStatus.ACTIVE

    @model_validator(mode="after")
    def check_model_belongs_to_provider(self):
        _validate_model_for_provider(self.provider, self.model)
        return self


class OrganizationAgentUpdate(BaseModel):
    agent_name: Optional[str] = Field(default=None, min_length=1, max_length=150)

    # provider is the routing key for an agent, so it is not updatable --
    # switching providers means creating the agent for that provider instead.
    model: Optional[str] = None
    language: Optional[Language] = None

    system_prompt: Optional[str] = Field(default=None, min_length=1)
    security_key: Optional[str] = Field(default=None, min_length=1)

    status: Optional[AgentStatus] = None

    @field_validator("model")
    @classmethod
    def model_not_blank(cls, value: Optional[str]):

        if value is not None and not value.strip():
            raise ValueError("model cannot be blank")

        return value


class OrganizationAgentResponse(BaseModel):
    """Read model. The security_key is deliberately never returned -- callers
    only get to know whether one is configured."""

    id: str
    organization_id: int
    agent_name: str

    provider: TranscriptProvider
    model: str
    language: Language

    system_prompt: str
    has_security_key: bool

    status: AgentStatus

    @classmethod
    def from_document(cls, document: dict) -> "OrganizationAgentResponse":
        return cls(
            id=str(document["_id"]),
            organization_id=document["organization_id"],
            agent_name=document["agent_name"],
            provider=document["provider"],
            model=document["model"],
            language=document["language"],
            system_prompt=document["system_prompt"],
            has_security_key=bool(document.get("security_key")),
            status=document.get("status", AgentStatus.ACTIVE),
        )
