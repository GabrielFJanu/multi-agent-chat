from jwt import decode

from multi_agent_chat.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
)


def test_access_token():
    claims = {'test': 'test'}

    token = create_access_token(claims)

    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)

    assert decoded['test'] == claims['test']
    assert 'exp' in decoded
