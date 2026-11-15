from http import HTTPStatus

import pytest
from sqlalchemy import func, select

from multi_agent_chat.models import (
    Agent,
    Conversation,
    User,
    UserRole,
    conversation_agents,
)


@pytest.mark.asyncio
async def test_many_to_many_and_duplicate_membership(
    client, session, conversation, agent, token
):
    second_agent = Agent(
        name='second',
        description='Second agent',
        model='test',
        system_prompt='Help.',
        temperature=0.5,
    )
    second_conversation = Conversation(
        user_id=conversation.user_id, title='Second conversation'
    )
    session.add_all([second_agent, second_conversation])
    await session.commit()
    headers = {'Authorization': f'Bearer {token}'}
    for conversation_id, agent_id in [
        (conversation.id, agent.id),
        (conversation.id, second_agent.id),
        (second_conversation.id, agent.id),
        (conversation.id, agent.id),
    ]:
        response = client.put(
            f'/conversations/{conversation_id}/agents/{agent_id}',
            headers=headers,
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()['id'] == agent_id

    count = await session.scalar(
        select(func.count()).select_from(conversation_agents)
    )
    expected_links = 3
    assert count == expected_links
    response = client.get(
        f'/conversations/{conversation.id}/agents', headers=headers
    )
    assert [item['id'] for item in response.json()] == [
        agent.id,
        second_agent.id,
    ]
    response = client.get(
        f'/conversations/{conversation.id}/agents?offset=1&limit=1',
        headers=headers,
    )
    assert [item['id'] for item in response.json()] == [second_agent.id]
    response = client.get(
        f'/conversations/{second_conversation.id}/agents', headers=headers
    )
    assert [item['id'] for item in response.json()] == [agent.id]


def test_remove_agent_preserves_agent_and_conversation(
    client, conversation, agent, token
):
    headers = {'Authorization': f'Bearer {token}'}
    path = f'/conversations/{conversation.id}/agents/{agent.id}'
    assert client.put(path, headers=headers).status_code == HTTPStatus.OK
    assert (
        client.delete(path, headers=headers).status_code
        == HTTPStatus.NO_CONTENT
    )
    assert (
        client.get(
            f'/conversations/{conversation.id}/agents', headers=headers
        ).json()
        == []
    )
    assert (
        client.get(f'/agents/{agent.id}', headers=headers).status_code
        == HTTPStatus.OK
    )
    assert (
        client.get(
            f'/conversations/{conversation.id}', headers=headers
        ).status_code
        == HTTPStatus.OK
    )
    assert (
        client.delete(path, headers=headers).status_code
        == HTTPStatus.NOT_FOUND
    )


@pytest.fixture
def membership_context(client, conversation, agent, token, admin_token):
    return client, conversation, agent, token, admin_token


@pytest.mark.parametrize('method', ['get', 'put', 'delete'])
@pytest.mark.parametrize('role', ['user', 'admin'])
@pytest.mark.asyncio
async def test_other_owner_cannot_manage_membership(
    session, membership_context, method, role
):
    client, conversation, agent, _, admin_token = membership_context
    admin = await session.scalar(select(User).where(User.username == 'admin'))
    admin.role = UserRole(role)
    await session.commit()
    path = f'/conversations/{conversation.id}/agents'
    if method != 'get':
        path += f'/{agent.id}'
    response = client.request(
        method, path, headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Conversation not found'


@pytest.mark.parametrize('method', ['get', 'put', 'delete'])
def test_membership_requires_authentication(client, method):
    path = '/conversations/999/agents'
    if method != 'get':
        path += '/999'
    assert client.request(method, path).status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize('method', ['get', 'put', 'delete'])
def test_missing_conversation(client, token, method):
    path = '/conversations/999/agents'
    if method != 'get':
        path += '/999'
    response = client.request(
        method, path, headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Conversation not found'


@pytest.mark.parametrize('method', ['put', 'delete'])
def test_missing_agent(client, conversation, token, method):
    response = client.request(
        method,
        f'/conversations/{conversation.id}/agents/999',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize('target', ['conversation', 'agent'])
async def test_delete_parent_cleans_membership(
    session, membership_context, target
):
    client, conversation, agent, token, admin_token = membership_context
    headers = {'Authorization': f'Bearer {token}'}
    client.put(
        f'/conversations/{conversation.id}/agents/{agent.id}', headers=headers
    )
    if target == 'conversation':
        path = f'/conversations/{conversation.id}'
    else:
        headers = {'Authorization': f'Bearer {admin_token}'}
        path = f'/agents/{agent.id}'
    assert (
        client.delete(path, headers=headers).status_code
        == HTTPStatus.NO_CONTENT
    )
    count = await session.scalar(
        select(func.count()).select_from(conversation_agents)
    )
    assert count == 0
    if target == 'conversation':
        assert await session.get(Agent, agent.id) is not None
    else:
        assert await session.get(Conversation, conversation.id) is not None


@pytest.mark.asyncio
async def test_relationships_persist_from_both_sides(
    session, conversation, agent
):
    await session.refresh(conversation, ['agents'])
    conversation.agents.append(agent)
    await session.commit()
    session.expire_all()

    await session.refresh(agent, ['conversations'])
    assert agent.conversations == [conversation]
    agent.conversations.remove(conversation)
    await session.commit()
    session.expire_all()

    await session.refresh(conversation, ['agents'])
    assert conversation.agents == []
    count = await session.scalar(
        select(func.count()).select_from(conversation_agents)
    )
    assert count == 0
