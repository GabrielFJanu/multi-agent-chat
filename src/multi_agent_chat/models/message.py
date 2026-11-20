from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Text, func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    relationship,
)

from multi_agent_chat.models.base import table_registry

if TYPE_CHECKING:
    from multi_agent_chat.models.agent import Agent
    from multi_agent_chat.models.conversation import Conversation
    from multi_agent_chat.models.user import User


@mapped_as_dataclass(table_registry)
class Message:
    __tablename__ = 'messages'
    __table_args__ = (
        CheckConstraint(
            '(user_id IS NOT NULL AND agent_id IS NULL) OR '
            '(user_id IS NULL AND agent_id IS NOT NULL)',
            name='ck_messages_exactly_one_author',
        ),
    )

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey('conversations.id', ondelete='CASCADE'), index=True
    )
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), default=None
    )
    agent_id: Mapped[int | None] = mapped_column(
        ForeignKey('agents.id'), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    conversation: Mapped['Conversation'] = relationship(
        back_populates='messages',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )

    user: Mapped['User | None'] = relationship(
        back_populates='messages',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )

    agent: Mapped['Agent | None'] = relationship(
        back_populates='messages',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )
