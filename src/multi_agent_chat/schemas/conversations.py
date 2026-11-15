from datetime import datetime

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationUpdate(BaseModel):
    title: str | None = None


class ConversationReplace(ConversationCreate):
    pass
