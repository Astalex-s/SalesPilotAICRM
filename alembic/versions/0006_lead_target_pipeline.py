"""add target_pipeline_id to leads

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-06 12:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("target_pipeline_id", sa.UUID(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("leads", "target_pipeline_id")
