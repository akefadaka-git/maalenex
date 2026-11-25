"""PostgreSQL integration tests for A3.5 tenant RLS."""
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from app.core.config import settings


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_GEO_RLS_INTEGRATION") != "1",
    reason="requires disposable PostGIS database with A3.5 migrations applied",
)


def _insert_tenant_fixture(connection, organization_id, vehicle_id, device_id, source_id, position_id):
    connection.execute(text("""
        INSERT INTO public.organizations (id, organization_type, display_name, status)
        VALUES (:org, 'operator', 'A3.5 synthetic tenant', 'active')
    """), {"org": organization_id})
    connection.execute(text("""
        INSERT INTO public.vehicles
            (id, organization_id, vehicle_reference, status, review_status)
        VALUES (:vehicle, :org, :reference, 'active', 'approved')
    """), {"vehicle": vehicle_id, "org": organization_id, "reference": str(vehicle_id)})
    connection.execute(text("""
        INSERT INTO geo.data_sources (
            id, organization_id, provider, source_name, license_identifier,
            license_name, attribution_text, source_srid, collected_at,
            verification_status, responsible_actor_type, responsible_actor_id,
            publication_eligible
        ) VALUES (
            :source, :org, 'A3.5 synthetic fixture', 'Synthetic fixture',
            'INTERNAL_TEST', 'Synthetic test only', 'No external data',
            4326, now(), 'unverified', 'test', 'a3.5-test', false
        )
    """), {"source": source_id, "org": organization_id})
    connection.execute(text("""
        INSERT INTO geo.devices (
            id, organization_id, device_identifier, credential_ciphertext,
            credential_version, status, last_sequence
        ) VALUES (
            :device, :org, :identifier, 'synthetic-ciphertext',
            1, 'active', 1
        )
    """), {"device": device_id, "org": organization_id, "identifier": str(device_id)})
    connection.execute(text("""
        INSERT INTO geo.vehicle_positions (
            id, organization_id, device_id, vehicle_id, source_id, sequence,
            recorded_at, received_at, geom, speed_kph, heading_degrees,
            accuracy_meters, is_synthetic
        ) VALUES (
            :position, :org, :device, :vehicle, :source, 1,
            now(), now(), ST_SetSRID(ST_MakePoint(37.0, 6.0), 4326),
            0, 0, 5, true
        )
    """), {
        "position": position_id, "org": organization_id, "device": device_id,
        "vehicle": vehicle_id, "source": source_id,
    })


def test_internal_reader_is_fail_closed_and_tenant_scoped():
    engine = create_engine(settings.database_url)
    org_a, org_b = uuid4(), uuid4()
    fixtures = []
    try:
        with engine.begin() as connection:
            for org in (org_a, org_b):
                values = (org, uuid4(), uuid4(), uuid4(), uuid4())
                _insert_tenant_fixture(connection, *values)
                fixtures.append(values)

        with engine.begin() as connection:
            connection.execute(text("SET LOCAL ROLE maalenex_geo_internal_reader"))
            assert connection.execute(text("""
                SELECT count(*) FROM geo_internal.vehicle_positions
            """)).scalar_one() == 0
            assert connection.execute(text("""
                SELECT count(*) FROM geo.vehicle_positions
            """)).scalar_one() == 0
            connection.execute(text("""
                SELECT pg_catalog.set_config(
                    'app.current_organization_id', 'not-a-uuid', true
                )
            """))
            assert connection.execute(text("""
                SELECT count(*) FROM geo_internal.vehicle_positions
            """)).scalar_one() == 0

        with engine.begin() as connection:
            connection.execute(text("SET LOCAL ROLE maalenex_geo_internal_reader"))
            connection.execute(text("""
                SELECT pg_catalog.set_config(
                    'app.current_organization_id', :org, true
                )
            """), {"org": str(org_a)})
            view_ids = set(connection.scalars(text("""
                SELECT id FROM geo_internal.vehicle_positions
            """)))
            raw_ids = set(connection.scalars(text("""
                SELECT id FROM geo.vehicle_positions
            """)))
            assert view_ids == {fixtures[0][4]}
            assert raw_ids == {fixtures[0][4]}
            assert fixtures[1][4] not in view_ids
    finally:
        engine.dispose()


