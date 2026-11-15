"""Create conversations table."""
from alembic import op
import sqlalchemy as sa

revision = 'b83d042c8e15'
down_revision = 'a62f931b7c04'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('conversations')
