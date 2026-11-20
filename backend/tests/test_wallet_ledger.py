from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.domains.audit.models import AuditEvent
from app.domains.wallet.models import LedgerAccount, LedgerPosting, LedgerTransaction
from app.domains.wallet.service import (
    IdempotencyConflict, LedgerInvariantError, create_ledger_account,
    get_account_balance_minor, post_balanced_transaction,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[
        LedgerAccount.__table__, LedgerTransaction.__table__,
        LedgerPosting.__table__, AuditEvent.__table__,
    ])
    with Session(engine) as session:
        yield session
        session.rollback()
    engine.dispose()


def test_balanced_deposit_and_withdrawal_update_wallet_balance(db):
    settlement = create_ledger_account(
        db, account_code="ETB-SETTLEMENT-001", account_kind="settlement_asset",
        owner_type="platform", owner_ref=None, currency_code="ETB",
        normal_balance="debit", )
    wallet = create_ledger_account(
        db, account_code="ETB-CUSTOMER-001", account_kind="customer_wallet_liability",
        owner_type="passenger", owner_ref=uuid4(), currency_code="ETB",
        normal_balance="credit",
    )
    deposit = post_balanced_transaction(
        db, idempotency_key="deposit-test-0001", transaction_type="sandbox_deposit",
        amount_minor_units=12500, currency_code="ETB",
        debit_account_id=settlement.id, credit_account_id=wallet.id,
        description="Synthetic test deposit",
    )
    assert get_account_balance_minor(db, wallet) == 12500

    withdrawal = post_balanced_transaction(
        db, idempotency_key="withdraw-test-0001", transaction_type="sandbox_withdrawal",
        amount_minor_units=2500, currency_code="ETB",
        debit_account_id=wallet.id, credit_account_id=settlement.id,
        description="Synthetic test withdrawal",
    )
    assert get_account_balance_minor(db, wallet) == 10000
    assert deposit.id != withdrawal.id
    assert db.query(LedgerPosting).filter_by(transaction_id=deposit.id).count() == 2


def test_idempotent_replay_returns_original_transaction(db):
    settlement = create_ledger_account(
        db, account_code="ETB-SETTLEMENT-002", account_kind="settlement_asset",
        owner_type="platform", owner_ref=None, currency_code="ETB",
        normal_balance="debit", )
    wallet = create_ledger_account(
        db, account_code="ETB-CUSTOMER-002", account_kind="customer_wallet_liability",
        owner_type="passenger", owner_ref=uuid4(), currency_code="ETB",
        normal_balance="credit",
    )
    args = dict(
        idempotency_key="deposit-test-0002", transaction_type="sandbox_deposit",
        amount_minor_units=4000, currency_code="ETB",
        debit_account_id=settlement.id, credit_account_id=wallet.id,
        description="Synthetic test deposit",
    )
    first = post_balanced_transaction(db, **args)
    second = post_balanced_transaction(db, **args)
    assert first.id == second.id
    assert db.query(LedgerPosting).filter_by(transaction_id=first.id).count() == 2


def test_idempotency_key_cannot_be_reused_for_different_amount(db):
    settlement = create_ledger_account(
        db, account_code="ETB-SETTLEMENT-003", account_kind="settlement_asset",
        owner_type="platform", owner_ref=None, currency_code="ETB",
        normal_balance="debit", )
    wallet = create_ledger_account(
        db, account_code="ETB-CUSTOMER-003", account_kind="customer_wallet_liability",
        owner_type="passenger", owner_ref=uuid4(), currency_code="ETB",
        normal_balance="credit",
    )
    args = dict(
        idempotency_key="deposit-test-0003", transaction_type="sandbox_deposit",
        amount_minor_units=4000, currency_code="ETB",
        debit_account_id=settlement.id, credit_account_id=wallet.id,
        description="Synthetic test deposit",
    )
    post_balanced_transaction(db, **args)
    with pytest.raises(IdempotencyConflict):
        post_balanced_transaction(db, **{**args, "amount_minor_units": 4500})


def test_wallet_cannot_be_overdrawn(db):
    settlement = create_ledger_account(
        db, account_code="ETB-SETTLEMENT-004", account_kind="settlement_asset",
        owner_type="platform", owner_ref=None, currency_code="ETB",
        normal_balance="debit", )
    wallet = create_ledger_account(
        db, account_code="ETB-CUSTOMER-004", account_kind="customer_wallet_liability",
        owner_type="passenger", owner_ref=uuid4(), currency_code="ETB",
        normal_balance="credit",
    )
    with pytest.raises(LedgerInvariantError, match="overdraw"):
        post_balanced_transaction(
            db, idempotency_key="withdraw-test-0004", transaction_type="sandbox_withdrawal",
            amount_minor_units=1, currency_code="ETB",
            debit_account_id=wallet.id, credit_account_id=settlement.id,
            description="Synthetic test withdrawal",
        )
