"""A3.7 negative tests for tenant isolation and public publication leakage."""
import os
from uuid import uuid4

from app.core.config import settings
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_GEO_LEAKAGE_INTEGRATION") != "1",
    reason="requires disposable PostGIS database with A3.5 migrations applied",
)


def _tenant_catalog_fixture(connection, organization_id):
    connection.execute(text("""
        INSERT INTO public.organizations (id, organization_type, display_name, status)
        VALUES (:org, 'operator', 'A3.7 synthetic tenant', 'active')
    """), {"org": organization_id})
    source_id, origin_id, destination_id, route_id = (uuid4() for _ in range(4))
    connection.execute(text("""
        INSERT INTO geo.data_sources (
            id, organization_id, provider, source_name, license_identifier,
            license_name, attribution_text, source_srid, collected_at,
            verification_status, verified_at, license_review_status,
            license_reviewed_at, license_reviewed_by, responsible_actor_type,
            responsible_actor_id, publication_eligible
        ) VALUES (
            :source, :org, 'A3.7 synthetic', 'Tenant fixture',
            'INTERNAL_TEST', 'Synthetic only', 'No external data',
            4326, now(), 'verified', now(), 'approved', now(),
            'a3.7-ci-reviewer', 'test', 'a3.7-test', true
        )
    """), {"source": source_id, "org": organization_id})
    for location_id, name, lon in (
        (origin_id, "Tenant origin", 37.0),
        (destination_id, "Tenant destination", 37.1),
    ):
        connection.execute(text("""
            INSERT INTO geo.locations (
                id, organization_id, name, location_type, status, geom,
                source_id, publication_eligible
            ) VALUES (
                :id, :org, :name, 'boarding_point', 'published',
                ST_SetSRID(ST_MakePoint(:lon, 6.0), 4326), :source, true
            )
        """), {
            "id": location_id, "org": organization_id, "name": name,
            "lon": lon, "source": source_id,
        })
        connection.execute(text("""
            INSERT INTO geo.publications (
                organization_id, entity_type, entity_id, source_id, status
            ) VALUES (:org, 'location', :entity, :source, 'published')
        """), {"org": organization_id, "entity": location_id, "source": source_id})
    connection.execute(text("""
        INSERT INTO geo.routes (
            id, organization_id, code, origin_location_id,
            destination_location_id, geom, status, source_id,
            publication_eligible
        ) VALUES (
            :route, :org, :code, :origin, :destination,
            ST_GeomFromText('MULTILINESTRING((37 6, 37.1 6))', 4326),
            'published', :source, true
        )
    """), {
        "route": route_id, "org": organization_id,
        "code": f"A37-{organization_id}", "origin": origin_id,
        "destination": destination_id, "source": source_id,
    })
    connection.execute(text("""
        INSERT INTO geo.publications (
            organization_id, entity_type, entity_id, source_id, status
        ) VALUES (:org, 'route', :route, :source, 'published')
    """), {"org": organization_id, "route": route_id, "source": source_id})
    return {
        "source": source_id, "origin": origin_id,
        "destination": destination_id, "route": route_id,
    }


def test_catalog_manager_cannot_read_other_tenant_locations_routes_or_publications():
    engine = create_engine(settings.database_url)
    org_a, org_b = uuid4(), uuid4()
    fixtures = {}
    try:
        with engine.begin() as connection:
            fixtures[org_a] = _tenant_catalog_fixture(connection, org_a)
            fixtures[org_b] = _tenant_catalog_fixture(connection, org_b)

        with engine.begin() as connection:
            connection.execute(text("SET LOCAL ROLE maalenex_geo_catalog_manager"))
            connection.execute(text("""
                SELECT pg_catalog.set_config(
                    'app.current_organization_id', :org, true
                )
            """), {"org": str(org_a)})
            for table, key in (
                ("geo.locations", "origin"),
                ("geo.routes", "route"),
            ):
                visible = set(connection.scalars(text(f"SELECT id FROM {table}")))
                assert fixtures[org_a][key] in visible
                assert fixtures[org_b][key] not in visible
            visible_publications = set(connection.scalars(text(
                "SELECT entity_id FROM geo.publications"
            )))
            assert fixtures[org_a]["origin"] in visible_publications
            assert fixtures[org_a]["route"] in visible_publications
            assert fixtures[org_b]["origin"] not in visible_publications
            assert fixtures[org_b]["route"] not in visible_publications

        with engine.begin() as connection:
            connection.execute(text("SET LOCAL ROLE maalenex_geo_catalog_manager"))
            assert connection.execute(text("SELECT count(*) FROM geo.locations")).scalar_one() == 0
            assert connection.execute(text("SELECT count(*) FROM geo.routes")).scalar_one() == 0
            assert connection.execute(text("SELECT count(*) FROM geo.publications")).scalar_one() == 0
            connection.execute(text("""
                SELECT pg_catalog.set_config(
                    'app.current_organization_id', 'malformed-tenant', true
                )
            """))
            assert connection.execute(text("SELECT count(*) FROM geo.locations")).scalar_one() == 0
            assert connection.execute(text("SELECT count(*) FROM geo.routes")).scalar_one() == 0
            assert connection.execute(text("SELECT count(*) FROM geo.publications")).scalar_one() == 0
    finally:
        engine.dispose()


