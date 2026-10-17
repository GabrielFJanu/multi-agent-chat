from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException

from multi_agent_chat.core.security import (
    create_access_token,
    verify_password,
)
from multi_agent_chat.models.user import User
from multi_agent_chat.repositories.users import UserRepository

Repository = Annotated[UserRepository, Depends()]


class AuthService:
    def __init__(
        self,
        repository: Repository,
    ):
        self.repository = repository

    async def authenticate_user(self, username: str, password: str) -> dict:
        db_user = await self.repository.find_by_username(username)

        if not db_user or not verify_password(password, db_user.password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Incorrect username or password',
            )

        payload = {'sub': db_user.username}
        access_token = create_access_token(payload)

        return {'access_token': access_token, 'token_type': 'Bearer'}

    @staticmethod
    async def refresh_token(user: User) -> dict:

        payload = {'sub': user.username}
        new_access_token = create_access_token(payload)

        return {'access_token': new_access_token, 'token_type': 'Bearer'}
