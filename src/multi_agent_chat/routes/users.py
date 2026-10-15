from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from multi_agent_chat.database import get_session
from multi_agent_chat.models import User
from multi_agent_chat.schemas import (
    PaginationParams,
    UserCreate,
    UserList,
    UserRead,
    UserReplace,
    UserUpdate,
)
from multi_agent_chat.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
PaginationParams = Annotated[PaginationParams, Query()]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserRead,
)
def create_user(
    user_to_create: UserCreate,
    session: Session,
):
    hashed_password = get_password_hash(user_to_create.password)
    db_user = User(
        username=user_to_create.username,
        email=user_to_create.email,
        password=hashed_password,
    )
    session.add(db_user)

    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )

    session.refresh(db_user)

    return db_user


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=UserList,
)
def read_users(session: Session, pagination: PaginationParams):
    db_users = session.scalars(
        select(User).offset(pagination.offset).limit(pagination.limit)
    ).all()
    return {'users': db_users}


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
)
def read_user(
    user_id: int,
    session: Session,
):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user


@router.patch(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
)
def update_user(
    user_id: int,
    user_to_update: UserUpdate,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    if user_to_update.username:
        current_user.username = user_to_update.username
    if user_to_update.email:
        current_user.email = user_to_update.email
    if user_to_update.password:
        hashed_password = get_password_hash(user_to_update.password)
        current_user.password = hashed_password

    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )

    session.refresh(current_user)

    return current_user


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
)
def replace_user(
    user_id: int,
    user_to_replace: UserReplace,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    current_user.username = user_to_replace.username
    current_user.email = user_to_replace.email
    hashed_password = get_password_hash(user_to_replace.password)
    current_user.password = hashed_password

    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )

    session.refresh(current_user)

    return current_user


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    session.commit()
