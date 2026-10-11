from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from multi_agent_chat.database import get_session
from multi_agent_chat.models import User
from multi_agent_chat.schemas import (
    UserCreate,
    UserList,
    UserRead,
    UserReplace,
    UserUpdate,
)

app = FastAPI()


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    conflict_user = session.scalar(
        select(User).where(User.username == user.username)
    )
    if conflict_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username already exists',
        )

    conflict_user = session.scalar(
        select(User).where(User.email == user.email)
    )
    if conflict_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )

    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    db_users = session.scalars(select(User).offset(offset).limit(limit)).all()
    return {'users': db_users}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserRead
)
def read_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user


@app.patch(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserRead,
)
def update_user(
    user_id: int, user: UserUpdate, session: Session = Depends(get_session)
):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    if user.username:
        conflict_user = session.scalar(
            select(User).where(
                (User.id != user_id) & (User.username == user.username)
            )
        )
        if conflict_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )

    if user.email:
        conflict_user = session.scalar(
            select(User).where(
                (User.id != user_id) & (User.email == user.email)
            )
        )
        if conflict_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    if user.username:
        db_user.username = user.username
    if user.email:
        db_user.email = user.email
    if user.password:
        db_user.password = user.password
    session.commit()
    session.refresh(db_user)

    return db_user


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserRead
)
def replace_user(
    user_id: int, user: UserReplace, session: Session = Depends(get_session)
):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    conflict_user = session.scalar(
        select(User).where(
            (User.id != user_id) & (User.username == user.username)
        )
    )
    if conflict_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username already exists',
        )

    conflict_user = session.scalar(
        select(User).where((User.id != user_id) & (User.email == user.email))
    )
    if conflict_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )

    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password
    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.delete(db_user)
    session.commit()
