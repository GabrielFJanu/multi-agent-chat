from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_chat.core.database import get_session
from multi_agent_chat.models.message import Message

Session = Annotated[AsyncSession, Depends(get_session)]


class MessageRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_data: dict) -> Message:
        db_message = Message(**create_data)

        self.session.add(db_message)
        await self.session.commit()
        await self.session.refresh(db_message)
        return db_message

    async def list(
        self, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> list[Message]:
        result = await self.session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.id)
            .offset(skip)
            .limit(limit)
        )
        db_messages = result.all()
        return db_messages

    async def get_by_id(
        self, message_id: int, conversation_id: int
    ) -> Message | None:
        db_message = await self.session.scalar(
            select(Message).where(
                Message.id == message_id,
                Message.conversation_id == conversation_id,
            )
        )
        return db_message

    async def update(self, db_obj: Message, update_data: dict) -> Message:
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def replace(self, db_obj: Message, replace_data: dict) -> Message:
        for field, value in replace_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Message) -> None:
        await self.session.delete(db_obj)
        await self.session.commit()
