from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from multi_agent_chat.database import get_session
from multi_agent_chat.models import User
from multi_agent_chat.schemas import (
    Token,
    UserCreate,
    UserList,
    UserRead,
    UserReplace,
    UserUpdate,
)
from multi_agent_chat.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.post('/login', status_code=HTTPStatus.OK, response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    db_user = session.scalar(
        select(User).where(User.username == form_data.username)
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    claims = {'sub': db_user.username}
    access_token = create_access_token(claims)
    return {'access_token': access_token, 'token_type': 'Bearer'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
    )
    session.add(db_user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )

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
        db_user.username = user.username
    if user.email:
        db_user.email = user.email
    if user.password:
        hashed_password = get_password_hash(user.password)
        db_user.password = hashed_password

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )

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

    db_user.username = user.username
    db_user.email = user.email
    hashed_password = get_password_hash(user.password)
    db_user.password = hashed_password

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )

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
