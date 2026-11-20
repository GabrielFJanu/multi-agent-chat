from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from multi_agent_chat.core.security import get_current_user
from multi_agent_chat.models.user import User
from multi_agent_chat.schemas.common import PaginationParams
from multi_agent_chat.schemas.messages import (
    MessageCreate,
    MessageReplace,
    MessageResponse,
    MessageUpdate,
)
from multi_agent_chat.services.messages import MessageService

router = APIRouter(
    prefix='/conversations/{conversation_id}/messages', tags=['Messages']
)
Pagination = Annotated[PaginationParams, Query()]
Service = Annotated[MessageService, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


# authenticated owner
@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=MessageResponse,
)
async def create_message(
    conversation_id: int,
    message_in: MessageCreate,
    service: Service,
    current_user: CurrentUser,
):
    return await service.create_message(
        message_in, conversation_id, current_user.id
    )


# authenticated owner
@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=list[MessageResponse],
)
async def list_conversation_messages(
    conversation_id: int,
    pagination: Pagination,
    service: Service,
    current_user: CurrentUser,
):
    return await service.list_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
        skip=pagination.offset,
        limit=pagination.limit,
    )


# authenticated owner
@router.get(
    '/{message_id}',
    status_code=HTTPStatus.OK,
    response_model=MessageResponse,
)
async def get_message_by_id(
    conversation_id: int,
    message_id: int,
    service: Service,
    current_user: CurrentUser,
):
    return await service.get_message_by_id(
        message_id, conversation_id, current_user.id
    )


# authenticated owner
@router.patch(
    '/{message_id}',
    status_code=HTTPStatus.OK,
    response_model=MessageResponse,
)
async def update_message(
    conversation_id: int,
    message_id: int,
    message_in: MessageUpdate,
    service: Service,
    current_user: CurrentUser,
):
    return await service.update_message(
        message_id, message_in, conversation_id, current_user.id
    )


# authenticated owner
@router.put(
    '/{message_id}',
    status_code=HTTPStatus.OK,
    response_model=MessageResponse,
)
async def replace_message(
    conversation_id: int,
    message_id: int,
    message_in: MessageReplace,
    service: Service,
    current_user: CurrentUser,
):
    return await service.replace_message(
        message_id, message_in, conversation_id, current_user.id
    )


# authenticated owner
@router.delete(
    '/{message_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_message(
    conversation_id: int,
    message_id: int,
    service: Service,
    current_user: CurrentUser,
):
    await service.delete_message(message_id, conversation_id, current_user.id)
