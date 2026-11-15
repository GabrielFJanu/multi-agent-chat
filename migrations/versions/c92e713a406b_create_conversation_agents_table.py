"""Create conversation_agents table."""
from alembic import op
import sqlalchemy as sa

revision = 'c92e713a406b'
down_revision = 'b83d042c8e15'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'conversation_agents',
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('agent_id', sa.Integer(), sa.ForeignKey('agents.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('conversation_agents')
