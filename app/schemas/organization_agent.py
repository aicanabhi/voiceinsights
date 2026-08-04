from typing import Optional
from pydantic import BaseModel


class AgentRules(BaseModel):
    check_greeting: bool
    check_closing: bool
    check_empathy: bool
    check_professionalism: bool


class OrganizationAgentCreate(BaseModel):
    organization_id: int
    agent_name: str
    description: str
    system_prompt: str
    rules: AgentRules


class OrganizationAgentUpdate(BaseModel):
    agent_name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    rules: Optional[AgentRules] = None
    status: Optional[str] = None