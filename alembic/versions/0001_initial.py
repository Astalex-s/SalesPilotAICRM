"""Initial schema — all tables

Revision ID: 0001
Revises: None
Create Date: 2026-05-04

Tables created:
  users, pipelines, stages, leads, deals,
  activities, email_messages, gdpr_audit_log, deal_attachments

Enums created:
  userrole, leadstatus, leadsource, dealstatus,
  activitytype, emaildirection, gdpreventtype
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── Enum helpers ─────────────────────────────────────────────────────────────

def _create_enums() -> None:
    op.execute(
        "CREATE TYPE userrole AS ENUM ('admin', 'manager', 'sales_rep')"
    )
    op.execute(
        "CREATE TYPE leadstatus AS ENUM "
        "('new', 'contacted', 'qualified', 'unqualified', 'converted')"
    )
    op.execute(
        "CREATE TYPE leadsource AS ENUM "
        "('website', 'referral', 'cold_call', 'social_media', 'email_campaign', 'other')"
    )
    op.execute(
        "CREATE TYPE dealstatus AS ENUM ('open', 'won', 'lost')"
    )
    op.execute(
        "CREATE TYPE activitytype AS ENUM "
        "('call', 'email', 'meeting', 'note', 'status_change', 'stage_change', 'lead_converted')"
    )
    op.execute(
        "CREATE TYPE emaildirection AS ENUM ('inbound', 'outbound')"
    )
    op.execute(
        "CREATE TYPE gdpreventtype AS ENUM "
        "('user_data_deleted', 'lead_anonymized', 'user_data_exported', 'retention_policy_applied')"
    )


def _drop_enums() -> None:
    for name in (
        "gdpreventtype",
        "emaildirection",
        "activitytype",
        "dealstatus",
        "leadsource",
        "leadstatus",
        "userrole",
    ):
        op.execute(f"DROP TYPE IF EXISTS {name}")


# ── upgrade ──────────────────────────────────────────────────────────────────

def upgrade() -> None:
    _create_enums()

    # ── users ────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "admin", "manager", "sales_rep",
                name="userrole",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── pipelines ────────────────────────────────────────────────────────────
    op.create_table(
        "pipelines",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pipelines_owner_id", "pipelines", ["owner_id"])

    # ── stages ───────────────────────────────────────────────────────────────
    op.create_table(
        "stages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("pipeline_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("probability", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("color", sa.String(20), nullable=True),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pipeline_id", "order", name="uq_stage_pipeline_order"),
    )
    op.create_index("ix_stages_pipeline_id", "stages", ["pipeline_id"])

    # ── leads ────────────────────────────────────────────────────────────────
    op.create_table(
        "leads",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "new", "contacted", "qualified", "unqualified", "converted",
                name="leadstatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.Enum(
                "website", "referral", "cold_call", "social_media", "email_campaign", "other",
                name="leadsource",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("notes", sa.String(2000), nullable=True),
        sa.Column("converted_deal_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_index("ix_leads_owner_id", "leads", ["owner_id"])

    # ── deals ────────────────────────────────────────────────────────────────
    op.create_table(
        "deals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("stage_id", sa.UUID(), nullable=False),
        sa.Column("pipeline_id", sa.UUID(), nullable=False),
        sa.Column("value_amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("value_currency", sa.String(3), nullable=False),
        sa.Column(
            "status",
            sa.Enum("open", "won", "lost", name="dealstatus", create_type=False),
            nullable=False,
        ),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("source_lead_id", sa.UUID(), nullable=True),
        sa.Column("expected_close_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["stage_id"], ["stages.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_deals_owner_id", "deals", ["owner_id"])
    op.create_index("ix_deals_stage_id", "deals", ["stage_id"])
    op.create_index("ix_deals_pipeline_id", "deals", ["pipeline_id"])

    # ── activities ───────────────────────────────────────────────────────────
    op.create_table(
        "activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column(
            "activity_type",
            sa.Enum(
                "call", "email", "meeting", "note",
                "status_change", "stage_change", "lead_converted",
                name="activitytype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("performed_by_id", sa.UUID(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_entity_type", "activities", ["entity_type"])
    op.create_index("ix_activities_entity_id", "activities", ["entity_id"])
    op.create_index("ix_activities_performed_by_id", "activities", ["performed_by_id"])
    op.create_index("ix_activities_occurred_at", "activities", ["occurred_at"])

    # ── email_messages ───────────────────────────────────────────────────────
    op.create_table(
        "email_messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("gmail_message_id", sa.String(255), nullable=False),
        sa.Column("gmail_thread_id", sa.String(255), nullable=False),
        sa.Column("from_address", sa.String(320), nullable=False),
        sa.Column("to_addresses", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "direction",
            sa.Enum("inbound", "outbound", name="emaildirection", create_type=False),
            nullable=False,
        ),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lead_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("gmail_message_id"),
    )
    op.create_index("ix_email_messages_gmail_message_id", "email_messages", ["gmail_message_id"])
    op.create_index("ix_email_messages_gmail_thread_id", "email_messages", ["gmail_thread_id"])
    op.create_index("ix_email_messages_lead_id", "email_messages", ["lead_id"])
    op.create_index(
        "ix_email_messages_from_received",
        "email_messages",
        ["from_address", "received_at"],
    )

    # ── gdpr_audit_log ───────────────────────────────────────────────────────
    op.create_table(
        "gdpr_audit_log",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "event_type",
            sa.Enum(
                "user_data_deleted", "lead_anonymized",
                "user_data_exported", "retention_policy_applied",
                name="gdpreventtype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("target_type", sa.String(20), nullable=False),
        sa.Column("target_id", sa.UUID(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("performed_by_id", sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gdpr_audit_log_event_type", "gdpr_audit_log", ["event_type"])
    op.create_index("ix_gdpr_audit_log_target_type", "gdpr_audit_log", ["target_type"])
    op.create_index("ix_gdpr_audit_log_target_id", "gdpr_audit_log", ["target_id"])
    op.create_index("ix_gdpr_audit_log_performed_at", "gdpr_audit_log", ["performed_at"])

    # ── deal_attachments ─────────────────────────────────────────────────────
    op.create_table(
        "deal_attachments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("deal_id", sa.UUID(), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("content_type", sa.String(200), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["deal_id"], ["deals.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_deal_attachments_deal_id", "deal_attachments", ["deal_id"])


# ── downgrade ─────────────────────────────────────────────────────────────────

def downgrade() -> None:
    op.drop_table("deal_attachments")
    op.drop_table("gdpr_audit_log")
    op.drop_table("email_messages")
    op.drop_table("activities")
    op.drop_table("deals")
    op.drop_table("leads")
    op.drop_table("stages")
    op.drop_table("pipelines")
    op.drop_table("users")
    _drop_enums()
