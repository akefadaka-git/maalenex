import secrets
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.fleet.models import Vehicle
from app.domains.identity.authorization import has_permission
from app.domains.identity.service import StaffContext
from app.domains.tracking.models import TrackingDevice, VehicleDeviceAssignment
from app.domains.tracking.schemas import TelemetryPayload
from app.domains.tracking.security import encrypt_credential
from app.domains.tracking.service import (
    TelemetryRejected, ingest_telemetry, latest_vehicle_position,
)
from app.routers.auth import current_staff_context, require_csrf

router = APIRouter(prefix="/tracking", tags=["vehicle-tracking"])
StaffContextDep = Annotated[StaffContext, Depends(current_staff_context)]
DatabaseSession = Annotated[Session, Depends(get_db)]


class DeviceRegistration(BaseModel):
    device_identifier: str = Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9._-]+$")


class AssignmentRequest(BaseModel):
    vehicle_id: UUID


class DeviceStatusRequest(BaseModel):
    status: str = Field(pattern=r"^(suspended|revoked)$")


def _authorize(db: Session, context: StaffContext, permission: str) -> None:
    if not has_permission(
        db, user_id=context.user.id, permission_code=permission, organization_id=None
    ):
        raise HTTPException(status_code=403, detail="Required platform tracking permission is missing.")


def _audit(db: Session, context: StaffContext, event_type: str, device_id: UUID,
           action: str, metadata: dict | None = None) -> None:
    record_event(
        db, event_type=event_type, actor_type="staff", actor_id=str(context.user.id),
        resource_type="tracking_device", resource_id=str(device_id),
        action=action, outcome="success", metadata=metadata,
    )


def _require_encryption_key() -> str:
    if settings.mitp_encryption_key is None:
        raise HTTPException(
            status_code=503,
            detail="MITP_DEVICE_ENCRYPTION_KEY must be configured before device credentials can be issued.",
        )
    try:
        encrypt_credential("validation-only-device-credential-000000", settings.mitp_encryption_key)
    except ValueError:
        raise HTTPException(status_code=503, detail="MITP_DEVICE_ENCRYPTION_KEY is invalid.")
    return settings.mitp_encryption_key


@router.get("/devices")
def list_devices(
    context: StaffContextDep,
    db: DatabaseSession,
    limit: int = 100,
) -> list[dict]:
    _authorize(db, context, "platform.tracking.read")
    devices = db.scalars(
        select(TrackingDevice).order_by(TrackingDevice.created_at.desc()).limit(max(1, min(limit, 200)))
    ).all()
    result = []
    for device in devices:
        assignment = db.scalar(select(VehicleDeviceAssignment).where(
            VehicleDeviceAssignment.device_id == device.id,
            VehicleDeviceAssignment.unassigned_at.is_(None),
        ))
        result.append({
            "id": str(device.id),
            "device_identifier": device.device_identifier,
            "status": device.status,
            "credential_version": device.credential_version,
            "last_sequence": device.last_sequence,
            "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
            "active_vehicle_id": str(assignment.vehicle_id) if assignment else None,
        })
    return result


