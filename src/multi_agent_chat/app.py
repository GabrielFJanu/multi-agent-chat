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
    get_current_user,
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

    payload = {'sub': db_user.username}
    access_token = create_access_token(payload)
    return {'access_token': access_token, 'token_type': 'Bearer'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserRead)
def create_user(
    user_to_create: UserCreate,
    session: Session = Depends(get_session),
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
def read_user(
    user_id: int,
    session: Session = Depends(get_session),
):
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
    user_id: int,
    user_to_update: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
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


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserRead
)
def replace_user(
    user_id: int,
    user_to_replace: UserReplace,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
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


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    session.commit()
