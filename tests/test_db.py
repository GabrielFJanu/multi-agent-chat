import pytest
from sqlalchemy import delete, func, inspect, select, text

from multi_agent_chat.models import (
    Agent,
    Conversation,
    Message,
    User,
    UserRole,
    conversation_agents,
)


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

    assert {
        attr.key: getattr(user, attr.key)
        for attr in inspect(User).column_attrs
    } == {
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


@pytest.mark.asyncio
@pytest.mark.parametrize('author_type', ['user', 'agent'])
async def test_message_relationships_are_bidirectional(
    session, user, agent, author_type
):
    conversation = Conversation(user_id=user.id, title='Relationships')
    conversation.user = user
    session.add(conversation)
    await session.flush()
    message = Message(conversation_id=conversation.id, content='Hello')
    message.conversation = conversation
    author = user if author_type == 'user' else agent
    setattr(message, author_type, author)
    session.add(message)
    await session.commit()
    session.expire_all()

    await session.refresh(message, ['conversation', 'user', 'agent'])
    await session.refresh(conversation, ['user', 'messages'])
    await session.refresh(user, ['conversations', 'messages'])
    await session.refresh(agent, ['messages'])

    assert message.conversation is conversation
    assert conversation.user is user
    assert conversation in user.conversations
    assert message in conversation.messages
    assert getattr(message, author_type) is author
    assert message in author.messages
    other_author = agent if author_type == 'user' else user
    assert message not in other_author.messages


@pytest.mark.asyncio
async def test_removing_message_from_conversation_deletes_orphan(
    session, conversation, user
):
    message = Message(
        conversation_id=conversation.id, content='Hello', user_id=user.id
    )
    session.add(message)
    await session.commit()
    message_id = message.id
    await session.refresh(conversation, ['messages'])
    conversation.messages.remove(message)
    await session.commit()

    assert await session.get(Message, message_id) is None


@pytest.mark.asyncio
@pytest.mark.parametrize('mode', ['orm_loaded', 'orm_unloaded', 'sql'])
async def test_delete_user_cascades_and_preserves_shared_agents(
    session, user, agent, conversation_with_agent, mode
):
    if mode == 'sql':
        # Direct SQL bypasses ORM cascades and needs database enforcement.
        await session.execute(text('PRAGMA foreign_keys=ON'))

    other = User(username='survivor', email='survivor@test.com', password='pw')
    session.add(other)
    await session.flush()
    surviving_conversation = Conversation(user_id=other.id, title='Keep')
    surviving_conversation.agents.append(agent)
    session.add(surviving_conversation)
    await session.flush()
    session.add_all([
        Message(
            conversation_id=conversation_with_agent.id,
            user_id=user.id,
            content='Delete user message',
        ),
        Message(
            conversation_id=conversation_with_agent.id,
            agent_id=agent.id,
            content='Delete agent reply',
        ),
        Message(
            conversation_id=surviving_conversation.id,
            agent_id=agent.id,
            content='Keep reply',
        ),
    ])
    await session.commit()
    user_id = user.id
    survivor_id = other.id
    conversation_id = surviving_conversation.id
    agent_id = agent.id
    session.expire_all()
    if mode == 'sql':
        await session.execute(delete(User).where(User.id == user_id))
    else:
        await session.refresh(user)
        if mode == 'orm_loaded':
            await session.refresh(user, ['conversations', 'messages'])
            await session.refresh(conversation_with_agent, ['messages'])
        await session.delete(user)
    await session.commit()
    session.expunge_all()

    assert await session.get(User, user_id) is None
    assert await session.get(User, survivor_id) is not None
    assert await session.get(Agent, agent_id) is not None
    assert list(await session.scalars(select(Conversation.id))) == [
        conversation_id
    ]
    assert list(await session.scalars(select(Message.content))) == [
        'Keep reply'
    ]
    assert list(
        (await session.execute(select(conversation_agents))).all()
    ) == [(conversation_id, agent_id)]
