from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnalysisBase(BaseModel):
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    compliance_score: Optional[float] = None
    professionalism_score: Optional[float] = None
    empathy_score: Optional[float] = None
    overall_score: Optional[float] = None
    greeting_followed: bool = False
    closing_followed: bool = False
    violations: Optional[str] = None
    recommendations: Optional[str] = None
    ai_feedback: Optional[str] = None


class AnalysisCreate(AnalysisBase):
    media_id: int


class AnalysisResponse(AnalysisBase):
    id: int
    media_id: int
    created_at: datetime

    class Config:
        from_attributes = True