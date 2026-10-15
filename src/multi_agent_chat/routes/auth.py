from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from multi_agent_chat.database import get_session
from multi_agent_chat.models import User
from multi_agent_chat.schemas import Token
from multi_agent_chat.security import (
    create_access_token,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])
OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[Session, Depends(get_session)]


@router.post(
    '/login',
    status_code=HTTPStatus.OK,
    response_model=Token,
)
def login(
    form_data: OAuthForm,
    session: Session,
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
