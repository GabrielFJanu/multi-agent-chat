from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserList(BaseModel):
    users: list[UserResponse]


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserReplace(UserCreate):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class PaginationParams(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)
