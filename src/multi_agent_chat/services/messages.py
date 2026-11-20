from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException

from multi_agent_chat.models.message import Message
from multi_agent_chat.repositories.messages import (
    MessageRepository,
)
from multi_agent_chat.schemas.messages import (
    MessageCreate,
    MessageReplace,
    MessageUpdate,
)
from multi_agent_chat.services.conversations import ConversationService

Repository = Annotated[MessageRepository, Depends()]
ConversationServiceDependency = Annotated[ConversationService, Depends()]


class MessageService:
    def __init__(
        self,
        repository: Repository,
        conversation_service: ConversationServiceDependency,
    ):
        self.repository = repository
        self.conversation_service = conversation_service

    async def _get_message_by_id_or_404(
        self, message_id: int, conversation_id: int, user_id: int
    ) -> Message:
        await self.conversation_service.get_conversation_by_id(
            conversation_id, user_id
        )
        db_message = await self.repository.get_by_id(
            message_id, conversation_id
        )

        if not db_message:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Message not found',
            )

        return db_message

    async def create_message(
        self, message_in: MessageCreate, conversation_id: int, user_id: int
    ) -> Message:
        await self.conversation_service.get_conversation_by_id(
            conversation_id, user_id
        )
        create_data = message_in.model_dump()
        create_data['conversation_id'] = conversation_id
        create_data['user_id'] = user_id

        db_message = await self.repository.create(create_data)
        return db_message

    async def list_messages(
        self,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        await self.conversation_service.get_conversation_by_id(
            conversation_id, user_id
        )
        db_messages = await self.repository.list(
            conversation_id=conversation_id,
            skip=skip,
            limit=limit,
        )
        return db_messages

    async def get_message_by_id(
        self, message_id: int, conversation_id: int, user_id: int
    ) -> Message:
        db_message = await self._get_message_by_id_or_404(
            message_id, conversation_id, user_id
        )
        return db_message

    async def update_message(
        self,
        message_id: int,
        message_in: MessageUpdate,
        conversation_id: int,
        user_id: int,
    ) -> Message:
        db_message = await self._get_message_by_id_or_404(
            message_id, conversation_id, user_id
        )

        update_data = message_in.model_dump(exclude_unset=True)

        db_message = await self.repository.update(db_message, update_data)
        return db_message

    async def replace_message(
        self,
        message_id: int,
        message_in: MessageReplace,
        conversation_id: int,
        user_id: int,
    ) -> Message:
        db_message = await self._get_message_by_id_or_404(
            message_id, conversation_id, user_id
        )

        replace_data = message_in.model_dump()

        db_message = await self.repository.replace(db_message, replace_data)
        return db_message

    async def delete_message(
        self, message_id: int, conversation_id: int, user_id: int
    ) -> None:
        db_message = await self._get_message_by_id_or_404(
            message_id, conversation_id, user_id
        )
        await self.repository.delete(db_message)
