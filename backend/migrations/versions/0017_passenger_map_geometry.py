"""Add verified location coordinates and published route geometry.

Revision ID: 0017_passenger_map_geometry
Revises: 0016_fleet_compliance
"""
from alembic import op
import sqlalchemy as sa

revision = "0017_passenger_map_geometry"
down_revision = "0016_fleet_compliance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("locations", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("locations", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column("locations", sa.Column("coordinate_source", sa.String(length=40), nullable=True))
    op.add_column("routes", sa.Column("geometry", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("routes", "geometry")
    op.drop_column("locations", "coordinate_source")
    op.drop_column("locations", "longitude")
    op.drop_column("locations", "latitude")
