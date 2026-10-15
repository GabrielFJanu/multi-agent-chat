from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from multi_agent_chat.database import get_session
from multi_agent_chat.models import User

class UserRepository:
    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def create(self, create_data: dict) -> User:
        db_user = User(**create_data)
        
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        db_users = self.session.scalars(
            select(User)
            .offset(skip)
            .limit(limit)
        ).all()
        return db_users

    def get_by_id(self, user_id: int) -> User | None:
        db_user = self.session.get(User, user_id)
        return db_user

    def find_by_username(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.username == username)
        )

    def find_by_email(self, email: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.email == email)
        )

    def update(self, db_obj: User, update_data: dict) -> User:
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def replace(self, db_obj: User, replace_data: dict) -> User:
        for field, value in replace_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: User) -> User:
        self.session.delete(db_obj)
        self.session.commit()
        return db_obj