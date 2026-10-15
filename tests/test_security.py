from http import HTTPStatus

from jwt import decode

from multi_agent_chat.core.security import create_access_token


def test_access_token(settings):
    payload = {'test': 'test'}

    token = create_access_token(payload)

    decoded_payload = decode(
        token,
        settings.SECRET_KEY,
        algorithms=settings.ALGORITHM,
    )

    assert decoded_payload['test'] == payload['test']
    assert 'exp' in decoded_payload


def test_invalid_access_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
