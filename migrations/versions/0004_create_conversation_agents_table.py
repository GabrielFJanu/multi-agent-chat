"""Create conversation_agents table."""

import sqlalchemy as sa
from alembic import op

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'conversation_agents',
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['agent_id'], ['agents.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['conversation_id'], ['conversations.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('conversation_id', 'agent_id'),
    )


def downgrade() -> None:
    op.drop_table('conversation_agents')
