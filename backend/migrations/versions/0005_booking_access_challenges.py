"""Guest booking access challenges and CSRF grant binding.

Revision ID: 0005_booking_access_challenges
Revises: 0004_staff_auth_controls
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_booking_access_challenges"
down_revision = "0004_staff_auth_controls"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("booking_access_grants", sa.Column("csrf_token_hash", sa.String(128), nullable=False, server_default=""))
    op.create_table(
        "booking_access_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id", ondelete="CASCADE")),
        sa.Column("code_hash", sa.String(512), nullable=False),
        sa.Column("requester_ip_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_booking_access_challenges_booking_id", "booking_access_challenges", ["booking_id"])
    op.create_index("ix_booking_access_challenges_expires_at", "booking_access_challenges", ["expires_at"])

def downgrade() -> None:
    op.drop_table("booking_access_challenges")
    op.drop_column("booking_access_grants", "csrf_token_hash")
