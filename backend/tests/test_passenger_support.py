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
from app.domains.support.passenger_models import PassengerSupportCase
from app.routers.passenger_auth import current_passenger_context
from app.routers.passenger_support import router


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        PassengerAccount.__table__, PassengerSupportCase.__table__, AuditEvent.__table__,
    ])
    db = Session(engine)
    passenger = PassengerAccount(
        id=uuid4(), login_identifier="rider@example.test",
        display_name="Synthetic Rider", status="active",
    )
    db.add(passenger)
    db.commit()
    csrf = "support-csrf-token"
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
        yield test_client
    db.close()
    engine.dispose()


def test_faqs_are_available_in_both_supported_languages(client):
    english = client.get("/api/v1/passenger/support/faqs?language=en")
    amharic = client.get("/api/v1/passenger/support/faqs?language=am")
    assert english.status_code == 200
    assert amharic.status_code == 200
    assert len(english.json()["items"]) >= 5
    assert any("መለያ" in item["question"] for item in amharic.json()["items"])


def test_support_case_requires_csrf_and_persists_with_reference(client):
    payload = {
        "category": "technical",
        "subject": "App connection problem",
        "message": "The application cannot reconnect after the internet returns.",
    }
    denied = client.post("/api/v1/passenger/support/cases", json=payload)
    assert denied.status_code == 403
    created = client.post(
        "/api/v1/passenger/support/cases",
        json=payload,
        headers={"X-CSRF-Token": "support-csrf-token"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["case_reference"].startswith("MN-SUP-")
    assert body["status"] == "open"
    assert client.get("/api/v1/passenger/support/cases").json()["items"][0]["case_reference"] == body["case_reference"]
    detail = client.get(f"/api/v1/passenger/support/cases/{body['case_reference']}")
    assert detail.status_code == 200
    assert detail.json()["message"] == payload["message"]


def test_support_case_validation_rejects_blank_content(client):
    response = client.post(
        "/api/v1/passenger/support/cases",
        json={"category": "general", "subject": "  ", "message": "          "},
        headers={"X-CSRF-Token": "support-csrf-token"},
    )
    assert response.status_code == 422
