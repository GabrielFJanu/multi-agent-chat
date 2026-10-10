from dataclasses import asdict

from sqlalchemy import select

from multi_agent_chat.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test',
            email='teste@example.com',
            password='test123',
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'test'))

    assert asdict(user) == {
        'id': 1,
        'username': 'test',
        'email': 'teste@example.com',
        'password': 'test123',
        'created_at': time,
        'updated_at': time,
    }
