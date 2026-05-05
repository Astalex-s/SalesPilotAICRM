"""add tags and category to leads

Revision ID: 0003
Revises: 4e5bd33eebab
Create Date: 2026-05-05 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "4e5bd33eebab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column(
            "tags",
            sa.ARRAY(sa.String(100)),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "leads",
        sa.Column("category", sa.String(100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("leads", "category")
    op.drop_column("leads", "tags")
