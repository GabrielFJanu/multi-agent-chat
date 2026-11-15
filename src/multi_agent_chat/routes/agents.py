from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from multi_agent_chat.core.dependencies import RoleChecker
from multi_agent_chat.core.security import get_current_user
from multi_agent_chat.models.user import User, UserRole
from multi_agent_chat.schemas.agents import (
    AgentCreate,
    AgentReplace,
    AgentResponse,
    AgentUpdate,
)
from multi_agent_chat.schemas.common import PaginationParams
from multi_agent_chat.services.agents import AgentService

router = APIRouter(prefix='/agents', tags=['Agents'])
Pagination = Annotated[PaginationParams, Query()]
Service = Annotated[AgentService, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(RoleChecker([UserRole.ADMIN]))]


# only admin
@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=AgentResponse,
)
async def create_agent(
    agent_in: AgentCreate,
    service: Service,
    current_admin: CurrentAdmin,
):
    return await service.create_agent(agent_in)


# authenticated users
@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=list[AgentResponse],
)
async def list_all_agents(
    pagination: Pagination,
    service: Service,
    current_user: CurrentUser,
):
    return await service.list_agents(
        skip=pagination.offset,
        limit=pagination.limit,
    )


# authenticated users
@router.get(
    '/{agent_id}',
    status_code=HTTPStatus.OK,
    response_model=AgentResponse,
)
async def get_agent_by_id(
    agent_id: int,
    service: Service,
    current_user: CurrentUser,
):
    return await service.get_agent_by_id(agent_id)


# only admin
@router.patch(
    '/{agent_id}',
    status_code=HTTPStatus.OK,
    response_model=AgentResponse,
)
async def update_agent(
    agent_id: int,
    agent_in: AgentUpdate,
    service: Service,
    current_admin: CurrentAdmin,
):
    return await service.update_agent(agent_id, agent_in)


# only admin
@router.put(
    '/{agent_id}',
    status_code=HTTPStatus.OK,
    response_model=AgentResponse,
)
async def replace_agent(
    agent_id: int,
    agent_in: AgentReplace,
    service: Service,
    current_admin: CurrentAdmin,
):
    return await service.replace_agent(agent_id, agent_in)


# only admin
@router.delete(
    '/{agent_id}',
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_agent(
    agent_id: int,
    service: Service,
    current_admin: CurrentAdmin,
):
    await service.delete_agent(agent_id)
