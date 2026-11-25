"""A3.4 database privilege and public-view contract checks."""
import os

import pytest
from sqlalchemy import create_engine, text

from app.core.config import settings


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_GEO_PUBLIC_VIEWS_INTEGRATION") != "1",
    reason="requires disposable PostGIS database with migrations applied",
)


def test_public_reader_is_non_login_and_only_has_sanitized_view_access():
    engine = create_engine(settings.database_url)
    try:
        with engine.connect() as connection:
            role = connection.execute(text("""
                SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole
                FROM pg_roles WHERE rolname = 'maalenex_geo_public_reader'
            """)).one()
            assert tuple(role) == (False, False, False, False, False, False)

            schemas = connection.execute(text("""
                SELECT has_schema_privilege(
                    'maalenex_geo_public_reader', 'geo_public', 'USAGE'
                ), has_schema_privilege(
                    'maalenex_geo_public_reader', 'geo', 'USAGE'
                )
            """)).one()
            assert tuple(schemas) == (True, False)

            for view in (
                "locations", "terminals", "routes", "route_stops", "boundaries", "roads"
            ):
                assert connection.execute(text("""
                    SELECT has_table_privilege(
                        'maalenex_geo_public_reader', :relation, 'SELECT'
                    )
                """), {"relation": f"geo_public.{view}"}).scalar_one()

            for relation in (
                "geo.devices",
                "geo.device_vehicle_assignments",
                "geo.vehicle_positions",
                "geo.legacy_tracking_quarantine",
            ):
                assert not connection.execute(text("""
                    SELECT has_table_privilege(
                        'maalenex_geo_public_reader', :relation, 'SELECT'
                    )
                """), {"relation": relation}).scalar_one()
    finally:
        engine.dispose()


def test_public_view_columns_exclude_tenant_and_operational_identifiers():
    engine = create_engine(settings.database_url)
    try:
        with engine.connect() as connection:
            columns = connection.execute(text("""
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'geo_public'
            """)).all()
        by_view = {}
        for view, column in columns:
            by_view.setdefault(view, set()).add(column)

        assert set(by_view) == {
            "locations", "terminals", "routes", "route_stops", "boundaries", "roads"
        }
        forbidden = {
            "organization_id", "device_id", "device_identifier",
            "credential_ciphertext", "created_by", "updated_by",
            "responsible_actor_id", "attributes",
        }
        for visible_columns in by_view.values():
            assert forbidden.isdisjoint(visible_columns)
    finally:
        engine.dispose()


def test_internal_reader_has_only_position_view_and_base_table_access():
    engine = create_engine(settings.database_url)
    try:
        with engine.connect() as connection:
            role = connection.execute(text("""
                SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole,
                       rolbypassrls, rolinherit
                FROM pg_roles WHERE rolname = 'maalenex_geo_internal_reader'
            """)).one()
            assert tuple(role) == (False, False, False, False)
            assert connection.execute(text("""
                SELECT has_schema_privilege(
                    'maalenex_geo_internal_reader', 'geo_internal', 'USAGE'
                )
            """)).scalar_one()
            assert connection.execute(text("""
                SELECT has_schema_privilege(
                    'maalenex_geo_internal_reader', 'geo', 'USAGE'
                )
            """)).scalar_one()
            assert connection.execute(text("""
                SELECT has_table_privilege(
                    'maalenex_geo_internal_reader',
                    'geo_internal.vehicle_positions', 'SELECT'
                )
            """)).scalar_one()
            assert connection.execute(text("""
                SELECT has_table_privilege(
                    'maalenex_geo_internal_reader',
                    'geo.vehicle_positions', 'SELECT'
                )
            """)).scalar_one()
    finally:
        engine.dispose()

def test_geo_write_roles_are_non_login_and_cannot_bypass_rls():
    engine = create_engine(settings.database_url)
    try:
        with engine.connect() as connection:
            for role_name in (
                "maalenex_geo_tenant_manager", "maalenex_geo_catalog_manager"
            ):
                role = connection.execute(text("""
                    SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole,
                           rolbypassrls, rolinherit
                    FROM pg_roles WHERE rolname = :role_name
                """), {"role_name": role_name}).one()
                assert tuple(role) == (False, False, False, False, False, False)
    finally:
        engine.dispose()
