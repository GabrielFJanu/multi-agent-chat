from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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


class MessageUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)

    @field_validator('content')
    @classmethod
    def content_cannot_be_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError('Content cannot be null')
        return value


class MessageReplace(BaseModel):
    content: str = Field(min_length=1)
