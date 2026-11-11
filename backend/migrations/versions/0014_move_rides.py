"""Authoritative Move ride lifecycle.
Revision ID: 0014_move_rides
Revises: 0013_location_consent
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "0014_move_rides"
down_revision = "0013_location_consent"
branch_labels = None
depends_on = None

def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "move_rides",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("service_code", sa.String(32), sa.ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False, server_default="move"),
        sa.Column("passenger_account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("driver_account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="RESTRICT")),
        sa.Column("status", sa.String(24), nullable=False, server_default="requested"),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("matched_at", sa.DateTime(timezone=True)), sa.Column("accepted_at", sa.DateTime(timezone=True)),
        sa.Column("arrived_at", sa.DateTime(timezone=True)), sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column("cancellation_reason_code", sa.String(80)),
        sa.CheckConstraint("status IN ('requested', 'matched', 'accepted', 'arrived', 'in_progress', 'completed', 'cancelled')", name="ck_move_ride_status"),
        sa.CheckConstraint("driver_account_id IS NULL OR driver_account_id <> passenger_account_id", name="ck_move_ride_distinct_participants"),
        sa.CheckConstraint("status IN ('requested', 'cancelled') OR driver_account_id IS NOT NULL", name="ck_move_ride_driver_required"),
        sa.CheckConstraint("completed_at IS NULL OR status = 'completed'", name="ck_move_ride_completed_timestamp"),
        sa.CheckConstraint("cancelled_at IS NULL OR status = 'cancelled'", name="ck_move_ride_cancelled_timestamp"),
    )
    op.create_index("ix_move_rides_passenger_status", "move_rides", ["passenger_account_id", "status"])
    op.create_index("ix_move_rides_driver_status", "move_rides", ["driver_account_id", "status"])

def downgrade() -> None:
    op.drop_index("ix_move_rides_driver_status", table_name="move_rides")
    op.drop_index("ix_move_rides_passenger_status", table_name="move_rides")
    op.drop_table("move_rides")
