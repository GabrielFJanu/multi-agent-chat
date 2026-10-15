from http import HTTPStatus
from fastapi import Depends, HTTPException
from multi_agent_chat.repositories.users import UserRepository
from multi_agent_chat.models import User
from multi_agent_chat.schemas import UserCreate, UserUpdate, UserReplace
from multi_agent_chat.security import get_password_hash

class UserService:
    def __init__(
        self,
        repository: UserRepository = Depends(),
    ):
        self.repository = repository

    def _get_user_by_id_or_404(self, user_id: int) -> User:
        db_user = self.repository.get_by_id(user_id)
        
        if not db_user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='User not found',
            )

        return db_user
    
    def create_user(self, user_in: UserCreate) -> User:
        existing_user = self.repository.find_by_username(user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )

        existing_user = self.repository.find_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )
        
        create_data = user_in.model_dump()

        create_data["password"] = get_password_hash(create_data["password"])
        
        db_user = self.repository.create(create_data)
        return db_user

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        db_users = self.repository.list(skip=skip, limit=limit)
        return db_users

    def get_user_by_id(self, user_id: int) -> User:
        db_user = self._get_user_by_id_or_404(user_id)
        return db_user

    def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        db_user = self._get_user_by_id_or_404(user_id)

        if user_in.username:
            existing_user = self.repository.find_by_username(user_in.username)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='Username already exists',
                )
            
        if user_in.email:
            existing_user = self.repository.find_by_email(user_in.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail='Email already exists',
                )

        update_data = user_in.model_dump(exclude_unset=True)

        if 'password' in update_data:
            update_data["password"] = get_password_hash(update_data["password"])
            
        db_user = self.repository.update(db_user, update_data)
        return db_user

    def replace_user(self, user_id: int, user_in: UserReplace) -> User:
        db_user = self._get_user_by_id_or_404(user_id)

        existing_user = self.repository.find_by_username(user_in.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
            
        existing_user = self.repository.find_by_email(user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

        replace_data = user_in.model_dump()

        replace_data["password"] = get_password_hash(replace_data["password"])
        
        db_user = self.repository.replace(db_user, replace_data)
        return db_user

    def delete_user(self, user_id: int) -> None:
        db_user = self._get_user_by_id_or_404(user_id)
        self.repository.delete(db_user)