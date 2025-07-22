"""Add UserProfile

Revision ID: 5b475881d81b
Revises: 5ca4b28d4bc8
Create Date: 2025-07-21 14:36:45.597008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '5b475881d81b'
down_revision: Union[str, None] = '5ca4b28d4bc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_profile',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('charity_id', sa.Integer(), sa.ForeignKey('charity.id'), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False, unique=True),
    )

def downgrade() -> None:
    op.drop_table('user_profile')
