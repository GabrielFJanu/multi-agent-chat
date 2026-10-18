from http import HTTPStatus

import pytest

from multi_agent_chat.models.user import User


def test_create_user(client, mock_db_time):
    with mock_db_time(model=User) as time:
        response = client.post(
            '/users/',
            json={
                'username': 'test',
                'email': 'test@example.com',
                'password': 'test123',
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@example.com',
        'role': 'user',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


def test_get_my_profile(client, user, token):
    response = client.get(
        '/users/me',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': 'user',
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


def test_update_my_profile(client, user, token):
    response = client.patch(
        '/users/me',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'test2',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'test2',
        'email': user.email,
        'role': 'user',
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


def test_replace_my_profile(client, user, token):
    response = client.put(
        '/users/me',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'test2',
            'email': 'test2@example.com',
            'password': 'test2123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'test2',
        'email': 'test2@example.com',
        'role': 'user',
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


def test_delete_my_account(client, user, token):
    response = client.delete(
        '/users/me',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_get_user_by_id(client, user, admin_token):
    response = client.get(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': 'user',
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


def test_admin_update_user(client, user, admin_token):
    response = client.patch(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'username': 'test2',
            'role': 'admin',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'test2',
        'email': user.email,
        'role': 'admin',
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


def test_admin_replace_user(client, user, admin_token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'username': 'test2',
            'role': 'admin',
            'email': 'test2@example.com',
            'password': 'test2123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'test2',
        'email': 'test2@example.com',
        'role': 'admin',
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


def test_admin_delete_user(client, user, admin_token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_list_all_users(client, user, admin, admin_token):
    response = client.get(
        '/users/',
        headers={'Authorization': f'Bearer {admin_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            'id': account.id,
            'username': account.username,
            'email': account.email,
            'role': account.role.value,
            'created_at': account.created_at.isoformat(),
            'updated_at': account.updated_at.isoformat(),
        }
        for account in (user, admin)
    ]


@pytest.mark.parametrize(
    ('method', 'path'),
    [
        ('get', '/users/'),
        ('get', '/users/1'),
        ('patch', '/users/1'),
        ('put', '/users/1'),
        ('delete', '/users/1'),
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


@pytest.mark.parametrize('method', ['get', 'patch', 'put', 'delete'])
def test_my_profile_requires_authentication(client, method):
    response = client.request(method, '/users/me')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
