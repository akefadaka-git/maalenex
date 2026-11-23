import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.domains.fleet.models import Vehicle
from app.domains.organizations.models import Organization
from app.domains.tracking.models import TrackingDevice, VehicleDeviceAssignment
from app.domains.tracking.schemas import TelemetryPayload
from app.domains.tracking.security import encrypt_credential, sign_telemetry
from app.domains.tracking.service import TelemetryRejected, ingest_telemetry


def _tracking_session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        Organization.__table__,
        Vehicle.__table__,
        TrackingDevice.__table__,
        VehicleDeviceAssignment.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    return engine


def test_ingestion_binds_telemetry_to_the_registered_vehicle_and_rejects_replay(monkeypatch):
    from sqlalchemy.orm import sessionmaker

    key = Fernet.generate_key().decode("ascii")
    monkeypatch.setattr(settings, "mitp_device_encryption_key", key)
    engine = _tracking_session()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    now = datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc)
    credential = "synthetic-device-credential-value-0001"
    with SessionLocal() as db:
        organization = Organization(display_name="Synthetic operator", status="approved")
        db.add(organization)
        db.flush()
        vehicle = Vehicle(
            organization_id=organization.id, vehicle_reference="SIM-VEHICLE-01",
            status="active", review_status="approved",
        )
        device = TrackingDevice(
            device_identifier="SIM-GPS-0001",
            credential_ciphertext=encrypt_credential(credential, key),
            status="active", last_sequence=0,
        )
        db.add_all([vehicle, device])
        db.flush()
        db.add(VehicleDeviceAssignment(device_id=device.id, vehicle_id=vehicle.id))
        db.commit()

        body = json.dumps({
            "sequence": 1, "recorded_at": now.isoformat(),
            "latitude": 6.25, "longitude": 36.88, "speed_kph": 20,
            "heading_degrees": 90, "accuracy_meters": 5,
        }, separators=(",", ":")).encode()
        payload = TelemetryPayload.model_validate_json(body)
        timestamp = str(int(now.timestamp()))
        signature = sign_telemetry(credential, timestamp, body)
        accepted = ingest_telemetry(
            db, device_identifier="SIM-GPS-0001", request_timestamp=timestamp,
            request_body=body, signature=signature, payload=payload, now=now,
        )
        db.commit()
        assert accepted.vehicle_id == vehicle.id
        assert accepted.sequence == 1
        assert device.last_sequence == 1

        with pytest.raises(TelemetryRejected, match="sequence_replayed_or_out_of_order"):
            ingest_telemetry(
                db, device_identifier="SIM-GPS-0001", request_timestamp=timestamp,
                request_body=body, signature=signature, payload=payload, now=now,
            )
    engine.dispose()


def test_ingestion_rejects_tampered_body_signature(monkeypatch):
    from sqlalchemy.orm import sessionmaker

    key = Fernet.generate_key().decode("ascii")
    monkeypatch.setattr(settings, "mitp_device_encryption_key", key)
    engine = _tracking_session()
    SessionLocal = sessionmaker(bind=engine)
    now = datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc)
    credential = "synthetic-device-credential-value-0001"
    with SessionLocal() as db:
        organization = Organization(display_name="Synthetic operator", status="approved")
        db.add(organization)
        db.flush()
        vehicle = Vehicle(
            organization_id=organization.id, vehicle_reference="SIM-VEHICLE-02",
            status="active", review_status="approved",
        )
        device = TrackingDevice(
            device_identifier="SIM-GPS-0002",
            credential_ciphertext=encrypt_credential(credential, key),
            status="active", last_sequence=0,
        )
        db.add_all([vehicle, device])
        db.flush()
        db.add(VehicleDeviceAssignment(device_id=device.id, vehicle_id=vehicle.id))
        db.commit()

        body = json.dumps({
            "sequence": 1, "recorded_at": now.isoformat(),
            "latitude": 6.25, "longitude": 36.88, "speed_kph": 20,
            "heading_degrees": 90, "accuracy_meters": 5,
        }, separators=(",", ":")).encode()
        payload = TelemetryPayload.model_validate_json(body)
        timestamp = str(int(now.timestamp()))
        signature = sign_telemetry(credential, timestamp, body)
        with pytest.raises(TelemetryRejected, match="invalid_device_signature"):
            ingest_telemetry(
                db, device_identifier="SIM-GPS-0002", request_timestamp=timestamp,
                request_body=body + b" ", signature=signature, payload=payload, now=now,
            )
    engine.dispose()
