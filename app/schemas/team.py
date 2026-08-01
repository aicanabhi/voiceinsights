from pydantic import BaseModel
from typing import Optional


class TeamCreate(BaseModel):
    organization_id: int
    name: str
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TeamResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True