@router.post("/devices", status_code=status.HTTP_201_CREATED)
def register_device(
    payload: DeviceRegistration, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    _authorize(db, context, "platform.tracking.manage")
    encryption_key = _require_encryption_key()
    raw_credential = secrets.token_urlsafe(48)
    device = TrackingDevice(
        device_identifier=payload.device_identifier,
        credential_ciphertext=encrypt_credential(raw_credential, encryption_key),
        status="pending",
        created_by=context.user.id,
    )
    db.add(device)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Device identifier already exists.")
    _audit(db, context, "tracking.device.registered", device.id, "register")
    db.commit()
    return {
        "id": str(device.id),
        "device_identifier": device.device_identifier,
        "status": device.status,
        "credential": raw_credential,
        "credential_display_policy": "shown_once",
    }


@router.post("/devices/{device_id}/assignments", status_code=status.HTTP_201_CREATED)
def assign_device(
    device_id: UUID, payload: AssignmentRequest, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    _authorize(db, context, "platform.tracking.manage")
    device = db.scalar(select(TrackingDevice).where(TrackingDevice.id == device_id).with_for_update())
    vehicle = db.scalar(select(Vehicle).where(Vehicle.id == payload.vehicle_id).with_for_update())
    if device is None or device.status not in {"pending", "active"}:
        raise HTTPException(status_code=404, detail="Assignable device not found.")
    if vehicle is None or vehicle.status != "active" or vehicle.review_status != "approved":
        raise HTTPException(status_code=409, detail="Vehicle must be approved and active.")
    current = db.scalar(select(VehicleDeviceAssignment).where(
        VehicleDeviceAssignment.device_id == device.id,
        VehicleDeviceAssignment.unassigned_at.is_(None),
    ))
    if current is not None:
        raise HTTPException(status_code=409, detail="Device already has an active vehicle assignment.")
    assignment = VehicleDeviceAssignment(
        device_id=device.id, vehicle_id=vehicle.id, assigned_by=context.user.id,
    )
    device.status = "active"
    db.add(assignment)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Vehicle already has an active tracking device.")
    _audit(db, context, "tracking.device.assigned", device.id, "assign",
           {"vehicle_id": str(vehicle.id)})
    db.commit()
    return {"assignment_id": str(assignment.id), "device_id": str(device.id),
            "vehicle_id": str(vehicle.id), "status": "active"}


@router.post("/devices/{device_id}/assignments/end")
def end_device_assignment(
    device_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    _authorize(db, context, "platform.tracking.manage")
    device = db.scalar(select(TrackingDevice).where(TrackingDevice.id == device_id).with_for_update())
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found.")
    assignment = db.scalar(select(VehicleDeviceAssignment).where(
        VehicleDeviceAssignment.device_id == device.id,
        VehicleDeviceAssignment.unassigned_at.is_(None),
    ).with_for_update())
    if assignment is None:
        raise HTTPException(status_code=409, detail="Device has no active vehicle assignment.")
    assignment.unassigned_at = datetime.now(UTC)
    assignment.unassigned_by = context.user.id
    if device.status == "active":
        device.status = "pending"
    _audit(db, context, "tracking.device.unassigned", device.id, "unassign",
           {"vehicle_id": str(assignment.vehicle_id)})
    db.commit()
    return {"device_id": str(device.id), "vehicle_id": str(assignment.vehicle_id),
            "status": device.status, "assignment_status": "ended"}


@router.post("/devices/{device_id}/credentials/rotate")
def rotate_device_credential(
    device_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    _authorize(db, context, "platform.tracking.manage")
    encryption_key = _require_encryption_key()
    device = db.scalar(select(TrackingDevice).where(TrackingDevice.id == device_id).with_for_update())
    if device is None or device.status == "revoked":
        raise HTTPException(status_code=404, detail="Rotatable device not found.")
    raw_credential = secrets.token_urlsafe(48)
    device.credential_ciphertext = encrypt_credential(raw_credential, encryption_key)
    device.credential_version += 1
    _audit(db, context, "tracking.device.credential_rotated", device.id, "rotate",
           {"credential_version": device.credential_version})
    db.commit()
    return {"device_id": str(device.id), "credential": raw_credential,
            "credential_version": device.credential_version, "credential_display_policy": "shown_once"}


@router.post("/devices/{device_id}/status")
def change_device_status(
    device_id: UUID, payload: DeviceStatusRequest, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    _authorize(db, context, "platform.tracking.manage")
    device = db.scalar(select(TrackingDevice).where(TrackingDevice.id == device_id).with_for_update())
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found.")
    if device.status == "revoked":
        raise HTTPException(status_code=409, detail="Revoked devices cannot be reactivated.")
    device.status = payload.status
    if payload.status == "revoked":
        assignment = db.scalar(select(VehicleDeviceAssignment).where(
            VehicleDeviceAssignment.device_id == device.id,
            VehicleDeviceAssignment.unassigned_at.is_(None),
        ).with_for_update())
        if assignment is not None:
            assignment.unassigned_at = datetime.now(timezone.utc)
            assignment.unassigned_by = context.user.id
    _audit(db, context, f"tracking.device.{payload.status}", device.id, payload.status)
    db.commit()
    return {"device_id": str(device.id), "status": device.status}


@router.post("/telemetry", status_code=status.HTTP_202_ACCEPTED)
async def receive_telemetry(request: Request, db: Session = Depends(get_db)) -> dict:
    device_identifier = request.headers.get("X-MITP-Device-ID", "")
    request_timestamp = request.headers.get("X-MITP-Timestamp", "")
    signature = request.headers.get("X-MITP-Signature", "")
    if not device_identifier or not request_timestamp or not signature:
        raise HTTPException(status_code=401, detail="Device authentication headers are required.")
    body = await request.body()
    if len(body) > 4096:
        raise HTTPException(status_code=413, detail="Telemetry payload exceeds 4096 bytes.")
    try:
        payload = TelemetryPayload.model_validate_json(body)
        item = ingest_telemetry(
            db, device_identifier=device_identifier,
            request_timestamp=request_timestamp, request_body=body,
            signature=signature, payload=payload,
        )
        db.commit()
    except TelemetryRejected as exc:
        db.rollback()
        status_code = 503 if exc.reason == "device_security_not_configured" else (
            429 if exc.reason == "device_rate_limit_exceeded" else (
                401 if exc.reason in {"device_not_active", "invalid_device_signature"} else 409
            )
        )
        raise HTTPException(status_code=status_code, detail=exc.reason)
    except ValueError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Invalid telemetry payload.")
    return {"accepted": True, "telemetry_id": str(item.id), "sequence": item.sequence}


@router.get("/vehicles/{vehicle_id}/latest")
def read_latest_vehicle_position(
    vehicle_id: UUID,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _authorize(db, context, "platform.tracking.read")
    position = latest_vehicle_position(db, vehicle_id)
    if position is None:
        raise HTTPException(status_code=404, detail="No accepted telemetry is available.")
    return {
        "vehicle_id": str(position.vehicle_id),
        "latitude": float(position.latitude),
        "longitude": float(position.longitude),
        "speed_kph": float(position.speed_kph),
        "heading_degrees": float(position.heading_degrees),
        "accuracy_meters": float(position.accuracy_meters),
        "recorded_at": position.recorded_at.isoformat(),
        "received_at": position.received_at.isoformat() if position.received_at else None,
        "source": "installed_vehicle_gps",
    }
