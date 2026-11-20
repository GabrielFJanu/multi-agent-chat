from datetime import datetime

from pydantic import BaseModel, Field

from multi_agent_chat.schemas.common import PartialUpdate


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    user_id: int | None
    agent_id: int | None
    content: str
    created_at: datetime
    updated_at: datetime


class MessageUpdate(PartialUpdate):
    content: str | None = Field(default=None, min_length=1)


class MessageReplace(MessageCreate):
    pass
