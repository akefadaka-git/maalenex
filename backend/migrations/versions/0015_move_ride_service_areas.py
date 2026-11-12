"""Persist pickup and drop-off service areas on Move rides.

Revision ID: 0015_move_ride_service_areas
Revises: 0014_move_rides
"""
from alembic import op
import sqlalchemy as sa

revision = "0015_move_ride_service_areas"
down_revision = "0014_move_rides"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "move_rides",
        sa.Column(
            "pickup_area_code", sa.String(48),
            sa.ForeignKey("service_areas.code", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    op.add_column(
        "move_rides",
        sa.Column(
            "dropoff_area_code", sa.String(48),
            sa.ForeignKey("service_areas.code", ondelete="RESTRICT"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("move_rides", "dropoff_area_code")
    op.drop_column("move_rides", "pickup_area_code")
