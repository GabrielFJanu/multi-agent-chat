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
