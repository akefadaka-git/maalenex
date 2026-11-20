from secrets import token_hex
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.wallet.models import LedgerAccount, LedgerPosting, LedgerTransaction


class LedgerInvariantError(ValueError):
    pass


class IdempotencyConflict(LedgerInvariantError):
    pass


def create_ledger_account(
    db: Session, *, account_code: str, account_kind: str, owner_type: str,
    owner_ref: UUID | None, currency_code: str, normal_balance: str,
    allow_negative: bool = False,
) -> LedgerAccount:
    if normal_balance not in {"debit", "credit"}:
        raise LedgerInvariantError("Invalid account normal balance.")
    if len(currency_code) != 3 or currency_code != currency_code.upper():
        raise LedgerInvariantError("Currency must be a three-letter uppercase code.")
    account = LedgerAccount(
        account_code=account_code, account_kind=account_kind, owner_type=owner_type,
        owner_ref=owner_ref, currency_code=currency_code,
        normal_balance=normal_balance, allow_negative=allow_negative, status="active",
    )
    db.add(account)
    db.flush()
    return account


def get_account_balance_minor(db: Session, account: LedgerAccount) -> int:
    normal = func.coalesce(func.sum(case(
        (LedgerPosting.side == account.normal_balance, LedgerPosting.amount_minor_units),
        else_=-LedgerPosting.amount_minor_units,
    )), 0)
    return int(db.scalar(select(normal).where(LedgerPosting.account_id == account.id)) or 0)


def post_balanced_transaction(
    db: Session, *, idempotency_key: str, transaction_type: str,
    amount_minor_units: int, currency_code: str, debit_account_id: UUID,
    credit_account_id: UUID, description: str,
    external_reference: str | None = None,
) -> LedgerTransaction:
    if not 8 <= len(idempotency_key) <= 128:
        raise LedgerInvariantError("Idempotency key must contain 8 to 128 characters.")
    if amount_minor_units <= 0:
        raise LedgerInvariantError("Amount must be a positive integer in minor units.")
    if debit_account_id == credit_account_id:
        raise LedgerInvariantError("A transaction must use two distinct ledger accounts.")

    existing = db.scalar(select(LedgerTransaction).where(
        LedgerTransaction.idempotency_key == idempotency_key
    ))
    if existing is not None:
        postings = db.scalars(select(LedgerPosting).where(
            LedgerPosting.transaction_id == existing.id
        )).all()
        expected = {(debit_account_id, "debit"), (credit_account_id, "credit")}
        actual = {(item.account_id, item.side) for item in postings}
        if (
            existing.transaction_type != transaction_type
            or existing.amount_minor_units != amount_minor_units
            or existing.currency_code != currency_code
            or actual != expected
        ):
            raise IdempotencyConflict("Idempotency key was already used for a different command.")
        return existing

    accounts = db.scalars(select(LedgerAccount).where(
        LedgerAccount.id.in_([debit_account_id, credit_account_id])
    ).with_for_update()).all()
    by_id = {item.id: item for item in accounts}
    if len(by_id) != 2:
        raise LedgerInvariantError("Ledger account not found.")
    debit = by_id[debit_account_id]
    credit = by_id[credit_account_id]
    if debit.status != "active" or credit.status != "active":
        raise LedgerInvariantError("Both ledger accounts must be active.")
    if debit.currency_code != currency_code or credit.currency_code != currency_code:
        raise LedgerInvariantError("Transaction and account currencies must match.")

    debit_delta = amount_minor_units if debit.normal_balance == "debit" else -amount_minor_units
    credit_delta = amount_minor_units if credit.normal_balance == "credit" else -amount_minor_units
    if not debit.allow_negative and get_account_balance_minor(db, debit) + debit_delta < 0:
        raise LedgerInvariantError("Debit would overdraw the source ledger account.")
    if not credit.allow_negative and get_account_balance_minor(db, credit) + credit_delta < 0:
        raise LedgerInvariantError("Credit would overdraw the destination ledger account.")

    transaction = LedgerTransaction(
        reference=f"MNX-{token_hex(8).upper()}",
        idempotency_key=idempotency_key, transaction_type=transaction_type,
        status="posted", amount_minor_units=amount_minor_units,
        currency_code=currency_code, description=description[:240],
        external_reference=external_reference,
    )
    db.add(transaction)
    db.flush()
    db.add_all([
        LedgerPosting(
            transaction_id=transaction.id, account_id=debit.id,
            side="debit", amount_minor_units=amount_minor_units,
        ),
        LedgerPosting(
            transaction_id=transaction.id, account_id=credit.id,
            side="credit", amount_minor_units=amount_minor_units,
        ),
    ])
    record_event(
        db, event_type="wallet.ledger.transaction.posted", actor_type="system",
        actor_id=None, resource_type="ledger_transaction",
        resource_id=str(transaction.id), action=transaction_type, outcome="success",
        metadata={"currency_code": currency_code, "amount_minor_units": amount_minor_units},
    )
    db.flush()
    return transaction
