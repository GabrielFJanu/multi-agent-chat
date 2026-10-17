from http import HTTPStatus


def test_login_for_access_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.username,
            'password': user.plain_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token
    assert token['token_type'] == 'Bearer'


def test_refresh_access_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    new_token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in new_token
    assert 'token_type' in new_token
    assert new_token['token_type'] == 'Bearer'
