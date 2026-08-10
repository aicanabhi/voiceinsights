from pydantic import BaseModel


class ProviderModels(BaseModel):
    provider: str
    models: list[str]