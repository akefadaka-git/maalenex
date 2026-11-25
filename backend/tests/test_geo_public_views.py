"""A3.4 database privilege and public-view contract checks."""
import os

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_GEO_PUBLIC_VIEWS_INTEGRATION") != "1",
    reason="requires disposable PostGIS database with migrations applied",
)


def test_public_reader_is_non_login_and_only_has_sanitized_view_access(db_session):
    role = db_session.execute(text("""
        SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole
        FROM pg_roles WHERE rolname = 'maalenex_geo_public_reader'
    """)).one()
    assert tuple(role) == (False, False, False, False)

    schemas = db_session.execute(text("""
        SELECT has_schema_privilege(
            'maalenex_geo_public_reader', 'geo_public', 'USAGE'
        ), has_schema_privilege(
            'maalenex_geo_public_reader', 'geo', 'USAGE'
        )
    """)).one()
    assert tuple(schemas) == (True, False)

    views = [
        "locations", "terminals", "routes", "route_stops", "boundaries", "roads"
    ]
    for view in views:
        assert db_session.execute(text("""
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
        assert not db_session.execute(text("""
            SELECT has_table_privilege(
                'maalenex_geo_public_reader', :relation, 'SELECT'
            )
        """), {"relation": relation}).scalar_one()


def test_public_view_columns_exclude_tenant_and_operational_identifiers(db_session):
    columns = db_session.execute(text("""
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


def test_internal_reader_has_no_a3_4_access_grants(db_session):
    role = db_session.execute(text("""
        SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole
        FROM pg_roles WHERE rolname = 'maalenex_geo_internal_reader'
    """)).one()
    assert tuple(role) == (False, False, False, False)
    assert not db_session.execute(text("""
        SELECT has_schema_privilege(
            'maalenex_geo_internal_reader', 'geo_internal', 'USAGE'
        )
    """)).scalar_one()
    assert not db_session.execute(text("""
        SELECT has_table_privilege(
            'maalenex_geo_internal_reader',
            'geo_internal.vehicle_positions', 'SELECT'
        )
    """)).scalar_one()
