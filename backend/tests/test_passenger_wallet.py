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
from app.domains.wallet.models import LedgerAccount, LedgerPosting, LedgerTransaction
from app.routers.passenger_auth import current_passenger_context
from app.routers.passenger_wallet import router


@pytest.fixture
def wallet_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        PassengerAccount.__table__, LedgerAccount.__table__,
        LedgerTransaction.__table__, LedgerPosting.__table__, AuditEvent.__table__,
    ])
    db = Session(engine)
    passenger = PassengerAccount(
        id=uuid4(), login_identifier="wallet-rider@example.test",
        display_name="Synthetic Wallet Rider", status="active",
    )
    db.add(passenger)
    db.commit()
    context = SimpleNamespace(passenger=passenger)
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[current_passenger_context] = lambda: context
    with TestClient(app) as client:
        yield client, db, passenger
    db.close()
    engine.dispose()


def _wallet(db, passenger):
    return db.query(LedgerAccount).filter_by(
        owner_type="passenger", owner_ref=passenger.id,
        account_kind="passenger_wallet", currency_code="ETB",
    ).one()


def test_wallet_is_provisioned_once_and_starts_at_zero(wallet_client):
    client, db, passenger = wallet_client
    first = client.get("/api/v1/passenger/wallet")
    second = client.get("/api/v1/passenger/wallet")
    assert first.status_code == 200
    assert first.json()["balance_minor_units"] == 0
    assert first.json()["currency_code"] == "ETB"
    assert first.json()["history"] == []
    assert first.json()["funding_enabled"] is False
    assert first.json()["withdrawals_enabled"] is False
    assert first.json()["transfers_enabled"] is False
    assert second.json()["wallet_id"] == first.json()["wallet_id"]
    assert db.query(LedgerAccount).filter_by(owner_ref=passenger.id, account_kind="passenger_wallet").count() == 1
    assert db.query(AuditEvent).filter_by(event_type="passenger.wallet.provisioned").count() == 1


def test_wallet_balance_and_history_are_derived_from_balanced_postings(wallet_client):
    client, db, passenger = wallet_client
    client.get("/api/v1/passenger/wallet")
    wallet = _wallet(db, passenger)
    clearing = LedgerAccount(
        account_code="CLEARING-TEST-001", account_kind="clearing",
        owner_type="platform", owner_ref=None, currency_code="ETB",
        normal_balance="debit", allow_negative=True, status="active",
    )
    transaction = LedgerTransaction(
        reference="MNW-TEST-0001", idempotency_key="wallet-test-idempotency-0001",
        transaction_type="test_credit", status="posted", amount_minor_units=12500,
        currency_code="ETB", description="Synthetic ledger fixture",
    )
    db.add_all([clearing, transaction])
    db.flush()
    db.add_all([
        LedgerPosting(transaction_id=transaction.id, account_id=clearing.id, side="debit", amount_minor_units=12500),
        LedgerPosting(transaction_id=transaction.id, account_id=wallet.id, side="credit", amount_minor_units=12500),
    ])
    db.commit()
    response = client.get("/api/v1/passenger/wallet")
    assert response.status_code == 200
    assert response.json()["balance_minor_units"] == 12500
    assert response.json()["history"][0]["reference"] == "MNW-TEST-0001"
    assert response.json()["history"][0]["direction"] == "credit"
    assert response.json()["history"][0]["amount_minor_units"] == 12500


def test_wallet_fails_closed_when_transaction_is_unbalanced(wallet_client):
    client, db, passenger = wallet_client
    client.get("/api/v1/passenger/wallet")
    wallet = _wallet(db, passenger)
    transaction = LedgerTransaction(
        reference="MNW-TEST-UNBALANCED", idempotency_key="wallet-test-unbalanced-0001",
        transaction_type="test_credit", status="posted", amount_minor_units=900,
        currency_code="ETB", description="Invalid synthetic fixture",
    )
    db.add(transaction)
    db.flush()
    db.add(LedgerPosting(
        transaction_id=transaction.id, account_id=wallet.id,
        side="credit", amount_minor_units=900,
    ))
    db.commit()
    response = client.get("/api/v1/passenger/wallet")
    assert response.status_code == 503
    assert "reconciliation" in response.json()["detail"].lower()


def test_wallet_refuses_inactive_passenger(wallet_client):
    client, db, passenger = wallet_client
    passenger.status = "suspended"
    db.commit()
    response = client.get("/api/v1/passenger/wallet")
    assert response.status_code == 409
