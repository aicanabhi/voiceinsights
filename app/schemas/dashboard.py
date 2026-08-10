from pydantic import BaseModel


class SuperAdminDashboardResponse(BaseModel):
    organizations: int
    teams: int
    users: int

    uploaded_calls: int
    pending_calls: int
    processing_calls: int
    completed_calls: int
    failed_calls: int

    completed_analysis: int

    average_score: float
    average_compliance: float
    average_professionalism: float
    average_empathy: float

    positive_calls: int
    neutral_calls: int
    negative_calls: int
    other_sentiment_calls: int
class OrganizationDashboardResponse(BaseModel):
    organization: str
    teams: int
    agents: int

    uploaded_calls: int
    pending_calls: int
    processing_calls: int
    completed_calls: int
    failed_calls: int

    completed_analysis: int

    average_score: float
    average_compliance: float
    average_professionalism: float
    average_empathy: float

    positive_calls: int
    neutral_calls: int
    negative_calls: int
    other_sentiment_calls: int

class TeamDashboardResponse(BaseModel):
    team: str
    agents: int
    uploaded_calls: int
    pending_calls: int
    processing_calls: int
    completed_calls: int
    failed_calls: int

    completed_analysis: int

    average_score: float
    average_compliance: float
    average_professionalism: float
    average_empathy: float

    positive_calls: int
    neutral_calls: int
    negative_calls: int
    other_sentiment_calls: int

class AgentDashboardResponse(BaseModel):
    agent: str
    uploaded_calls: int
    pending_calls: int
    processing_calls: int
    completed_calls: int
    failed_calls: int

    completed_analysis: int

    average_score: float
    average_compliance: float
    average_professionalism: float
    average_empathy: float

    positive_calls: int
    neutral_calls: int
    negative_calls: int
    other_sentiment_calls: int