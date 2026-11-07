"""Durable per-IP guest access challenge rate limits.

Revision ID: 0006_guest_access_rate_limits
Revises: 0005_booking_access_challenges
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_guest_access_rate_limits"
down_revision = "0005_booking_access_challenges"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "guest_access_rate_limits",
        sa.Column("key_hash", sa.String(64), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
    )

def downgrade() -> None:
    op.drop_table("guest_access_rate_limits")
