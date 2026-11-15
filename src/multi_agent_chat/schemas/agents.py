from datetime import datetime

from pydantic import BaseModel


class AgentCreate(BaseModel):
    name: str
    description: str
    model: str
    system_prompt: str
    temperature: float


class AgentResponse(BaseModel):
    id: int
    name: str
    description: str
    model: str
    system_prompt: str
    temperature: float
    created_at: datetime
    updated_at: datetime


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    temperature: float | None = None


class AgentReplace(AgentCreate):
    pass
