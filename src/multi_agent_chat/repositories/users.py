from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_chat.core.database import get_session
from multi_agent_chat.models.user import User

Session = Annotated[AsyncSession, Depends(get_session)]


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_data: dict) -> User:
        db_user = User(**create_data)

        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.session.scalars(
            select(User).offset(skip).limit(limit)
        )
        db_users = result.all()
        return db_users

    async def get_by_id(self, user_id: int) -> User | None:
        db_user = await self.session.get(User, user_id)
        return db_user

    async def find_by_username(self, username: str) -> User | None:
        return await self.session.scalar(
            select(User).where(User.username == username)
        )

    async def find_by_email(self, email: str) -> User | None:
        return await self.session.scalar(
            select(User).where(User.email == email)
        )

    async def update(self, db_obj: User, update_data: dict) -> User:
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def replace(self, db_obj: User, replace_data: dict) -> User:
        for field, value in replace_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: User) -> User:
        await self.session.delete(db_obj)
        await self.session.commit()
        return db_obj
