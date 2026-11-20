from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    relationship,
)

from multi_agent_chat.models.base import table_registry
from multi_agent_chat.models.conversation_agent import conversation_agents

if TYPE_CHECKING:
    from multi_agent_chat.models.agent import Agent
    from multi_agent_chat.models.message import Message
    from multi_agent_chat.models.user import User


@mapped_as_dataclass(table_registry)
class Conversation:
    __tablename__ = 'conversations'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    title: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    agents: Mapped[list['Agent']] = relationship(
        secondary=conversation_agents,
        back_populates='conversations',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )

    messages: Mapped[list['Message']] = relationship(
        back_populates='conversation',
        cascade='all, delete-orphan',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )

    user: Mapped['User'] = relationship(
        back_populates='conversations',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )
