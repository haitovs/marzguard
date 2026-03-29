"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-03-29
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "policies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("default_ip_limit", sa.Integer(), nullable=True),
        sa.Column("auto_reenable", sa.Boolean(), default=True),
        sa.Column("reenable_delay_sec", sa.Integer(), default=300),
        sa.Column("notify_on_violation", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "user_ip_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("ip_limit", sa.Integer(), nullable=True),
        sa.Column("policy_id", sa.Integer(), nullable=True),
        sa.Column("is_monitored", sa.Boolean(), default=True),
        sa.Column("is_exempt", sa.Boolean(), default=False),
        sa.Column("auto_reenable", sa.Boolean(), default=True),
        sa.Column("reenable_delay_sec", sa.Integer(), nullable=True),
        sa.Column("disabled_at", sa.DateTime(), nullable=True),
        sa.Column("disabled_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_ip_configs_username", "user_ip_configs", ["username"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_addresses", sa.Text(), nullable=True),
        sa.Column("source", sa.String(50), default="system"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"])
    op.create_index("ix_audit_logs_username", "audit_logs", ["username"])

    op.create_table(
        "global_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("global_settings")
    op.drop_table("audit_logs")
    op.drop_table("user_ip_configs")
    op.drop_table("policies")
