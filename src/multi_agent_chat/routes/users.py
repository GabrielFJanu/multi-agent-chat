from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from multi_agent_chat.models import User
from multi_agent_chat.schemas import (
    PaginationParams,
    UserCreate,
    UserReplace,
    UserResponse,
    UserUpdate,
)
from multi_agent_chat.security import get_current_user
from multi_agent_chat.services.users import UserService

router = APIRouter(prefix='/users', tags=['Users'])
Pagination = Annotated[PaginationParams, Query()]
Service = Annotated[UserService, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=UserResponse, status_code=HTTPStatus.CREATED)
def create_user(user_in: UserCreate, service: Service):
    return service.create_user(user_in)


@router.get('/', response_model=list[UserResponse])
def list_users(pagination: Pagination, service: Service):
    return service.list_users(
        skip=pagination.offset,
        limit=pagination.limit,
    )


@router.get('/{user_id}', response_model=UserResponse)
def get_user(user_id: int, service: Service):
    return service.get_user_by_id(user_id)


@router.patch('/{user_id}', response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    service: Service,
    current_user: CurrentUser,
):
    return service.update_user(user_id, user_in)


@router.put('/{user_id}', response_model=UserResponse)
def replace_user(
    user_id: int,
    user_in: UserReplace,
    service: Service,
    current_user: CurrentUser,
):
    return service.replace_user(user_id, user_in)


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int, service: Service, current_user: CurrentUser):
    service.delete_user(user_id)
