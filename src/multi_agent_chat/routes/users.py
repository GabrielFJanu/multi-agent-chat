from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from multi_agent_chat.schemas import (
    PaginationParams,
    UserCreate,
    UserUpdate,
    UserReplace,
    UserResponse,
    UserList,
)
from multi_agent_chat.services.users import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", 
    response_model=UserResponse, 
    status_code=HTTPStatus.CREATED
)
def create_user(
    user_in: UserCreate, 
    service: UserService = Depends()
):
    return service.create_user(user_in)


@router.get(
    "/", 
    response_model=UserList
)
def list_users(
    pagination: PaginationParams = Query(),
    service: UserService = Depends()
):
    return service.list_users(
        skip=pagination.offset,
        limit=pagination.limit,
    )


@router.get(
    "/{user_id}", 
    response_model=UserResponse
)
def get_user(
    user_id: int, 
    service: UserService = Depends()
):
    return service.get_user_by_id(user_id)


@router.patch(
    "/{user_id}", 
    response_model=UserResponse
)
def update_user(
    user_id: int, 
    user_in: UserUpdate, 
    service: UserService = Depends()
):
    return service.update_user(user_id, user_in)


@router.put(
    "/{user_id}", 
    response_model=UserResponse
)
def replace_user(
    user_id: int, 
    user_in: UserReplace, 
    service: UserService = Depends()
):
    return service.replace_user(user_id, user_in)


@router.delete(
    "/{user_id}", 
    status_code=HTTPStatus.NO_CONTENT
)
def delete_user(
    user_id: int, 
    service: UserService = Depends()
):
    service.delete_user(user_id)
    return None