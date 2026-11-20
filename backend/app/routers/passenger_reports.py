"""Passenger-owned reporting and complaints API with private evidence uploads."""
# FastAPI dependency injection requires Depends instances in endpoint defaults.
# ruff: noqa: B008
import base64
import binascii
import hashlib
import os
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from secrets import token_urlsafe
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.identity.passenger_service import PassengerContext, verify_passenger_csrf
from app.domains.support.passenger_models import PassengerReport, PassengerReportAttachment
from app.routers.passenger_auth import current_passenger_context

router = APIRouter(prefix="/passenger/reports", tags=["passenger-reports"])

ReportType = Literal["report", "complaint"]
ReportCategory = Literal[
    "app_issue", "journey", "booking", "wallet", "payment", "safety",
    "driver_vehicle", "accessibility", "fraud", "other",
]
Severity = Literal["low", "normal", "high", "urgent"]
_ALLOWED_FILES = {
    "application/pdf": (".pdf", b"%PDF-"),
    "image/jpeg": (".jpg", b"\xff\xd8\xff"),
    "image/png": (".png", b"\x89PNG\r\n\x1a\n"),
    "image/webp": (".webp", b"RIFF"),
}
_MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024
_MAX_ATTACHMENTS = 3


class ReportCreate(BaseModel):
    report_type: ReportType
    category: ReportCategory
    severity: Severity = "normal"
    subject: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=5000)


class AttachmentCreate(BaseModel):
    file_name: str = Field(min_length=1, max_length=180)
    content_type: str = Field(min_length=1, max_length=80)
    content_base64: str = Field(min_length=8, max_length=7_000_000)


def _require_mutation_access(request: Request, context: PassengerContext) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed.")
    if not verify_passenger_csrf(
        context,
        cookie_token=request.cookies.get("mnm_passenger_csrf"),
        header_token=request.headers.get("X-CSRF-Token"),
    ):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")


def _storage_root() -> Path:
    configured = os.environ.get("MAALENEX_PRIVATE_UPLOAD_DIR", "/var/lib/maalenex/private-uploads")
    return Path(configured).expanduser().resolve()


def _report_payload(report: PassengerReport, attachments: list[PassengerReportAttachment]) -> dict:
    return {
        "report_reference": report.report_reference,
        "report_type": report.report_type,
        "category": report.category,
        "severity": report.severity,
        "subject": report.subject,
        "description": report.description,
        "status": report.status,
        "resolution_note": report.resolution_note,
        "created_at": report.created_at.isoformat(),
        "updated_at": report.updated_at.isoformat(),
        "resolved_at": report.resolved_at.isoformat() if report.resolved_at else None,
        "attachments": [{
            "id": str(item.id),
            "file_name": item.original_filename,
            "content_type": item.content_type,
            "size_bytes": item.size_bytes,
            "sha256": item.sha256,
        } for item in attachments],
    }


def _owned_report(db: Session, context: PassengerContext, report_reference: str) -> PassengerReport:
    report = db.scalar(select(PassengerReport).where(
        PassengerReport.report_reference == report_reference,
        PassengerReport.passenger_id == context.passenger.id,
    ))
    if report is None:
        raise HTTPException(status_code=404, detail="Report or complaint not found.")
    return report


