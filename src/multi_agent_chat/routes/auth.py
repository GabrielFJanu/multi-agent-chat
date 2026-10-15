from http import HTTPStatus
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from multi_agent_chat.schemas import Token
from multi_agent_chat.services.auth import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
    '/login',
    status_code=HTTPStatus.OK,
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(),
):
    return service.login(
        username=form_data.username,
        password=form_data.password,
    )