def test_internal_reader_cannot_read_sensitive_device_or_quarantine_tables():
    engine = create_engine(settings.database_url)
    try:
        for relation in (
            "geo.devices", "geo.device_vehicle_assignments",
            "geo.legacy_tracking_quarantine",
        ):
            with engine.begin() as connection:
                connection.execute(text("SET LOCAL ROLE maalenex_geo_internal_reader"))
                with pytest.raises(Exception):
                    connection.execute(text(f"SELECT * FROM {relation} LIMIT 1"))
    finally:
        engine.dispose()

def test_tenant_manager_cannot_read_or_write_another_organizations_devices():
    engine = create_engine(settings.database_url)
    org_a, org_b = uuid4(), uuid4()
    fixtures = []
    try:
        with engine.begin() as connection:
            for org in (org_a, org_b):
                values = (org, uuid4(), uuid4(), uuid4(), uuid4())
                _insert_tenant_fixture(connection, *values)
                fixtures.append(values)

        with engine.begin() as connection:
            connection.execute(text("SET LOCAL ROLE maalenex_geo_tenant_manager"))
            connection.execute(text("""
                SELECT pg_catalog.set_config(
                    'app.current_organization_id', :org, true
                )
            """), {"org": str(org_a)})
            visible = set(connection.scalars(text("SELECT id FROM geo.devices")))
            assert visible == {fixtures[0][2]}
            assert fixtures[1][2] not in visible

        with pytest.raises(DBAPIError):
            with engine.begin() as connection:
                connection.execute(text("SET LOCAL ROLE maalenex_geo_tenant_manager"))
                connection.execute(text("""
                    SELECT pg_catalog.set_config(
                        'app.current_organization_id', :org, true
                    )
                """), {"org": str(org_a)})
                connection.execute(text("""
                    INSERT INTO geo.devices (
                        id, organization_id, device_identifier, credential_ciphertext,
                        credential_version, status, last_sequence
                    ) VALUES (
                        :device, :org_b, :identifier, 'synthetic-ciphertext',
                        1, 'active', 0
                    )
                """), {
                    "device": uuid4(), "org_b": org_b, "identifier": str(uuid4()),
                })
    finally:
        engine.dispose()


def test_catalog_manager_cannot_bind_tenant_location_to_other_tenant_source():
    engine = create_engine(settings.database_url)
    org_a, org_b = uuid4(), uuid4()
    fixtures = []
    try:
        with engine.begin() as connection:
            for org in (org_a, org_b):
                values = (org, uuid4(), uuid4(), uuid4(), uuid4())
                _insert_tenant_fixture(connection, *values)
                fixtures.append(values)

        with pytest.raises(DBAPIError):
            with engine.begin() as connection:
                connection.execute(text("SET LOCAL ROLE maalenex_geo_catalog_manager"))
                connection.execute(text("""
                    SELECT pg_catalog.set_config(
                        'app.current_organization_id', :org, true
                    )
                """), {"org": str(org_a)})
                connection.execute(text("""
                    INSERT INTO geo.locations (
                        id, organization_id, name, location_type, status,
                        source_id, publication_eligible
                    ) VALUES (
                        :location, :org_a, 'Cross-tenant source test',
                        'boarding_point', 'draft', :source_b, false
                    )
                """), {
                    "location": uuid4(), "org_a": org_a, "source_b": fixtures[1][3],
                })
    finally:
        engine.dispose()


def test_rls_is_enabled_on_all_canonical_geo_tables():
    engine = create_engine(settings.database_url)
    expected = {
        "data_sources", "locations", "terminals", "routes", "route_stops",
        "route_versions", "boundaries", "roads", "devices",
        "device_vehicle_assignments", "vehicle_positions", "publications",
        "legacy_tracking_quarantine",
    }
    try:
        with engine.connect() as connection:
            enabled = set(connection.scalars(text("""
                SELECT c.relname
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'geo'
                  AND c.relkind = 'r'
                  AND c.relrowsecurity
            """)))
        assert expected <= enabled
    finally:
        engine.dispose()
