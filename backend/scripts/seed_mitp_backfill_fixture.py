"""Seed deterministic synthetic legacy MITP rows for migration CI only.

This script is used only against the disposable PostgreSQL service in CI.
It creates no production or real-person/device data.
"""
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import create_engine, text

from app.core.config import settings


ORG_A = UUID("a3300000-0000-4000-8000-000000000001")
ORG_B = UUID("a3300000-0000-4000-8000-000000000002")
VEHICLE_A = UUID("a3300000-0000-4000-8000-000000000011")
VEHICLE_B = UUID("a3300000-0000-4000-8000-000000000012")
DEVICE_VALID = UUID("a3300000-0000-4000-8000-000000000021")
DEVICE_UNASSIGNED = UUID("a3300000-0000-4000-8000-000000000022")
DEVICE_CROSS_TENANT = UUID("a3300000-0000-4000-8000-000000000023")
ASSIGNMENT_VALID = UUID("a3300000-0000-4000-8000-000000000031")
ASSIGNMENT_CROSS_A = UUID("a3300000-0000-4000-8000-000000000032")
ASSIGNMENT_CROSS_B = UUID("a3300000-0000-4000-8000-000000000033")
TELEMETRY_VALID = UUID("a3300000-0000-4000-8000-000000000041")
TELEMETRY_MISMATCH = UUID("a3300000-0000-4000-8000-000000000042")
TELEMETRY_CROSS = UUID("a3300000-0000-4000-8000-000000000043")


def main() -> None:
    now = datetime.now(UTC)
    engine = create_engine(settings.database_url)
    with engine.begin() as connection:
        connection.execute(text("""
            INSERT INTO organizations (id, organization_type, display_name, status)
            VALUES
              (:org_a, 'operator', 'Synthetic operator A', 'active'),
              (:org_b, 'operator', 'Synthetic operator B', 'active')
        """), {"org_a": ORG_A, "org_b": ORG_B})
        connection.execute(text("""
            INSERT INTO vehicles (id, organization_id, vehicle_reference, status, review_status)
            VALUES
              (:vehicle_a, :org_a, 'SYNTH-A3301', 'active', 'approved'),
              (:vehicle_b, :org_b, 'SYNTH-A3302', 'active', 'approved')
        """), {
            "vehicle_a": VEHICLE_A, "vehicle_b": VEHICLE_B,
            "org_a": ORG_A, "org_b": ORG_B,
        })
        connection.execute(text("""
            INSERT INTO tracking_devices (
                id, device_identifier, credential_ciphertext, credential_version,
                status, last_sequence, created_at
            ) VALUES
              (:valid, 'SIM-A330-VALID', 'synthetic-ciphertext-valid', 1, 'active', 3, :now),
              (:unassigned, 'SIM-A330-UNASSIGNED', 'synthetic-ciphertext-unassigned', 1, 'pending', 0, :now),
              (:cross, 'SIM-A330-CROSS', 'synthetic-ciphertext-cross', 1, 'active', 2, :now)
        """), {
            "valid": DEVICE_VALID, "unassigned": DEVICE_UNASSIGNED,
            "cross": DEVICE_CROSS_TENANT, "now": now,
        })
        connection.execute(text("""
            INSERT INTO vehicle_device_assignments (
                id, device_id, vehicle_id, assigned_at, unassigned_at
            ) VALUES
              (:valid_assignment, :valid_device, :vehicle_a, :start, NULL),
              (:cross_a, :cross_device, :vehicle_a, :start, :middle),
              (:cross_b, :cross_device, :vehicle_b, :middle, NULL)
        """), {
            "valid_assignment": ASSIGNMENT_VALID, "valid_device": DEVICE_VALID,
            "cross_a": ASSIGNMENT_CROSS_A, "cross_b": ASSIGNMENT_CROSS_B,
            "cross_device": DEVICE_CROSS_TENANT, "vehicle_a": VEHICLE_A,
            "vehicle_b": VEHICLE_B, "start": now - timedelta(days=2),
            "middle": now - timedelta(days=1),
        })
        connection.execute(text("""
            INSERT INTO vehicle_telemetry (
                id, device_id, vehicle_id, sequence, recorded_at, received_at,
                latitude, longitude, speed_kph, heading_degrees, accuracy_meters,
                is_synthetic
            ) VALUES
              (:valid_id, :valid_device, :vehicle_a, 1, :valid_time, :now,
               5.7678630, 36.7985890, 22.5, 45.0, 5.0, true),
              (:mismatch_id, :valid_device, :vehicle_b, 2, :mismatch_time, :now,
               5.7680000, 36.7990000, 18.0, 50.0, 6.0, true),
              (:cross_id, :cross_device, :vehicle_b, 1, :cross_time, :now,
               5.7690000, 36.8000000, 15.0, 60.0, 7.0, true)
        """), {
            "valid_id": TELEMETRY_VALID, "mismatch_id": TELEMETRY_MISMATCH,
            "cross_id": TELEMETRY_CROSS, "valid_device": DEVICE_VALID,
            "cross_device": DEVICE_CROSS_TENANT, "vehicle_a": VEHICLE_A,
            "vehicle_b": VEHICLE_B, "valid_time": now - timedelta(minutes=10),
            "mismatch_time": now - timedelta(minutes=5),
            "cross_time": now - timedelta(minutes=30), "now": now,
        })
    engine.dispose()


if __name__ == "__main__":
    main()
