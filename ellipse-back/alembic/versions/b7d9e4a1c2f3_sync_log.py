"""sync log tables

Таблицы журнала синхронизации с 1С: sync_log, sync_unmatched, sync_session.

Revision ID: b7d9e4a1c2f3
Revises: a3c1f0d2b7e4
Create Date: 2026-11-18 12:05:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7d9e4a1c2f3"
down_revision: Union[str, Sequence[str], None] = "a3c1f0d2b7e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sync_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("received_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("batch_id", sa.String(length=100), nullable=True),
        sa.Column("mode", sa.String(length=10), nullable=False),
        sa.Column("is_final", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("items_received", sa.Integer(), nullable=False),
        sa.Column("items_applied", sa.Integer(), nullable=False),
        sa.Column("prices_inserted", sa.Integer(), nullable=False),
        sa.Column("prices_unchanged", sa.Integer(), nullable=False),
        sa.Column("zeroed", sa.Integer(), nullable=False),
        sa.Column("unmatched_products", sa.Integer(), nullable=False),
        sa.Column("unmatched_stores", sa.Integer(), nullable=False),
        sa.Column("rejected_count", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("client_ip", sa.String(length=64), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("rejected", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_log_received_at", "sync_log", ["received_at"])
    op.create_index("ix_sync_log_batch_id", "sync_log", ["batch_id"])
    op.create_index("ix_sync_log_status", "sync_log", ["status"])

    op.create_table(
        "sync_unmatched",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("external_id", sa.String(length=200), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("seen_count", sa.Integer(), nullable=False),
        sa.Column("sample", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kind", "external_id", name="uq_sync_unmatched_kind_ext"),
    )

    op.create_table(
        "sync_session",
        sa.Column("batch_id", sa.String(length=100), nullable=False),
        sa.Column("started_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("store_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("batch_id"),
    )


def downgrade() -> None:
    op.drop_table("sync_session")
    op.drop_table("sync_unmatched")
    op.drop_index("ix_sync_log_status", table_name="sync_log")
    op.drop_index("ix_sync_log_batch_id", table_name="sync_log")
    op.drop_index("ix_sync_log_received_at", table_name="sync_log")
    op.drop_table("sync_log")
