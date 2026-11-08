"""Persisted rate limits for account challenge resend requests.

Revision ID: 0012_account_challenge_resend_limits
Revises: 0011_account_identity_lifecycle
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_challenge_resend"
down_revision = "0011_account_identity_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_challenge_requests",
        sa.Column("key_digest", sa.String(64), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("account_challenge_requests")
