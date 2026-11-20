from datetime import datetime

from pydantic import BaseModel

from multi_agent_chat.schemas.common import PartialUpdate


class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationUpdate(PartialUpdate):
    title: str | None = None


class ConversationReplace(ConversationCreate):
    pass
