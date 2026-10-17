from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from multi_agent_chat.core.security import get_current_user
from multi_agent_chat.models.user import User
from multi_agent_chat.schemas.auth import Token
from multi_agent_chat.services.auth import AuthService

router = APIRouter(prefix='/auth', tags=['Auth'])
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Service = Annotated[AuthService, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/token',
    status_code=HTTPStatus.OK,
    response_model=Token,
)
async def login_for_access_token(
    form_data: OAuth2Form,
    service: Service,
):
    return await service.authenticate_user(
        username=form_data.username,
        password=form_data.password,
    )


@router.post(
    '/refresh_token',
    status_code=HTTPStatus.OK,
    response_model=Token,
)
async def refresh_access_token(
    current_user: CurrentUser,
    service: Service,
):
    return await service.refresh_token(current_user)
