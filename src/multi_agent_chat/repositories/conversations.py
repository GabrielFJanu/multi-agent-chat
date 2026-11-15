from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_chat.core.database import get_session
from multi_agent_chat.models.agent import Agent
from multi_agent_chat.models.conversation import Conversation

Session = Annotated[AsyncSession, Depends(get_session)]


class ConversationRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_data: dict) -> Conversation:
        db_conversation = Conversation(**create_data)

        self.session.add(db_conversation)
        await self.session.commit()
        await self.session.refresh(db_conversation)
        return db_conversation

    async def list(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Conversation]:
        result = await self.session.scalars(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.id)
            .offset(skip)
            .limit(limit)
        )
        db_conversations = result.all()
        return db_conversations

    async def get_by_id(
        self, conversation_id: int, user_id: int
    ) -> Conversation | None:
        db_conversation = await self.session.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        return db_conversation

    async def update(
        self, db_obj: Conversation, update_data: dict
    ) -> Conversation:
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def replace(
        self, db_obj: Conversation, replace_data: dict
    ) -> Conversation:
        for field, value in replace_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Conversation) -> None:
        await self.session.delete(db_obj)
        await self.session.commit()

    async def add_agent(
        self, conversation: Conversation, agent: Agent
    ) -> None:
        await self.session.refresh(conversation, ['agents'])
        if agent in conversation.agents:
            return
        conversation_id, agent_id = conversation.id, agent.id
        conversation.agents.append(agent)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            existing = await self.session.scalar(
                select(Agent)
                .join(Agent.conversations)
                .where(
                    Conversation.id == conversation_id, Agent.id == agent_id
                )
            )
            if existing is None:
                raise
            await self.session.refresh(agent)

    async def list_agents(
        self, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> list[Agent]:
        result = await self.session.scalars(
            select(Agent)
            .join(Agent.conversations)
            .where(Conversation.id == conversation_id)
            .order_by(Agent.id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())

    async def remove_agent(
        self, conversation: Conversation, agent_id: int
    ) -> bool:
        await self.session.refresh(conversation, ['agents'])
        agent = next(
            (agent for agent in conversation.agents if agent.id == agent_id),
            None,
        )
        if agent is None:
            return False
        conversation.agents.remove(agent)
        await self.session.commit()
        return True
