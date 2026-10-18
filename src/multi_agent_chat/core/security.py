from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash

from multi_agent_chat.core.settings import Settings
from multi_agent_chat.repositories.users import UserRepository

pwd_context = PasswordHash.recommended()
settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
Repository = Annotated[UserRepository, Depends()]
AccessToken = Annotated[str, Depends(oauth2_scheme)]


def create_access_token(payload: dict):
    payload_to_encode = payload.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload_to_encode.update({'exp': expire})

    access_token = encode(
        payload_to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return access_token


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    repository: Repository,
    access_token: AccessToken,
):
    try:
        decoded_payload = decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=settings.ALGORITHM,
        )
        subject_username = decoded_payload.get('sub')

        if not subject_username:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    except DecodeError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    db_user = await repository.find_by_username(subject_username)

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return db_user
