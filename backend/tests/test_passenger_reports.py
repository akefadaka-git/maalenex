import base64
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.domains.audit.models import AuditEvent
from app.domains.identity.passenger_models import PassengerAccount
from app.domains.identity.security import token_digest
from app.domains.support.report_models import PassengerReport, PassengerReportAttachment
from app.routers import admin as admin_module
from app.routers.auth import current_staff_context
from app.routers.passenger_auth import current_passenger_context
from app.routers.passenger_reports import router


@pytest.fixture
def report_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        PassengerAccount.__table__, PassengerReport.__table__,
        PassengerReportAttachment.__table__, AuditEvent.__table__,
    ])
    db = Session(engine)
    passenger = PassengerAccount(
        id=uuid4(), login_identifier="report-rider@example.test",
        display_name="Synthetic Report Rider", status="active",
    )
    db.add(passenger)
    db.commit()
    csrf = "reports-csrf-token"
    context = SimpleNamespace(
        passenger=passenger,
        session=SimpleNamespace(csrf_token_hash=token_digest(csrf)),
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[current_passenger_context] = lambda: context
    with TestClient(app) as test_client:
        test_client.cookies.set("mnm_passenger_csrf", csrf)
        yield test_client, db, passenger
    db.close()
    engine.dispose()


def _payload(**overrides):
    return {
        "report_type": "report",
        "category": "app_issue",
        "severity": "normal",
        "subject": "Application fails to reconnect",
        "description": "The application does not reconnect after the network becomes available.",
        **overrides,
    }


def _create(client):
    return client.post(
        "/api/v1/passenger/reports",
        json=_payload(),
        headers={"X-CSRF-Token": "reports-csrf-token"},
    )


def test_report_and_complaint_submission_persists_separate_types(report_client):
    client, _, _ = report_client
    report = _create(client)
    complaint = client.post(
        "/api/v1/passenger/reports",
        json=_payload(
            report_type="complaint", category="safety", severity="high",
            subject="Unsafe vehicle", description="A passenger door was damaged during the trip.",
        ),
        headers={"X-CSRF-Token": "reports-csrf-token"},
    )
    assert report.status_code == 201
    assert complaint.status_code == 201
    assert report.json()["report_reference"].startswith("MN-RPT-")
    assert complaint.json()["report_type"] == "complaint"
    assert complaint.json()["status"] == "submitted"
    assert len(client.get("/api/v1/passenger/reports").json()["items"]) == 2
    detail = client.get(f"/api/v1/passenger/reports/{complaint.json()['report_reference']}")
    assert detail.status_code == 200
    assert detail.json()["category"] == "safety"


def test_report_submission_requires_csrf_and_valid_content(report_client):
    client, _, _ = report_client
    denied = client.post("/api/v1/passenger/reports", json=_payload())
    assert denied.status_code == 403
    invalid = client.post(
        "/api/v1/passenger/reports",
        json=_payload(subject="  ", description="          "),
        headers={"X-CSRF-Token": "reports-csrf-token"},
    )
    assert invalid.status_code == 422


def test_report_submission_is_rate_limited(report_client):
    client, _, _ = report_client
    for _ in range(5):
        assert _create(client).status_code == 201
    assert _create(client).status_code == 429


def test_private_evidence_upload_and_owner_scoped_download(report_client, monkeypatch, tmp_path):
    client, _, _ = report_client
    monkeypatch.setenv("MAALENEX_PRIVATE_UPLOAD_DIR", str(tmp_path))
    created = _create(client)
    reference = created.json()["report_reference"]
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
    uploaded = client.post(
        f"/api/v1/passenger/reports/{reference}/attachments",
        json={
            "file_name": "../../vehicle-evidence.png",
            "content_type": "image/png",
            "content_base64": base64.b64encode(png).decode("ascii"),
        },
        headers={"X-CSRF-Token": "reports-csrf-token"},
    )
    assert uploaded.status_code == 201
    assert uploaded.json()["file_name"] == "vehicle-evidence.png"
    assert uploaded.json()["size_bytes"] == len(png)
    detail = client.get(f"/api/v1/passenger/reports/{reference}")
    assert len(detail.json()["attachments"]) == 1
    attachment_id = uploaded.json()["id"]
    downloaded = client.get(f"/api/v1/passenger/reports/{reference}/attachments/{attachment_id}")
    assert downloaded.status_code == 200
    assert downloaded.content == png
    assert downloaded.headers["x-content-type-options"] == "nosniff"
    assert list(tmp_path.iterdir())[0].stat().st_mode & 0o777 == 0o600


def test_evidence_rejects_mismatched_file_signature(report_client, monkeypatch, tmp_path):
    client, _, _ = report_client
    monkeypatch.setenv("MAALENEX_PRIVATE_UPLOAD_DIR", str(tmp_path))
    reference = _create(client).json()["report_reference"]
    response = client.post(
        f"/api/v1/passenger/reports/{reference}/attachments",
        json={
            "file_name": "not-a-pdf.pdf",
            "content_type": "application/pdf",
            "content_base64": base64.b64encode(b"not a PDF document").decode("ascii"),
        },
        headers={"X-CSRF-Token": "reports-csrf-token"},
    )
    assert response.status_code == 415
    assert list(tmp_path.iterdir()) == []


@pytest.fixture
def staff_report_client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        PassengerAccount.__table__, PassengerReport.__table__, AuditEvent.__table__,
    ])
    db = Session(engine)
    passenger = PassengerAccount(
        id=uuid4(), login_identifier="staff-report-rider@example.test",
        display_name="Report Queue Rider", status="active",
    )
    db.add(passenger)
    report = PassengerReport(
        report_reference="MN-RPT-STAFF-TEST", passenger_id=passenger.id,
        report_type="complaint", category="safety", severity="high",
        subject="Unsafe vehicle", description="A passenger door was damaged during the trip.",
        status="submitted",
    )
    db.add(report)
    db.commit()
    context = SimpleNamespace(user=SimpleNamespace(id=uuid4()))
    app = FastAPI()
    app.include_router(admin_module.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[current_staff_context] = lambda: context
    monkeypatch.setattr(admin_module, "_authorize", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(admin_module, "require_csrf", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(admin_module, "_audit", lambda *_args, **_kwargs: None)
    with TestClient(app) as client:
        yield client, db, report
    db.close()
    engine.dispose()


def test_staff_can_filter_claim_and_resolve_complaints(staff_report_client):
    client, db, report = staff_report_client
    listed = client.get("/api/v1/reports/passenger?report_type=complaint&report_status=submitted")
    assert listed.status_code == 200
    assert listed.json()[0]["report_reference"] == report.report_reference
    claimed = client.post(f"/api/v1/reports/passenger/{report.id}/claim")
    assert claimed.status_code == 200
    assert claimed.json()["status"] == "under_review"
    reviewed = client.post(
        f"/api/v1/reports/passenger/{report.id}/review",
        json={"status": "resolved", "resolution_note": "The safety issue was reviewed and corrective action recorded."},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "resolved"
    db.refresh(report)
    assert report.resolved_at is not None
    assert report.resolution_note.startswith("The safety issue")
