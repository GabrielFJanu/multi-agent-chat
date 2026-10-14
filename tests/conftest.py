from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from multi_agent_chat.app import app
from multi_agent_chat.database import get_session
from multi_agent_chat.models import User, table_registry
from multi_agent_chat.security import get_password_hash


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user(session):
    plain_password = 'test123'
    hashed_password = get_password_hash(plain_password)
    user = User(
        username='test',
        email='test@example.com',
        password=hashed_password,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.plain_password = plain_password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/login',
        data={'username': user.username, 'password': user.plain_password},
    )
    return response.json()['access_token']


@contextmanager
def _mock_db_time(*, model, time=datetime.now()):

    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
