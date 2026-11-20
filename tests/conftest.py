from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from multi_agent_chat.app import app
from multi_agent_chat.core.database import get_session
from multi_agent_chat.core.security import (
    create_access_token,
    get_password_hash,
)
from multi_agent_chat.core.settings import Settings
from multi_agent_chat.models import (
    Agent,
    Conversation,
    User,
    UserRole,
    table_registry,
)


@pytest.fixture
def settings():
    return Settings()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session):
    plain_password = 'test123'
    hashed_password = get_password_hash(plain_password)
    user = User(
        username='test',
        email='test@example.com',
        password=hashed_password,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.plain_password = plain_password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.plain_password},
    )
    return response.json()['access_token']


@pytest_asyncio.fixture
async def admin(session):
    plain_password = 'admin123'
    hashed_password = get_password_hash(plain_password)
    admin = User(
        username='admin',
        email='admin@example.com',
        password=hashed_password,
        role=UserRole.ADMIN,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)

    admin.plain_password = plain_password

    return admin


@pytest.fixture
def admin_token(client, admin):
    response = client.post(
        '/auth/token',
        data={'username': admin.username, 'password': admin.plain_password},
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


@pytest_asyncio.fixture
async def agent(session):
    agent = Agent(
        name='test',
        description='Test agent',
        model='test-model',
        system_prompt='Be helpful.',
        temperature=0.7,
    )
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def conversation(session, user):
    conversation = Conversation(user_id=user.id, title='Test conversation')
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


@pytest_asyncio.fixture
async def other_token(session):
    user = User(username='other', email='other@example.com', password='unused')
    session.add(user)
    await session.commit()
    return create_access_token({'sub': user.username})


@pytest_asyncio.fixture
async def conversation_with_agent(session, conversation, agent):
    await session.refresh(conversation, ['agents'])
    conversation.agents.append(agent)
    await session.commit()
    return conversation


@pytest_asyncio.fixture
async def second_agent(session):
    agent = Agent(
        name='second',
        description='Second agent',
        model='test-model',
        system_prompt='Be helpful.',
        temperature=0.5,
    )
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def second_conversation_with_agent(session, user, agent):
    conversation = Conversation(user_id=user.id, title='Second conversation')
    conversation.agents.append(agent)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
