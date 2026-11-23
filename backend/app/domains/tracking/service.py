from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.tracking.models import TrackingDevice, VehicleDeviceAssignment, VehicleTelemetry
from app.domains.tracking.schemas import TelemetryPayload
from app.domains.tracking.security import decrypt_credential, verify_telemetry_signature


class TelemetryRejected(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def ingest_telemetry(
    db: Session,
    *,
    device_identifier: str,
    request_timestamp: str,
    request_body: bytes,
    signature: str,
    payload: TelemetryPayload,
    now: datetime | None = None,
) -> VehicleTelemetry:
    current = now or datetime.now(UTC)
    try:
        sent_at = datetime.fromtimestamp(int(request_timestamp), tz=UTC)
    except (ValueError, OverflowError, OSError):
        raise TelemetryRejected("invalid_request_timestamp")
    if abs((current - sent_at).total_seconds()) > 300:
        raise TelemetryRejected("request_timestamp_outside_window")

    device = db.scalar(
        select(TrackingDevice)
        .where(TrackingDevice.device_identifier == device_identifier)
        .with_for_update()
    )
    if device is None or device.status != "active":
        raise TelemetryRejected("device_not_active")
    if settings.mitp_encryption_key is None:
        raise TelemetryRejected("device_security_not_configured")
    try:
        raw_credential = decrypt_credential(
            device.credential_ciphertext, settings.mitp_encryption_key
        )
    except ValueError:
        raise TelemetryRejected("device_credential_unavailable")
    if not verify_telemetry_signature(
        raw_credential, request_timestamp, request_body, signature
    ):
        raise TelemetryRejected("invalid_device_signature")

    assignment = db.scalar(
        select(VehicleDeviceAssignment).where(
            VehicleDeviceAssignment.device_id == device.id,
            VehicleDeviceAssignment.unassigned_at.is_(None),
        )
    )
    if assignment is None:
        raise TelemetryRejected("device_not_assigned")
    if payload.sequence <= device.last_sequence:
        raise TelemetryRejected("sequence_replayed_or_out_of_order")
    recent_count = db.scalar(select(func.count(VehicleTelemetry.id)).where(
        VehicleTelemetry.device_id == device.id,
        VehicleTelemetry.received_at >= current - timedelta(minutes=1),
    )) or 0
    if recent_count >= 120:
        raise TelemetryRejected("device_rate_limit_exceeded")

    recorded_at = payload.recorded_at.astimezone(UTC)
    if recorded_at > current + timedelta(seconds=60):
        raise TelemetryRejected("telemetry_timestamp_in_future")
    if recorded_at < current - timedelta(hours=24):
        raise TelemetryRejected("telemetry_older_than_24_hours")

    item = VehicleTelemetry(
        device_id=device.id,
        vehicle_id=assignment.vehicle_id,
        sequence=payload.sequence,
        recorded_at=recorded_at,
        latitude=payload.latitude,
        longitude=payload.longitude,
        speed_kph=payload.speed_kph,
        heading_degrees=payload.heading_degrees,
        accuracy_meters=payload.accuracy_meters,
    )
    device.last_sequence = payload.sequence
    device.last_seen_at = current
    db.add(item)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise TelemetryRejected("duplicate_telemetry") from exc
    return item


def latest_vehicle_position(db: Session, vehicle_id: UUID) -> VehicleTelemetry | None:
    return db.scalar(
        select(VehicleTelemetry)
        .where(VehicleTelemetry.vehicle_id == vehicle_id)
        .order_by(VehicleTelemetry.recorded_at.desc(), VehicleTelemetry.sequence.desc())
        .limit(1)
    )
