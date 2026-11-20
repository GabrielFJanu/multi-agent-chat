from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from multi_agent_chat.models.agent import Agent
from multi_agent_chat.repositories.agents import AgentRepository
from multi_agent_chat.schemas.agents import (
    AgentCreate,
    AgentReplace,
    AgentUpdate,
)

Repository = Annotated[AgentRepository, Depends()]


class AgentService:
    def __init__(
        self,
        repository: Repository,
    ):
        self.repository = repository

    async def _get_agent_by_id_or_404(self, agent_id: int) -> Agent:
        db_agent = await self.repository.get_by_id(agent_id)

        if not db_agent:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Agent not found',
            )

        return db_agent

    async def create_agent(self, agent_in: AgentCreate) -> Agent:
        create_data = agent_in.model_dump()

        db_agent = await self.repository.create(create_data)
        return db_agent

    async def list_agents(
        self, skip: int = 0, limit: int = 100
    ) -> list[Agent]:
        db_agents = await self.repository.list(skip=skip, limit=limit)
        return db_agents

    async def get_agent_by_id(self, agent_id: int) -> Agent:
        db_agent = await self._get_agent_by_id_or_404(agent_id)
        return db_agent

    async def update_agent(
        self,
        agent_id: int,
        agent_in: AgentUpdate,
    ) -> Agent:
        db_agent = await self._get_agent_by_id_or_404(agent_id)

        update_data = agent_in.model_dump(exclude_unset=True)

        db_agent = await self.repository.update(db_agent, update_data)
        return db_agent

    async def replace_agent(
        self,
        agent_id: int,
        agent_in: AgentReplace,
    ) -> Agent:
        db_agent = await self._get_agent_by_id_or_404(agent_id)

        replace_data = agent_in.model_dump()

        db_agent = await self.repository.replace(db_agent, replace_data)
        return db_agent

    async def delete_agent(self, agent_id: int) -> None:
        db_agent = await self._get_agent_by_id_or_404(agent_id)
        try:
            await self.repository.delete(db_agent)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Cannot delete an agent with messages',
            ) from exc
