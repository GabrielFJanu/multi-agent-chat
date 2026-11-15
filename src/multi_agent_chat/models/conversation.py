from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column

from multi_agent_chat.models.base import table_registry


@mapped_as_dataclass(table_registry)
class Conversation:
    __tablename__ = 'conversations'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    title: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
