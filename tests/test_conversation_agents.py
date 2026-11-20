from http import HTTPStatus

import pytest


def test_add_conversation_agent(client, conversation, agent, token):
    response = client.put(
        f'/conversations/{conversation.id}/agents/{agent.id}',
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


def test_list_conversation_agents(
    client, conversation_with_agent, agent, token
):
    response = client.get(
        f'/conversations/{conversation_with_agent.id}/agents',
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


def test_list_conversation_agents_with_offset(
    client, conversation_with_agent, token
):
    response = client.get(
        f'/conversations/{conversation_with_agent.id}/agents?offset=1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_add_conversation_agent_is_idempotent(
    client, conversation_with_agent, agent, token
):
    response = client.put(
        f'/conversations/{conversation_with_agent.id}/agents/{agent.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    response = client.get(
        f'/conversations/{conversation_with_agent.id}/agents',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert [item['id'] for item in response.json()] == [agent.id]


def test_conversation_supports_multiple_agents(
    client, conversation_with_agent, agent, second_agent, token
):
    path = f'/conversations/{conversation_with_agent.id}/agents'

    response = client.put(
        f'{path}/{second_agent.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    response = client.get(path, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert [item['id'] for item in response.json()] == [
        agent.id,
        second_agent.id,
    ]

    response = client.get(
        f'{path}?offset=1&limit=1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert [item['id'] for item in response.json()] == [second_agent.id]


def test_remove_conversation_agent(
    client, conversation_with_agent, agent, token
):
    path = f'/conversations/{conversation_with_agent.id}/agents'
    headers = {'Authorization': f'Bearer {token}'}

    response = client.delete(f'{path}/{agent.id}', headers=headers)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''

    response = client.get(path, headers=headers)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []

    response = client.get(f'/agents/{agent.id}', headers=headers)

    assert response.status_code == HTTPStatus.OK

    response = client.get(
        f'/conversations/{conversation_with_agent.id}', headers=headers
    )

    assert response.status_code == HTTPStatus.OK

    response = client.delete(f'{path}/{agent.id}', headers=headers)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Agent not found in conversation'}


def test_remove_agent_preserves_other_conversation(
    client,
    conversation_with_agent,
    second_conversation_with_agent,
    agent,
    token,
):
    headers = {'Authorization': f'Bearer {token}'}

    response = client.delete(
        f'/conversations/{conversation_with_agent.id}/agents/{agent.id}',
        headers=headers,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(
        f'/conversations/{second_conversation_with_agent.id}/agents',
        headers=headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert [item['id'] for item in response.json()] == [agent.id]


@pytest.mark.parametrize('access_token', ['other_token', 'admin_token'])
@pytest.mark.parametrize('method', ['get', 'put', 'delete'])
def test_other_users_cannot_manage_conversation_agents(
    client, conversation_with_agent, request, access_token, method
):
    agent = request.getfixturevalue('agent')
    token = request.getfixturevalue('token')
    other_token = request.getfixturevalue(access_token)
    path = f'/conversations/{conversation_with_agent.id}/agents'
    target_agent = (
        request.getfixturevalue('second_agent') if method == 'put' else agent
    )
    target = path if method == 'get' else f'{path}/{target_agent.id}'

    response = client.request(
        method,
        target,
        headers={'Authorization': f'Bearer {other_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Conversation not found'}

    response = client.get(path, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert [item['id'] for item in response.json()] == [agent.id]


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('get', '/conversations/1/agents'),
        ('put', '/conversations/1/agents/1'),
        ('delete', '/conversations/1/agents/1'),
    ],
)
def test_conversation_agent_routes_require_authentication(
    client, method, path
):
    response = client.request(method, path)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('get', '/conversations/999/agents'),
        ('put', '/conversations/999/agents/1'),
        ('delete', '/conversations/999/agents/1'),
    ],
)
def test_conversation_not_found(client, token, method, path):
    response = client.request(
        method,
        path,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Conversation not found'}


@pytest.mark.parametrize(
    ('method', 'detail'),
    [
        ('put', 'Agent not found'),
        ('delete', 'Agent not found in conversation'),
    ],
)
def test_agent_not_found(client, conversation, token, method, detail):
    response = client.request(
        method,
        f'/conversations/{conversation.id}/agents/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': detail}


def test_delete_conversation_preserves_agent(
    client, conversation_with_agent, agent, token
):
    headers = {'Authorization': f'Bearer {token}'}

    response = client.delete(
        f'/conversations/{conversation_with_agent.id}', headers=headers
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(f'/agents/{agent.id}', headers=headers)

    assert response.status_code == HTTPStatus.OK


def test_delete_agent_removes_conversation_membership(
    client, conversation_with_agent, agent, admin_token, token
):
    response = client.delete(
        f'/agents/{agent.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get(
        f'/conversations/{conversation_with_agent.id}/agents',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []
