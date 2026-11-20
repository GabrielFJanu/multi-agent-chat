from http import HTTPStatus

import pytest

from multi_agent_chat.models.agent import Agent
from multi_agent_chat.models.message import Message


def test_create_agent(client, admin_token, mock_db_time):
    with mock_db_time(model=Agent) as time:
        response = client.post(
            '/agents/',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'test',
                'description': 'Test agent',
                'model': 'test-model',
                'system_prompt': 'Be helpful.',
                'temperature': 0.7,
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'test',
        'description': 'Test agent',
        'model': 'test-model',
        'system_prompt': 'Be helpful.',
        'temperature': 0.7,
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


def test_get_agent_by_id(client, agent, token):
    response = client.get(
        f'/agents/{agent.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': agent.id,
        'name': agent.name,
        'description': agent.description,
        'model': agent.model,
        'system_prompt': agent.system_prompt,
        'temperature': agent.temperature,
        'created_at': agent.created_at.isoformat(),
        'updated_at': agent.updated_at.isoformat(),
    }


def test_update_agent(client, agent, admin_token):
    response = client.patch(
        f'/agents/{agent.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'test2',
            'temperature': 0,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': agent.id,
        'name': 'test2',
        'description': agent.description,
        'model': agent.model,
        'system_prompt': agent.system_prompt,
        'temperature': 0,
        'created_at': agent.created_at.isoformat(),
        'updated_at': agent.updated_at.isoformat(),
    }


def test_replace_agent(client, agent, admin_token):
    response = client.put(
        f'/agents/{agent.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'test2',
            'description': 'New description',
            'model': 'another-model',
            'system_prompt': 'New prompt',
            'temperature': 1.0,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': agent.id,
        'name': 'test2',
        'description': 'New description',
        'model': 'another-model',
        'system_prompt': 'New prompt',
        'temperature': 1.0,
        'created_at': agent.created_at.isoformat(),
        'updated_at': agent.updated_at.isoformat(),
    }


def test_delete_agent(client, agent, admin_token):
    response = client.delete(
        f'/agents/{agent.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''

    response = client.get(
        f'/agents/{agent.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_list_all_agents(client, agent, token):
    response = client.get(
        '/agents/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            'id': agent.id,
            'name': agent.name,
            'description': agent.description,
            'model': agent.model,
            'system_prompt': agent.system_prompt,
            'temperature': agent.temperature,
            'created_at': agent.created_at.isoformat(),
            'updated_at': agent.updated_at.isoformat(),
        }
    ]


def test_list_agents_with_offset(client, agent, token):
    response = client.get(
        '/agents/?offset=1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('post', '/agents/'),
        ('patch', '/agents/1'),
        ('put', '/agents/1'),
        ('delete', '/agents/1'),
    ],
)
def test_admin_routes_forbid_regular_user(client, token, method, path):
    response = client.request(
        method,
        path,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('get', '/agents/'),
        ('get', '/agents/1'),
        ('post', '/agents/'),
        ('patch', '/agents/1'),
        ('put', '/agents/1'),
        ('delete', '/agents/1'),
    ],
)
def test_agent_routes_require_authentication(client, method, path):
    response = client.request(method, path)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize('method', ['get', 'patch', 'put', 'delete'])
def test_agent_not_found(client, admin_token, method):
    response = client.request(
        method,
        '/agents/999',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'name': 'test',
            'description': 'Test agent',
            'model': 'test-model',
            'system_prompt': 'Be helpful.',
            'temperature': 0.7,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Agent not found'}


@pytest.mark.parametrize(
    ('method', 'path'), [('post', '/agents/'), ('put', '/agents/1')]
)
def test_full_payload_required(client, admin_token, method, path):
    response = client.request(
        method,
        path,
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'name': 'Incomplete'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    'field', ['name', 'description', 'model', 'system_prompt', 'temperature']
)
def test_patch_agent_rejects_null(client, agent, admin_token, field):
    response = client.patch(
        f'/agents/{agent.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={field: None},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_patch_agent_preserves_omitted_fields(client, agent, admin_token):
    headers = {'Authorization': f'Bearer {admin_token}'}
    url = f'/agents/{agent.id}'
    before = client.get(url, headers=headers).json()
    response = client.patch(url, headers=headers, json={})
    assert response.status_code == HTTPStatus.OK
    assert response.json() == before


@pytest.mark.asyncio
async def test_delete_agent_with_messages_returns_conflict(
    client, session, conversation_with_agent, admin_token
):
    agent = conversation_with_agent.agents[0]
    agent_id = agent.id
    conversation_id = conversation_with_agent.id
    message = Message(
        conversation_id=conversation_id, agent_id=agent_id, content='Keep'
    )
    session.add(message)
    await session.commit()
    message_id = message.id
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.delete(f'/agents/{agent_id}', headers=headers)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Cannot delete an agent with messages'
    }
    assert (
        client.get(f'/agents/{agent_id}', headers=headers).status_code
        == HTTPStatus.OK
    )
    await session.refresh(message)
    assert message.agent_id == agent_id
    assert message.id == message_id
    await session.refresh(conversation_with_agent, ['agents'])
    assert [item.id for item in conversation_with_agent.agents] == [agent_id]
