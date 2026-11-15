from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException

from multi_agent_chat.models.conversation import Conversation
from multi_agent_chat.repositories.conversations import (
    ConversationRepository,
)
from multi_agent_chat.schemas.conversations import (
    ConversationCreate,
    ConversationReplace,
    ConversationUpdate,
)

Repository = Annotated[ConversationRepository, Depends()]


class ConversationService:
    def __init__(
        self,
        repository: Repository,
    ):
        self.repository = repository

    async def _get_conversation_by_id_or_404(
        self, conversation_id: int, user_id: int
    ) -> Conversation:
        db_conversation = await self.repository.get_by_id(
            conversation_id,
            user_id,
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