@router.post("", status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreate,
    request: Request,
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation_access(request, context)
    subject, description = payload.subject.strip(), payload.description.strip()
    if len(subject) < 3 or len(description) < 10:
        raise HTTPException(status_code=422, detail="A subject and description are required.")
    cutoff = datetime.now(UTC) - timedelta(hours=1)
    recent_count = db.scalar(select(func.count()).select_from(PassengerReport).where(
        PassengerReport.passenger_id == context.passenger.id,
        PassengerReport.created_at >= cutoff,
    )) or 0
    if recent_count >= 5:
        raise HTTPException(status_code=429, detail="Report submission limit reached. Try again later.")
    report = PassengerReport(
        report_reference="MN-RPT-" + token_urlsafe(9).replace("-", "").replace("_", "").upper(),
        passenger_id=context.passenger.id,
        report_type=payload.report_type,
        category=payload.category,
        severity=payload.severity,
        subject=subject,
        description=description,
        status="submitted",
    )
    db.add(report)
    db.flush()
    record_event(
        db, event_type="passenger.report.created", actor_type="passenger",
        actor_id=str(context.passenger.id), resource_type="passenger_report",
        resource_id=str(report.id), action="create", outcome="success",
        metadata={"report_type": report.report_type, "category": report.category, "severity": report.severity, "reference": report.report_reference},
    )
    db.commit()
    db.refresh(report)
    return _report_payload(report, [])


@router.get("")
def list_reports(
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    reports = db.scalars(select(PassengerReport).where(
        PassengerReport.passenger_id == context.passenger.id
    ).order_by(PassengerReport.created_at.desc()).limit(50)).all()
    result = []
    for report in reports:
        attachments = db.scalars(select(PassengerReportAttachment).where(
            PassengerReportAttachment.report_id == report.id
        )).all()
        result.append(_report_payload(report, attachments))
    return {"items": result}


@router.get("/{report_reference}")
def read_report(
    report_reference: str,
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    report = _owned_report(db, context, report_reference)
    attachments = db.scalars(select(PassengerReportAttachment).where(
        PassengerReportAttachment.report_id == report.id
    )).all()
    return _report_payload(report, attachments)


@router.post("/{report_reference}/attachments", status_code=status.HTTP_201_CREATED)
def upload_report_attachment(
    report_reference: str,
    payload: AttachmentCreate,
    request: Request,
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation_access(request, context)
    report = _owned_report(db, context, report_reference)
    if report.status in {"resolved", "dismissed"}:
        raise HTTPException(status_code=409, detail="Evidence cannot be added to a closed report.")
    count = db.scalar(select(func.count()).select_from(PassengerReportAttachment).where(
        PassengerReportAttachment.report_id == report.id
    )) or 0
    if count >= _MAX_ATTACHMENTS:
        raise HTTPException(status_code=422, detail="A report may contain at most three attachments.")
    content_type = payload.content_type.lower().strip()
    if content_type not in _ALLOWED_FILES:
        raise HTTPException(status_code=415, detail="Only PDF, JPEG, PNG and WebP evidence files are accepted.")
    try:
        raw = base64.b64decode(payload.content_base64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=422, detail="Attachment encoding is invalid.") from None
    if not raw or len(raw) > _MAX_ATTACHMENT_BYTES:
        raise HTTPException(status_code=413, detail="Each attachment must be between 1 byte and 5 MB.")
    extension, signature = _ALLOWED_FILES[content_type]
    if not raw.startswith(signature) or (content_type == "image/webp" and raw[8:12] != b"WEBP"):
        raise HTTPException(status_code=415, detail="The file content does not match its declared type.")
    storage_key = f"{uuid4().hex}{extension}"
    root = _storage_root()
    try:
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        target = (root / storage_key).resolve()
        if target.parent != root:
            raise HTTPException(status_code=400, detail="Invalid attachment storage key.")
        with target.open("xb") as handle:
            handle.write(raw)
        os.chmod(target, 0o600)
    except OSError:
        raise HTTPException(status_code=503, detail="Private evidence storage is unavailable.") from None
    safe_name = re.sub(r"[^A-Za-z0-9._ -]", "_", Path(payload.file_name).name)[:180] or f"evidence{extension}"
    attachment = PassengerReportAttachment(
        report_id=report.id, original_filename=safe_name, content_type=content_type,
        size_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), storage_key=storage_key,
    )
    db.add(attachment)
    record_event(
        db, event_type="passenger.report.attachment.created", actor_type="passenger",
        actor_id=str(context.passenger.id), resource_type="passenger_report",
        resource_id=str(report.id), action="attach_evidence", outcome="success",
        metadata={"content_type": content_type, "size_bytes": len(raw)},
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        (root / storage_key).unlink(missing_ok=True)
        raise
    db.refresh(attachment)
    return {
        "id": str(attachment.id), "file_name": attachment.original_filename,
        "content_type": attachment.content_type, "size_bytes": attachment.size_bytes,
        "sha256": attachment.sha256,
    }


@router.get("/{report_reference}/attachments/{attachment_id}")
def download_report_attachment(
    report_reference: str,
    attachment_id: UUID,
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> FileResponse:
    report = _owned_report(db, context, report_reference)
    attachment = db.scalar(select(PassengerReportAttachment).where(
        PassengerReportAttachment.id == attachment_id,
        PassengerReportAttachment.report_id == report.id,
    ))
    if attachment is None:
        raise HTTPException(status_code=404, detail="Evidence attachment not found.")
    target = (_storage_root() / attachment.storage_key).resolve()
    if target.parent != _storage_root() or not target.is_file():
        raise HTTPException(status_code=404, detail="Evidence attachment is unavailable.")
    return FileResponse(
        target, media_type=attachment.content_type, filename=attachment.original_filename,
        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"},
    )