def test_public_reader_sees_only_verified_published_and_allowlisted_features():
    engine = create_engine(settings.database_url)
    public_id, private_id = uuid4(), uuid4()
    source_public, source_private = uuid4(), uuid4()
    try:
        with engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO geo.data_sources (
                    id, provider, source_name, license_identifier, license_name,
                    attribution_text, source_srid, collected_at, verification_status,
                    verified_at, license_review_status, license_reviewed_at,
                    license_reviewed_by, responsible_actor_type, responsible_actor_id,
                    publication_eligible
                ) VALUES (
                    :source, 'A3.7 synthetic', 'Approved public fixture',
                    'INTERNAL_TEST', 'Synthetic only', 'No external data',
                    4326, now(), 'verified', now(), 'approved', now(),
                    'a3.7-ci-reviewer', 'test', 'a3.7-public', true
                )
            """), {"source": source_public})
            connection.execute(text("""
                INSERT INTO geo.locations (
                    id, name, location_type, status, geom, source_id,
                    publication_eligible
                ) VALUES (
                    :id, 'A3.7 approved public point', 'boarding_point',
                    'published', ST_SetSRID(ST_MakePoint(0, 0), 4326),
                    :source, true
                )
            """), {"id": public_id, "source": source_public})
            connection.execute(text("""
                INSERT INTO geo.publications (entity_type, entity_id, source_id, status)
                VALUES ('location', :id, :source, 'published')
            """), {"id": public_id, "source": source_public})

            connection.execute(text("""
                INSERT INTO geo.data_sources (
                    id, provider, source_name, license_identifier, license_name,
                    attribution_text, source_srid, collected_at, verification_status,
                    responsible_actor_type, responsible_actor_id, publication_eligible
                ) VALUES (
                    :source, 'A3.7 synthetic', 'Unverified private fixture',
                    'INTERNAL_TEST', 'Synthetic only', 'No external data',
                    4326, now(), 'unverified', 'test', 'a3.7-private', false
                )
            """), {"source": source_private})
            connection.execute(text("""
                INSERT INTO geo.locations (
                    id, name, location_type, status, geom, source_id,
                    publication_eligible
                ) VALUES (
                    :id, 'PRIVATE-DO-NOT-LEAK', 'private_business',
                    'published', ST_SetSRID(ST_MakePoint(0, 0), 4326),
                    :source, true
                )
            """), {"id": private_id, "source": source_private})
            connection.execute(text("""
                INSERT INTO geo.publications (entity_type, entity_id, source_id, status)
                VALUES ('location', :id, :source, 'published')
            """), {"id": private_id, "source": source_private})

        with engine.begin() as connection:
            connection.execute(text("SET LOCAL ROLE maalenex_geo_public_reader"))
            visible = set(connection.scalars(text("SELECT id FROM geo_public.locations")))
            assert public_id in visible
            assert private_id not in visible
            assert connection.execute(text("""
                SELECT count(*) FROM geo_public.locations
                WHERE name = 'PRIVATE-DO-NOT-LEAK'
            """)).scalar_one() == 0
            for relation in (
                "geo.locations", "geo.routes", "geo.publications",
                "geo.devices", "geo.vehicle_positions", "geo_audit.events",
            ):
                with pytest.raises(DBAPIError), connection.begin_nested():
                    connection.execute(text(f"SELECT * FROM {relation} LIMIT 1"))
    finally:
        engine.dispose()
