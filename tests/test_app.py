from http import HTTPStatus


def test_create_user(client):
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
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {'id': 1, 'username': 'test', 'email': 'test@example.com'},
            {'id': 2, 'username': 'test2', 'email': 'test2@example.com'},
        ]
    }


def test_read_user(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@example.com',
    }


def test_update_user(client):
    response = client.patch(
        '/users/1',
        json={
            'username': 'test2',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'test2',
        'email': 'test@example.com',
    }


def test_replace_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'test2',
            'email': 'test2@example.com',
            'password': 'test2123',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'test2',
        'email': 'test2@example.com',
    }
