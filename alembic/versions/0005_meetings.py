"""create meetings table

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-05 14:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE meetingstatus AS ENUM ('scheduled', 'completed', 'cancelled')")
    op.create_table(
        "meetings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("lead_id", sa.UUID(), nullable=True),
        sa.Column("deal_id", sa.UUID(), nullable=True),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("scheduled", "completed", "cancelled", name="meetingstatus", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_meetings_start_time", "meetings", ["start_time"])
    op.create_index("ix_meetings_created_by_id", "meetings", ["created_by_id"])
    op.create_index("ix_meetings_lead_id", "meetings", ["lead_id"])
    op.create_index("ix_meetings_deal_id", "meetings", ["deal_id"])


def downgrade() -> None:
    op.drop_index("ix_meetings_deal_id", "meetings")
    op.drop_index("ix_meetings_lead_id", "meetings")
    op.drop_index("ix_meetings_created_by_id", "meetings")
    op.drop_index("ix_meetings_start_time", "meetings")
    op.drop_table("meetings")
    op.execute("DROP TYPE meetingstatus")
