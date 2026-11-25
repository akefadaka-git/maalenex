"""Passenger in-app notifications and preferences.

Revision ID: 0013_passenger_notifications
Revises: 0012_passenger_wallet
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0013_passenger_notifications"
down_revision = "0012_passenger_wallet"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "passenger_notifications",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("passenger_id", uuid, sa.ForeignKey("passenger_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notification_type", sa.String(48), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.String(48), nullable=True),
        sa.Column("resource_reference", sa.String(64), nullable=True),
        sa.Column("dedupe_key", sa.String(128), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("dedupe_key", name="uq_passenger_notifications_dedupe_key"),
    )
    op.create_index("ix_passenger_notifications_owner_created", "passenger_notifications", ["passenger_id", "created_at"])
    op.create_index("ix_passenger_notifications_owner_read", "passenger_notifications", ["passenger_id", "read_at"])
    op.create_table(
        "passenger_notification_preferences",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("passenger_id", uuid, sa.ForeignKey("passenger_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sms_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("passenger_id", name="uq_passenger_notification_preferences_owner"),
    )


def downgrade() -> None:
    op.drop_table("passenger_notification_preferences")
    op.drop_index("ix_passenger_notifications_owner_read", table_name="passenger_notifications")
    op.drop_index("ix_passenger_notifications_owner_created", table_name="passenger_notifications")
    op.drop_table("passenger_notifications")
