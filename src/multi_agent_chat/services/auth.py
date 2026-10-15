from http import HTTPStatus
from fastapi import Depends, HTTPException
from multi_agent_chat.repositories.users import UserRepository
from multi_agent_chat.security import verify_password, create_access_token

class AuthService:
    def __init__(
        self,
        repository: UserRepository = Depends(),
    ):
        self.repository = repository

    def login(self, username: str, password: str) -> dict:
        db_user = self.repository.find_by_username(username)

        if not db_user or not verify_password(password, db_user.password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Incorrect username or password',
            )
    
        payload = {'sub': db_user.username}
        access_token = create_access_token(payload)
        
        return {
            'access_token': access_token, 
            'token_type': 'bearer'
        }