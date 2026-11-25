import os

import pytest
from sqlalchemy import create_engine, text

from app.core.config import settings


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_MITP_BACKFILL_INTEGRATION") != "1",
    reason="Requires synthetic legacy rows and the completed Alembic backfill.",
)


def test_mitp_legacy_rows_are_migrated_or_quarantined_without_tenant_guessing() -> None:
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        device_counts = connection.execute(text("""
            SELECT
              (SELECT count(*) FROM public.tracking_devices) AS legacy,
              (SELECT count(*) FROM geo.devices) AS migrated,
              (SELECT count(*) FROM geo.legacy_tracking_quarantine
               WHERE source_table = 'tracking_devices') AS quarantined
        """)).mappings().one()
        assert device_counts["legacy"] == 3
        assert device_counts["migrated"] == 1
        assert device_counts["quarantined"] == 2

        assignment_counts = connection.execute(text("""
            SELECT
              (SELECT count(*) FROM public.vehicle_device_assignments) AS legacy,
              (SELECT count(*) FROM geo.device_vehicle_assignments) AS migrated,
              (SELECT count(*) FROM geo.legacy_tracking_quarantine
               WHERE source_table = 'vehicle_device_assignments') AS quarantined
        """)).mappings().one()
        assert assignment_counts["legacy"] == 3
        assert assignment_counts["migrated"] == 1
        assert assignment_counts["quarantined"] == 2

        telemetry_counts = connection.execute(text("""
            SELECT
              (SELECT count(*) FROM public.vehicle_telemetry) AS legacy,
              (SELECT count(*) FROM geo.vehicle_positions) AS migrated,
              (SELECT count(*) FROM geo.legacy_tracking_quarantine
               WHERE source_table = 'vehicle_telemetry') AS quarantined
        """)).mappings().one()
        assert telemetry_counts["legacy"] == 3
        assert telemetry_counts["migrated"] == 1
        assert telemetry_counts["quarantined"] == 2

        migrated = connection.execute(text("""
            SELECT p.id, p.organization_id, p.source_id,
                   ST_X(p.geom) AS longitude, ST_Y(p.geom) AS latitude,
                   p.is_synthetic
            FROM geo.vehicle_positions p
            WHERE p.id = 'a3300000-0000-4000-8000-000000000041'
        """)).mappings().one()
        assert str(migrated["organization_id"]) == "a3300000-0000-4000-8000-000000000001"
        assert migrated["source_id"] is not None
        assert float(migrated["longitude"]) == 36.7985890
        assert float(migrated["latitude"]) == 5.7678630
        assert migrated["is_synthetic"] is True

        reasons = set(connection.scalars(text("""
            SELECT reason FROM geo.legacy_tracking_quarantine
        """)))
        assert "no_tenant_assignment_history" in reasons
        assert "multiple_tenant_assignment_history" in reasons
        assert "device_vehicle_tenant_mismatch" in reasons
        assert "device_tenant_unresolved" in reasons

        quarantined_device = connection.execute(text("""
            SELECT payload
            FROM geo.legacy_tracking_quarantine
            WHERE source_table = 'tracking_devices'
              AND source_id = 'a3300000-0000-4000-8000-000000000022'
        """)).scalar_one()
        assert quarantined_device["credential_ciphertext_redacted"] is True
        assert "credential_ciphertext" not in quarantined_device
    engine.dispose()
