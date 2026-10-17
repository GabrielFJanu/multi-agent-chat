from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from multi_agent_chat.core.security import get_current_user
from multi_agent_chat.models.user import User
from multi_agent_chat.schemas.common import PaginationParams
from multi_agent_chat.schemas.users import (
    UserCreate,
    UserReplace,
    UserResponse,
    UserUpdate,
)
from multi_agent_chat.services.users import UserService

router = APIRouter(prefix='/users', tags=['Users'])
Pagination = Annotated[PaginationParams, Query()]
Service = Annotated[UserService, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=UserResponse, status_code=HTTPStatus.CREATED)
async def create_user(user_in: UserCreate, service: Service):
    return await service.create_user(user_in)


@router.get('/', response_model=list[UserResponse])
async def list_users(pagination: Pagination, service: Service):
    return await service.list_users(
        skip=pagination.offset,
        limit=pagination.limit,
    )


@router.get('/{user_id}', response_model=UserResponse)
async def get_user(user_id: int, service: Service):
    return await service.get_user_by_id(user_id)


@router.patch('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    service: Service,
    current_user: CurrentUser,
):
    return await service.update_user(user_id, user_in)


@router.put('/{user_id}', response_model=UserResponse)
async def replace_user(
    user_id: int,
    user_in: UserReplace,
    service: Service,
    current_user: CurrentUser,
):
    return await service.replace_user(user_id, user_in)


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int, service: Service, current_user: CurrentUser
):
    await service.delete_user(user_id)
