from pydantic import BaseModel, EmailStr
from pydantic.experimental.missing_sentinel import MISSING


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserList(BaseModel):
    users: list[UserRead]


class UserUpdate(BaseModel):
    username: str | MISSING = MISSING
    email: EmailStr | MISSING = MISSING
    password: str | MISSING = MISSING


class UserReplace(UserCreate):
    pass
