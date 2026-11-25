import os

import pytest
from sqlalchemy import create_engine, text

from app.core.config import settings


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_GEO_SCHEMA_INTEGRATION") != "1",
    reason="Requires the isolated PostGIS integration database after Alembic upgrade.",
)


def test_postgis_extension_and_canonical_geo_tables_exist() -> None:
    engine = create_engine(settings.database_url)
    expected = {
        "data_sources",
        "locations",
        "terminals",
        "routes",
        "route_stops",
        "route_versions",
        "boundaries",
        "roads",
        "devices",
        "device_vehicle_assignments",
        "vehicle_positions",
        "publications",
    }
    with engine.connect() as connection:
        installed = connection.scalar(
            text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
        )
        assert installed is True
        tables = set(connection.scalars(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'geo' AND table_type = 'BASE TABLE'
        """)))
        assert expected <= tables
    engine.dispose()


def test_canonical_geometry_columns_use_epsg_4326() -> None:
    engine = create_engine(settings.database_url)
    expected = {
        ("locations", "geom", "POINT"),
        ("terminals", "geom", "POINT"),
        ("routes", "geom", "MULTILINESTRING"),
        ("route_stops", "geom", "POINT"),
        ("route_versions", "geom", "MULTILINESTRING"),
        ("boundaries", "geom", "MULTIPOLYGON"),
        ("roads", "geom", "MULTILINESTRING"),
        ("vehicle_positions", "geom", "POINT"),
    }
    with engine.connect() as connection:
        actual = {
            (row[0], row[1], row[2])
            for row in connection.execute(text("""
                SELECT f_table_name, f_geometry_column, type
                FROM public.geometry_columns
                WHERE f_table_schema = 'geo' AND srid = 4326
            """))
        }
        assert expected <= actual
        source_nullable = connection.scalar(text("""
            SELECT is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'geo'
              AND table_name = 'vehicle_positions'
              AND column_name = 'source_id'
        """))
        assert source_nullable == "NO"
    engine.dispose()


def test_tracking_foreign_keys_bind_devices_and_vehicles_to_tenant() -> None:
    engine = create_engine(settings.database_url)
    expected = {
        "fk_geo_assignment_device_tenant",
        "fk_geo_assignment_vehicle_tenant",
        "fk_geo_position_device_tenant",
        "fk_geo_position_vehicle_tenant",
        "vehicle_positions_source_id_fkey",
    }
    with engine.connect() as connection:
        actual = set(connection.scalars(text("""
            SELECT conname
            FROM pg_constraint
            WHERE connamespace = 'geo'::regnamespace
        """)))
        assert expected <= actual
    engine.dispose()
