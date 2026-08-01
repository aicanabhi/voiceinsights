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