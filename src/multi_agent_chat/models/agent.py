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
from multi_agent_chat.models.conversation_agent import conversation_agents

if TYPE_CHECKING:
    from multi_agent_chat.models.conversation import Conversation
    from multi_agent_chat.models.message import Message


@mapped_as_dataclass(table_registry)
class Agent:
    __tablename__ = 'agents'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    model: Mapped[str]
    system_prompt: Mapped[str]
    temperature: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    conversations: Mapped[list['Conversation']] = relationship(
        secondary=conversation_agents,
        back_populates='agents',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )

    messages: Mapped[list['Message']] = relationship(
        back_populates='agent',
        lazy='raise',
        init=False,
        repr=False,
        compare=False,
    )
