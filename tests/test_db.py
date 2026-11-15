from dataclasses import asdict

import pytest
from sqlalchemy import func, select

from multi_agent_chat.models import User, UserRole, conversation_agents


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test',
            email='teste@example.com',
            password='test123',
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'test'))

    assert asdict(user) == {
        'id': 1,
        'username': 'test',
        'email': 'teste@example.com',
        'password': 'test123',
        'role': UserRole.USER,
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_relationships_persist_from_both_sides(
    session, conversation, agent
):
    await session.refresh(conversation, ['agents'])
    conversation.agents.append(agent)
    await session.commit()
    session.expire_all()

    await session.refresh(agent, ['conversations'])
    assert agent.conversations == [conversation]
    agent.conversations.remove(conversation)
    await session.commit()
    session.expire_all()

    await session.refresh(conversation, ['agents'])
    assert conversation.agents == []
    count = await session.scalar(
        select(func.count()).select_from(conversation_agents)
    )
    assert count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('target', ['conversation', 'agent'])
async def test_delete_parent_removes_conversation_agent_links(
    session, conversation_with_agent, agent, target
):
    parent = conversation_with_agent if target == 'conversation' else agent
    await session.delete(parent)
    await session.commit()

    count = await session.scalar(
        select(func.count()).select_from(conversation_agents)
    )
    assert count == 0
