from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from multi_agent_chat.core.security import get_current_user
from multi_agent_chat.models.user import User
from multi_agent_chat.schemas.agents import AgentResponse
from multi_agent_chat.schemas.common import PaginationParams
from multi_agent_chat.schemas.conversations import (
    ConversationCreate,
    ConversationReplace,
    ConversationResponse,
    ConversationUpdate,
)
from multi_agent_chat.services.conversations import ConversationService

router = APIRouter(prefix='/conversations', tags=['Conversations'])
Pagination = Annotated[PaginationParams, Query()]
Service = Annotated[ConversationService, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


# authenticated users
@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=ConversationResponse,
)
async def create_conversation(
    conversation_in: ConversationCreate,
    service: Service,
    current_user: CurrentUser,
):
    return await service.create_conversation(conversation_in, current_user.id)


# authenticated owner
@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=list[ConversationResponse],
)
async def list_my_conversations(
    pagination: Pagination,
    service: Service,
    current_user: CurrentUser,
):
    return await service.list_conversations(
        user_id=current_user.id,
        skip=pagination.offset,
        limit=pagination.limit,
    )


# authenticated owner
@router.get(
    '/{conversation_id}',
    status_code=HTTPStatus.OK,
    response_model=ConversationResponse,
)
async def get_conversation_by_id(
    conversation_id: int,
    service: Service,
    current_user: CurrentUser,
):
    return await service.get_conversation_by_id(
        conversation_id, current_user.id
    )


# authenticated owner
@router.patch(
    '/{conversation_id}',
    status_code=HTTPStatus.OK,
    response_model=ConversationResponse,
)
async def update_conversation(
    conversation_id: int,
    conversation_in: ConversationUpdate,
    service: Service,
    current_user: CurrentUser,
):
    return await service.update_conversation(
        conversation_id, conversation_in, current_user.id
    )


# authenticated owner
@router.put(
    '/{conversation_id}',
    status_code=HTTPStatus.OK,
    response_model=ConversationResponse,
)
async def replace_conversation(
    conversation_id: int,
    conversation_in: ConversationReplace,
    service: Service,
    current_user: CurrentUser,
):
    return await service.replace_conversation(
        conversation_id, conversation_in, current_user.id
    )


# authenticated owner
@router.delete(
    '/{conversation_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_conversation(
    conversation_id: int,
    service: Service,
    current_user: CurrentUser,
):
    await service.delete_conversation(conversation_id, current_user.id)


# authenticated owner
@router.get(
    '/{conversation_id}/agents',
    status_code=HTTPStatus.OK,
    response_model=list[AgentResponse],
)
async def list_conversation_agents(
    conversation_id: int,
    pagination: Pagination,
    service: Service,
    current_user: CurrentUser,
):
    return await service.list_agents(
        conversation_id,
        current_user.id,
        skip=pagination.offset,
        limit=pagination.limit,
    )


# authenticated owner
@router.put(
    '/{conversation_id}/agents/{agent_id}',
    status_code=HTTPStatus.OK,
    response_model=AgentResponse,
)
async def add_conversation_agent(
    conversation_id: int,
    agent_id: int,
    service: Service,
    current_user: CurrentUser,
):
    return await service.add_agent(conversation_id, agent_id, current_user.id)


# authenticated owner
@router.delete(
    '/{conversation_id}/agents/{agent_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
async def remove_conversation_agent(
    conversation_id: int,
    agent_id: int,
    service: Service,
    current_user: CurrentUser,
):
    await service.remove_agent(conversation_id, agent_id, current_user.id)
