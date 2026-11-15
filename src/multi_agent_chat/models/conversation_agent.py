from sqlalchemy import Column, ForeignKey, Table

from multi_agent_chat.models.base import table_registry

conversation_agents = Table(
    'conversation_agents',
    table_registry.metadata,
    Column(
        'conversation_id',
        ForeignKey('conversations.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column(
        'agent_id',
        ForeignKey('agents.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)
