"""A3.8 provenance evidence and license-publication gate integration tests."""
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from app.core.config import settings


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_GEO_PROVENANCE_INTEGRATION") != "1",
    reason="requires disposable PostGIS database after A3.8 migrations",
)


def _source(connection, *, eligible=False):
    source_id = uuid4()
    connection.execute(text("""
        INSERT INTO geo.data_sources (
            id, provider, source_name, license_identifier, license_name,
            attribution_text, source_srid, collected_at, verification_status,
            verified_at, verified_by, license_review_status, license_reviewed_at,
            license_reviewed_by, responsible_actor_type, responsible_actor_id,
            publication_eligible
        ) VALUES (
            :id, 'A3.8 synthetic', 'Provenance fixture',
            'INTERNAL_TEST', 'Synthetic test terms', 'Synthetic data only',
            4326, now(), 'verified', now(),
            (SELECT id FROM public.staff_users LIMIT 1),
            'approved', now(), (SELECT id FROM public.staff_users LIMIT 1),
            'test', 'a3.8-ci', :eligible
        )
    """), {"id": source_id, "eligible": eligible})
    return source_id


def test_source_evidence_is_tenant_scoped_and_append_only():
    engine = create_engine(settings.database_url)
    source_id = uuid4()
    org_id = uuid4()
    try:
        with engine.begin() as connection:
            connection.execute(text("""
                INSERT INTO public.organizations (id, organization_type, display_name, status)
                VALUES (:id, 'operator', 'A3.8 synthetic tenant', 'active')
            """), {"id": org_id})
            connection.execute(text("""
                INSERT INTO geo.data_sources (
                    id, organization_id, provider, source_name, license_identifier,
                    license_name, attribution_text, source_srid, collected_at,
                    responsible_actor_type, responsible_actor_id
                ) VALUES (
                    :id, :org, 'A3.8', 'Tenant evidence fixture',
                    'INTERNAL_TEST', 'Synthetic', 'No external data',
                    4326, now(), 'test', 'a3.8-ci'
                )
            """), {"id": source_id, "org": org_id})
            evidence_id = connection.execute(text("""
                INSERT INTO geo.source_evidence (
                    source_id, evidence_type, evidence_checksum_sha256, evidence_note
                ) VALUES (
                    :source, 'license_document', repeat('a', 64), 'Synthetic fixture'
                ) RETURNING id
            """), {"source": source_id}).scalar_one()

        with engine.begin() as connection:
            connection.execute(text("SET LOCAL ROLE maalenex_geo_catalog_manager"))
            connection.execute(text("""
                SELECT pg_catalog.set_config('app.current_organization_id', :org, true)
            """), {"org": str(org_id)})
            assert connection.execute(text("""
                SELECT count(*) FROM geo.source_evidence WHERE id = :id
            """), {"id": evidence_id}).scalar_one() == 1
            with pytest.raises(DBAPIError), connection.begin_nested():
                connection.execute(text("""
                    UPDATE geo.source_evidence SET evidence_note = 'tampered' WHERE id = :id
                """), {"id": evidence_id})
    finally:
        engine.dispose()


def test_publication_eligibility_requires_independent_license_review():
    engine = create_engine(settings.database_url)
    try:
        with engine.begin() as connection:
            with pytest.raises(DBAPIError), connection.begin_nested():
                connection.execute(text("""
                    INSERT INTO geo.data_sources (
                        provider, source_name, license_identifier, license_name,
                        attribution_text, source_srid, collected_at,
                        verification_status, verified_at, verified_by,
                        responsible_actor_type, responsible_actor_id,
                        publication_eligible
                    ) VALUES (
                        'A3.8 synthetic', 'Missing license review',
                        'UNKNOWN', 'Unknown terms', 'Synthetic attribution',
                        4326, now(), 'verified', now(),
                        (SELECT id FROM public.staff_users LIMIT 1),
                        'test', 'a3.8-ci', true
                    )
                """))
    finally:
        engine.dispose()


def test_source_evidence_rejects_malformed_sha256():
    engine = create_engine(settings.database_url)
    try:
        with engine.begin() as connection:
            source_id = _source(connection)
            with pytest.raises(DBAPIError), connection.begin_nested():
                connection.execute(text("""
                    INSERT INTO geo.source_evidence (
                        source_id, evidence_type, evidence_checksum_sha256
                    ) VALUES (:source, 'checksum_record', 'not-a-sha256')
                """), {"source": source_id})
    finally:
        engine.dispose()
