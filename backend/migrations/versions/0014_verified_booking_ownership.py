"""Associate verified passenger accounts with bookings.

Revision ID: 0014_verified_booking_ownership
Revises: 0013_passenger_notifications
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0014_verified_booking_ownership"
down_revision = "0013_passenger_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.add_column(
        "bookings",
        sa.Column(
            "passenger_account_id", uuid,
            sa.ForeignKey("passenger_accounts.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_bookings_passenger_account_id", "bookings", ["passenger_account_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_bookings_passenger_account_id", table_name="bookings")
    op.drop_column("bookings", "passenger_account_id")
