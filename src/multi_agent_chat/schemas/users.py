from datetime import datetime

from pydantic import BaseModel, EmailStr

from multi_agent_chat.models.user import UserRole
from multi_agent_chat.schemas.common import PartialUpdate


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserUpdate(PartialUpdate):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserAdminUpdate(UserUpdate):
    role: UserRole | None = None


class UserReplace(UserCreate):
    pass


class UserAdminReplace(UserReplace):
    role: UserRole
