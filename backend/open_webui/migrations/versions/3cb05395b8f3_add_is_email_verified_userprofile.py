"""Add is_email_verified UserProfile

Revision ID: 3cb05395b8f3
Revises: 5b475881d81b
Create Date: 2025-07-23 10:41:49.663121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '3cb05395b8f3'
down_revision: Union[str, None] = '5b475881d81b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_profile', sa.Column('is_email_verified', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('user_profile', 'is_email_verified')
