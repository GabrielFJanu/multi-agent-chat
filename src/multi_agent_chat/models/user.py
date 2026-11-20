import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    relationship,
)

from multi_agent_chat.models.base import table_registry

if TYPE_CHECKING:
    from multi_agent_chat.models.conversation import Conversation
    from multi_agent_chat.models.message import Message


class UserRole(str, enum.Enum):
    ADMIN = 'admin'
    USER = 'user'


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    conversations: Mapped[list['Conversation']] = relationship(
        back_populates='user',
        cascade='all, delete',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )

    messages: Mapped[list['Message']] = relationship(
        back_populates='user',
        cascade='all, delete',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )
