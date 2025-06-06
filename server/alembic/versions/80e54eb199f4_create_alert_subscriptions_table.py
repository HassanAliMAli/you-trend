"""create_alert_subscriptions_table

Revision ID: 80e54eb199f4
Revises: bccb60026ecb
Create Date: 2025-05-27 17:18:58.146153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80e54eb199f4'
down_revision: Union[str, None] = 'bccb60026ecb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('alert_subscriptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('alert_type', sa.String(), nullable=False),
    sa.Column('criteria', sa.String(), nullable=False),
    sa.Column('notification_method', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_subscriptions_alert_type'), 'alert_subscriptions', ['alert_type'], unique=False)
    op.create_index(op.f('ix_alert_subscriptions_id'), 'alert_subscriptions', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_alert_subscriptions_id'), table_name='alert_subscriptions')
    op.drop_index(op.f('ix_alert_subscriptions_alert_type'), table_name='alert_subscriptions')
    op.drop_table('alert_subscriptions')
    # ### end Alembic commands ###
