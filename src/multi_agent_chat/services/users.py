from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException

from multi_agent_chat.core.security import get_password_hash
from multi_agent_chat.models.user import User, UserRole
from multi_agent_chat.repositories.users import UserRepository
from multi_agent_chat.schemas.users import (
    UserAdminReplace,
    UserAdminUpdate,
    UserCreate,
    UserReplace,
    UserUpdate,
)

Repository = Annotated[UserRepository, Depends()]


class UserService:
    def __init__(
        self,
        repository: Repository,
    ):
        self.repository = repository

    async def _get_user_by_id_or_404(self, user_id: int) -> User:
        db_user = await self.repository.get_by_id(user_id)

        if not db_user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='User not found',
            )

        return db_user

    async def create_user(self, user_in: UserCreate) -> User:
        existing_user = await self.repository.find_by_username(
            user_in.username
        )
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )

        existing_user = await self.repository.find_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

        create_data = user_in.model_dump()

        create_data['password'] = get_password_hash(create_data['password'])
        create_data['role'] = UserRole.USER

        db_user = await self.repository.create(create_data)
        return db_user

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        db_users = await self.repository.list(skip=skip, limit=limit)
        return db_users

    async def get_user_by_id(self, user_id: int) -> User:
        db_user = await self._get_user_by_id_or_404(user_id)
        return db_user

    async def update_user(
        self,
        user_id: int,
        user_in: UserUpdate | UserAdminUpdate,
    ) -> User:
        db_user = await self._get_user_by_id_or_404(user_id)

        if user_in.username:
            existing_user = await self.repository.find_by_username(
                user_in.username
            )
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='Username already exists',
                )

        if user_in.email:
            existing_user = await self.repository.find_by_email(user_in.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='Email already exists',
                )

        update_data = user_in.model_dump(exclude_unset=True)

        if 'password' in update_data:
            update_data['password'] = get_password_hash(
                update_data['password']
            )

        db_user = await self.repository.update(db_user, update_data)
        return db_user

    async def replace_user(
        self,
        user_id: int,
        user_in: UserReplace | UserAdminReplace,
    ) -> User:
        db_user = await self._get_user_by_id_or_404(user_id)

        existing_user = await self.repository.find_by_username(
            user_in.username
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )

        existing_user = await self.repository.find_by_email(user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

        replace_data = user_in.model_dump()

        replace_data['password'] = get_password_hash(replace_data['password'])

        db_user = await self.repository.replace(db_user, replace_data)
        return db_user

    async def delete_user(self, user_id: int) -> None:
        db_user = await self._get_user_by_id_or_404(user_id)
        await self.repository.delete(db_user)
