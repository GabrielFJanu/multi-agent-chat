from http import HTTPStatus

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from multi_agent_chat.models import Message


@pytest.fixture
def message_url(conversation):
    return f'/conversations/{conversation.id}/messages/'


@pytest.fixture
def headers(token):
    return {'Authorization': f'Bearer {token}'}


def test_message_lifecycle(client, message_url, headers, user):
    response = client.post(
        message_url,
        headers=headers,
        json={'content': 'Hello', 'user_id': 999},
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['user_id'] == user.id
    assert data['agent_id'] is None
    assert data['created_at']
    url = f'{message_url}{data["id"]}'
    assert client.get(url, headers=headers).json() == data
    assert client.get(message_url, headers=headers).json() == [data]
    assert client.get(message_url + '?offset=1', headers=headers).json() == []
    assert client.patch(url, headers=headers, json={}).json() == data
    for method in ['patch', 'put']:
        response = client.request(
            method,
            url,
            headers=headers,
            json={'content': method, 'agent_id': 999},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()['content'] == method
        assert response.json()['agent_id'] is None
    assert (
        client.delete(url, headers=headers).status_code
        == HTTPStatus.NO_CONTENT
    )
    assert client.get(url, headers=headers).status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures('conversation_with_agent')
@pytest.mark.parametrize('agent_id', [1, 999])
def test_public_creation_cannot_impersonate_agent(
    client, message_url, headers, user, agent_id
):
    response = client.post(
        message_url,
        headers=headers,
        json={'content': 'Reply', 'agent_id': agent_id, 'user_id': 999},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['agent_id'] is None
    assert response.json()['user_id'] == user.id


@pytest.mark.asyncio
async def test_internally_created_agent_message_is_readable(
    client, session, conversation_with_agent, agent, headers
):
    message = Message(
        conversation_id=conversation_with_agent.id,
        content='Internal reply',
        agent_id=agent.id,
    )
    session.add(message)
    await session.commit()
    response = client.get(
        f'/conversations/{conversation_with_agent.id}/messages/{message.id}',
        headers=headers,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['agent_id'] == agent.id
    assert response.json()['user_id'] is None
    assert response.json()['content'] == 'Internal reply'


@pytest.mark.parametrize('method', ['get', 'post', 'patch', 'put', 'delete'])
def test_access_control(client, message_url, headers, other_token, method):
    data = client.post(
        message_url, headers=headers, json={'content': 'Private'}
    ).json()
    url = message_url if method == 'post' else f'{message_url}{data["id"]}'
    response = client.request(method, url, json={'content': 'Changed'})
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    response = client.request(
        method,
        url,
        headers={'Authorization': f'Bearer {other_token}'},
        json={'content': 'Changed'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert (
        client.get(
            message_url, headers={'Authorization': f'Bearer {other_token}'}
        ).status_code
        == HTTPStatus.NOT_FOUND
    )


@pytest.mark.parametrize('content', [None, ''])
@pytest.mark.parametrize('method', ['post', 'patch', 'put'])
def test_invalid_content(client, message_url, headers, method, content):
    url = message_url if method == 'post' else message_url + '1'
    response = client.request(
        method, url, headers=headers, json={'content': content}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_conversation_removes_messages(
    client, session, conversation, message_url, headers
):
    client.post(message_url, headers=headers, json={'content': 'Hello'})
    response = client.delete(
        f'/conversations/{conversation.id}', headers=headers
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert await session.scalar(select(Message)) is None


@pytest.mark.asyncio
@pytest.mark.parametrize('both_authors', [False, True])
async def test_exactly_one_author(
    session, conversation, user, agent, both_authors
):
    session.add(
        Message(
            conversation_id=conversation.id,
            content='Invalid',
            user_id=user.id if both_authors else None,
            agent_id=agent.id if both_authors else None,
        )
    )
    with pytest.raises(IntegrityError):
        await session.commit()
    await session.rollback()


def test_message_cannot_be_accessed_through_another_conversation(
    client, message_url, headers, second_conversation_with_agent
):
    data = client.post(
        message_url, headers=headers, json={'content': 'Hello'}
    ).json()
    other_id = second_conversation_with_agent.id
    response = client.get(
        f'/conversations/{other_id}/messages/{data["id"]}', headers=headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
