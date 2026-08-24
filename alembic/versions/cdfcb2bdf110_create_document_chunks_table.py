"""create document chunks table

Revision ID: cdfcb2bdf110
Revises: 0d9a3f9bde3d
Create Date: 2026-08-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cdfcb2bdf110"
down_revision: Union[str, Sequence[str], None] = "0d9a3f9bde3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass