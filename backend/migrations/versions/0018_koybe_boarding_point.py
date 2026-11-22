"""Register the operator-confirmed Koybe passenger boarding point.

Revision ID: 0018_koybe_boarding_point
Revises: 0017_passenger_map_geometry
"""
from uuid import UUID, uuid5, NAMESPACE_URL

from alembic import op
import sqlalchemy as sa

revision = "0018_koybe_boarding_point"
down_revision = "0017_passenger_map_geometry"
branch_labels = None
depends_on = None

KOYBE_LOCATION_ID = UUID("bdb2e810-3f70-5f53-9f15-13d6c7f04e11")
KOYBE_TERMINAL_ID = UUID("e7218c83-89c8-5b35-99d4-37bb55a1c61e")
KOYBE_LATITUDE = 5.7678630
KOYBE_LONGITUDE = 36.7985890
COORDINATE_SOURCE = "operator_confirmed_terminal_pin"
TERMINAL_NAME = "Koybe Passenger Boarding Terminal"


def upgrade() -> None:
    bind = op.get_bind()
    locations = bind.execute(
        sa.text("SELECT id FROM locations WHERE lower(trim(name)) = 'koybe' ORDER BY id")
    ).all()
    if len(locations) > 1:
        raise RuntimeError(
            "Cannot register Koybe boarding point: multiple Koybe location records exist; reconcile them first."
        )

    if locations:
        location_id = locations[0][0]
        bind.execute(
            sa.text(
                "UPDATE locations SET latitude = :latitude, longitude = :longitude, "
                "coordinate_source = :source WHERE id = :location_id"
            ),
            {
                "latitude": KOYBE_LATITUDE,
                "longitude": KOYBE_LONGITUDE,
                "source": COORDINATE_SOURCE,
                "location_id": location_id,
            },
        )
    else:
        location_id = KOYBE_LOCATION_ID
        bind.execute(
            sa.text(
                "INSERT INTO locations "
                "(id, name, location_type, status, latitude, longitude, coordinate_source) "
                "VALUES (:id, 'Koybe', 'town', 'draft', :latitude, :longitude, :source)"
            ),
            {
                "id": location_id,
                "latitude": KOYBE_LATITUDE,
                "longitude": KOYBE_LONGITUDE,
                "source": COORDINATE_SOURCE,
            },
        )

    terminals = bind.execute(
        sa.text(
            "SELECT id FROM terminals WHERE location_id = :location_id "
            "AND lower(trim(name)) = lower(:terminal_name) ORDER BY id"
        ),
        {"location_id": location_id, "terminal_name": TERMINAL_NAME},
    ).all()
    if len(terminals) > 1:
        raise RuntimeError(
            "Cannot register Koybe boarding point: duplicate Koybe passenger terminal records exist."
        )
    if not terminals:
        bind.execute(
            sa.text(
                "INSERT INTO terminals (id, location_id, name, status) "
                "VALUES (:id, :location_id, :name, 'draft')"
            ),
            {
                "id": KOYBE_TERMINAL_ID,
                "location_id": location_id,
                "name": TERMINAL_NAME,
            },
        )


def downgrade() -> None:
    # Preserve the authoritative coordinates and terminal record once registered.
    # Reverting schema migration 0017 remains responsible for removing coordinate columns.
    pass
