from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from multi_agent_chat.core.security import get_current_user
from multi_agent_chat.core.dependencies import RoleChecker
from multi_agent_chat.models.user import User, UserRole
from multi_agent_chat.schemas.common import PaginationParams
from multi_agent_chat.schemas.users import (
    UserAdminReplace,
    UserAdminUpdate,
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
CurrentAdmin = Annotated[User, Depends(RoleChecker([UserRole.ADMIN]))]


# anyone
@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserResponse,
)
async def register_user(user_in: UserCreate, service: Service):
    return await service.create_user(user_in)


# anyone
@router.get(
    '/me',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
async def get_my_profile(current_user: CurrentUser):
    return current_user


# anyone
@router.patch(
    '/me',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
async def update_my_profile(
    user_in: UserUpdate,
    service: Service,
    current_user: CurrentUser,
):
    return await service.update_user(current_user.id, user_in)


# anyone
@router.put(
    '/me',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
async def replace_my_profile(
    user_in: UserReplace,
    service: Service,
    current_user: CurrentUser,
):
    return await service.replace_user(current_user.id, user_in)


# anyone
@router.delete('/me', status_code=HTTPStatus.NO_CONTENT)
async def delete_my_account(
    service: Service,
    current_user: CurrentUser,
):
    await service.delete_user(current_user.id)


# only admin
@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=list[UserResponse],
)
async def list_all_users(
    pagination: Pagination,
    service: Service,
    current_admin: CurrentAdmin,
):
    return await service.list_users(
        skip=pagination.offset,
        limit=pagination.limit,
    )


# only admin
@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
async def get_user_by_id(
    user_id: int,
    service: Service,
    current_admin: CurrentAdmin,
):
    return await service.get_user_by_id(user_id)


# only admin
@router.patch(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
async def admin_update_user(
    user_id: int,
    user_in: UserAdminUpdate,
    service: Service,
    current_admin: CurrentAdmin,
):
    return await service.update_user(user_id, user_in)


# only admin
@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
async def admin_replace_user(
    user_id: int,
    user_in: UserAdminReplace,
    service: Service,
    current_admin: CurrentAdmin,
):
    return await service.replace_user(user_id, user_in)


# only admin
@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
async def admin_delete_user(
    user_id: int,
    service: Service,
    current_admin: CurrentAdmin,
):
    await service.delete_user(user_id)
