"""Renamed user table to users

Revision ID: 93bd3ca13d08
Revises: 77cb4be53c15
Create Date: 2026-01-12 20:30:58.138674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93bd3ca13d08'
down_revision: Union[str, Sequence[str], None] = '77cb4be53c15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("user", "users")


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table("users", "user")
