from pydantic import BaseModel, EmailStr
from datetime import datetime


class OrganizationCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    website: str | None = None
    industry: str


class OrganizationUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    website: str | None = None
    industry: str | None = None
    is_active: bool | None = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: str
    website: str | None
    industry: str
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }