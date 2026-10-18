from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException

from multi_agent_chat.core.security import get_current_user
from multi_agent_chat.models.user import User, UserRole


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Not enough permissions',
            )
        return current_user
