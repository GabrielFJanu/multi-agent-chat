from http import HTTPStatus

from fastapi.testclient import TestClient

from src.multi_agent_chat.app import app


def test_create_user():
    client = TestClient(app)

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
