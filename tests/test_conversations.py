from http import HTTPStatus

import pytest

from multi_agent_chat.models.conversation import Conversation


def test_create_conversation(client, user, token, mock_db_time):
    with mock_db_time(model=Conversation) as time:
        response = client.post(
            '/conversations/',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'Test conversation', 'user_id': 999},
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'user_id': user.id,
        'title': 'Test conversation',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


def test_get_conversation_by_id(client, conversation, token):
    response = client.get(
        f'/conversations/{conversation.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': conversation.id,
        'user_id': conversation.user_id,
        'title': conversation.title,
        'created_at': conversation.created_at.isoformat(),
        'updated_at': conversation.updated_at.isoformat(),
    }


@pytest.mark.parametrize('method', ['patch', 'put'])
def test_update_and_replace_conversation(client, conversation, token, method):
    response = client.request(
        method,
        f'/conversations/{conversation.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Updated conversation', 'user_id': 999},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': conversation.id,
        'user_id': conversation.user_id,
        'title': 'Updated conversation',
        'created_at': conversation.created_at.isoformat(),
        'updated_at': conversation.updated_at.isoformat(),
    }


def test_patch_preserves_omitted_title(client, conversation, token):
    response = client.patch(
        f'/conversations/{conversation.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == conversation.title


def test_delete_conversation(client, conversation, token):
    response = client.delete(
        f'/conversations/{conversation.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''

    response = client.get(
        f'/conversations/{conversation.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_list_my_conversations(client, conversation, token):
    response = client.get(
        '/conversations/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            'id': conversation.id,
            'user_id': conversation.user_id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
        }
    ]


def test_list_conversations_with_offset(client, conversation, token):
    response = client.get(
        '/conversations/?offset=1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.parametrize('access_token', ['other_token', 'admin_token'])
@pytest.mark.parametrize('method', ['get', 'patch', 'put', 'delete'])
def test_other_users_cannot_access_conversation(
    client, conversation, request, access_token, method
):
    other_token = request.getfixturevalue(access_token)

    response = client.request(
        method,
        f'/conversations/{conversation.id}',
        headers={'Authorization': f'Bearer {other_token}'},
        json={'title': 'Unauthorized change'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Conversation not found'}

    token = request.getfixturevalue('token')

    response = client.get(
        f'/conversations/{conversation.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == conversation.title


@pytest.mark.parametrize('access_token', ['other_token', 'admin_token'])
def test_list_excludes_other_users_conversations(
    client, conversation, request, access_token
):
    other_token = request.getfixturevalue(access_token)

    response = client.get(
        '/conversations/',
        headers={'Authorization': f'Bearer {other_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('post', '/conversations/'),
        ('get', '/conversations/'),
        ('get', '/conversations/1'),
        ('patch', '/conversations/1'),
        ('put', '/conversations/1'),
        ('delete', '/conversations/1'),
    ],
)
def test_conversation_routes_require_authentication(client, method, path):
    response = client.request(method, path)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize('method', ['get', 'patch', 'put', 'delete'])
def test_conversation_not_found(client, token, method):
    response = client.request(
        method,
        '/conversations/999',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Test conversation'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Conversation not found'}


@pytest.mark.parametrize(
    ('method', 'path'),
    [('post', '/conversations/'), ('put', '/conversations/1')],
)
def test_full_payload_required(client, token, method, path):
    response = client.request(
        method,
        path,
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_patch_conversation_rejects_null(client, conversation, token):
    response = client.patch(
        f'/conversations/{conversation.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': None},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
