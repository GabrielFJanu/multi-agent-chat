from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_chat.core.database import get_session
from multi_agent_chat.models.agent import Agent

Session = Annotated[AsyncSession, Depends(get_session)]


class AgentRepository:
    def __init__(self, session: Session):
        self.session = session

    async def create(self, create_data: dict) -> Agent:
        db_agent = Agent(**create_data)

        self.session.add(db_agent)
        await self.session.commit()
        await self.session.refresh(db_agent)
        return db_agent

    async def list(self, skip: int = 0, limit: int = 100) -> list[Agent]:
        result = await self.session.scalars(
            select(Agent).order_by(Agent.id).offset(skip).limit(limit)
        )
        db_agents = result.all()
        return db_agents

    async def get_by_id(self, agent_id: int) -> Agent | None:
        db_agent = await self.session.get(Agent, agent_id)
        return db_agent

    async def update(self, db_obj: Agent, update_data: dict) -> Agent:
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def replace(self, db_obj: Agent, replace_data: dict) -> Agent:
        for field, value in replace_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Agent) -> None:
        try:
            await self.session.delete(db_obj)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
