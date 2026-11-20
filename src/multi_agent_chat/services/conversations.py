from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException

from multi_agent_chat.models.agent import Agent
from multi_agent_chat.models.conversation import Conversation
from multi_agent_chat.repositories.agents import AgentRepository
from multi_agent_chat.repositories.conversations import (
    ConversationRepository,
)
from multi_agent_chat.schemas.conversations import (
    ConversationCreate,
    ConversationReplace,
    ConversationUpdate,
)

Repository = Annotated[ConversationRepository, Depends()]
AgentRepositoryDependency = Annotated[AgentRepository, Depends()]


class ConversationService:
    def __init__(
        self,
        repository: Repository,
        agent_repository: AgentRepositoryDependency,
    ):
        self.repository = repository
        self.agent_repository = agent_repository

    async def _get_conversation_by_id_or_404(
        self, conversation_id: int, user_id: int
    ) -> Conversation:
        db_conversation = await self.repository.get_by_id(
            conversation_id, user_id
        )

        if not db_conversation:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Conversation not found',
            )

        return db_conversation

    async def create_conversation(
        self, conversation_in: ConversationCreate, user_id: int
    ) -> Conversation:
        create_data = conversation_in.model_dump()
        create_data['user_id'] = user_id

        db_conversation = await self.repository.create(create_data)
        return db_conversation

    async def list_conversations(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Conversation]:
        db_conversations = await self.repository.list(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
        return db_conversations

    async def get_conversation_by_id(
        self, conversation_id: int, user_id: int
    ) -> Conversation:
        db_conversation = await self._get_conversation_by_id_or_404(
            conversation_id, user_id
        )
        return db_conversation

    async def update_conversation(
        self,
        conversation_id: int,
        conversation_in: ConversationUpdate,
        user_id: int,
    ) -> Conversation:
        db_conversation = await self._get_conversation_by_id_or_404(
            conversation_id, user_id
        )

        update_data = conversation_in.model_dump(exclude_unset=True)

        db_conversation = await self.repository.update(
            db_conversation, update_data
        )
        return db_conversation

    async def replace_conversation(
        self,
        conversation_id: int,
        conversation_in: ConversationReplace,
        user_id: int,
    ) -> Conversation:
        db_conversation = await self._get_conversation_by_id_or_404(
            conversation_id, user_id
        )

        replace_data = conversation_in.model_dump()

        db_conversation = await self.repository.replace(
            db_conversation, replace_data
        )
        return db_conversation

    async def delete_conversation(
        self, conversation_id: int, user_id: int
    ) -> None:
        db_conversation = await self._get_conversation_by_id_or_404(
            conversation_id, user_id
        )
        await self.repository.delete(db_conversation)

    async def add_agent(
        self, conversation_id: int, agent_id: int, user_id: int
    ) -> Agent:
        db_conversation = await self._get_conversation_by_id_or_404(
            conversation_id, user_id
        )
        db_agent = await self.agent_repository.get_by_id(agent_id)

        if not db_agent:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Agent not found',
            )

        await self.repository.add_agent(db_conversation, db_agent)
        return db_agent

    async def list_agents(
        self,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Agent]:
        await self._get_conversation_by_id_or_404(conversation_id, user_id)

        db_agents = await self.repository.list_agents(
            conversation_id, skip=skip, limit=limit
        )
        return db_agents

    async def remove_agent(
        self, conversation_id: int, agent_id: int, user_id: int
    ) -> None:
        db_conversation = await self._get_conversation_by_id_or_404(
            conversation_id, user_id
        )
        removed = await self.repository.remove_agent(db_conversation, agent_id)

        if not removed:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Agent not found in conversation',
            )
