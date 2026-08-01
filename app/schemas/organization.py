from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    domain: str
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    domain: str
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }