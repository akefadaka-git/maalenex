"""Read-side passenger wallet provisioning and ledger reconciliation."""
from uuid import UUID, uuid4

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.domains.audit.service import record_event
from app.domains.identity.passenger_models import PassengerAccount
from app.domains.wallet.models import LedgerAccount, LedgerPosting, LedgerTransaction


WALLET_KIND = "passenger_wallet"
WALLET_CURRENCY = "ETB"
HISTORY_LIMIT = 50


class WalletUnavailable(Exception):
    """The passenger wallet cannot safely be displayed."""


class WalletLedgerIntegrityError(Exception):
    """A wallet transaction failed double-entry reconciliation."""


def get_or_create_passenger_wallet(db: Session, passenger_id: UUID) -> LedgerAccount:
    # Lock the owner row so concurrent first reads cannot create duplicate wallets.
    passenger = db.scalar(
        select(PassengerAccount)
        .where(PassengerAccount.id == passenger_id)
        .with_for_update()
    )
    if passenger is None or passenger.status != "active":
        raise WalletUnavailable("Passenger wallet is unavailable.")

    wallet = db.scalar(
        select(LedgerAccount).where(
            LedgerAccount.owner_type == "passenger",
            LedgerAccount.owner_ref == passenger_id,
            LedgerAccount.account_kind == WALLET_KIND,
            LedgerAccount.currency_code == WALLET_CURRENCY,
        )
    )
    if wallet is None:
        wallet = LedgerAccount(
            account_code=f"PW-{uuid4().hex.upper()}",
            account_kind=WALLET_KIND,
            owner_type="passenger",
            owner_ref=passenger_id,
            currency_code=WALLET_CURRENCY,
            normal_balance="credit",
            allow_negative=False,
            status="active",
        )
        db.add(wallet)
        db.flush()
        record_event(
            db,
            event_type="passenger.wallet.provisioned",
            actor_type="passenger",
            actor_id=str(passenger_id),
            resource_type="ledger_account",
            resource_id=str(wallet.id),
            action="provision_wallet",
            outcome="success",
            metadata={"currency_code": WALLET_CURRENCY, "account_kind": WALLET_KIND},
        )

    if (
        wallet.owner_type != "passenger"
        or wallet.owner_ref != passenger_id
        or wallet.account_kind != WALLET_KIND
        or wallet.currency_code != WALLET_CURRENCY
        or wallet.normal_balance != "credit"
        or wallet.allow_negative
    ):
        raise WalletUnavailable("Passenger wallet configuration is invalid.")
    return wallet


def passenger_wallet_snapshot(db: Session, passenger_id: UUID) -> dict:
    wallet = get_or_create_passenger_wallet(db, passenger_id)
    signed_amount = case(
        (LedgerPosting.side == "credit", LedgerPosting.amount_minor_units),
        else_=-LedgerPosting.amount_minor_units,
    )
    balance = db.scalar(
        select(func.coalesce(func.sum(signed_amount), 0)).where(
            LedgerPosting.account_id == wallet.id
        )
    )
    rows = db.execute(
        select(
            LedgerTransaction,
            func.coalesce(func.sum(signed_amount), 0).label("wallet_net"),
        )
        .join(LedgerPosting, LedgerPosting.transaction_id == LedgerTransaction.id)
        .where(LedgerPosting.account_id == wallet.id)
        .group_by(LedgerTransaction.id)
        .order_by(LedgerTransaction.posted_at.desc(), LedgerTransaction.created_at.desc())
        .limit(HISTORY_LIMIT)
    ).all()

    history = []
    for transaction, wallet_net in rows:
        totals = db.execute(
            select(
                func.coalesce(
                    func.sum(case((LedgerPosting.side == "debit", LedgerPosting.amount_minor_units), else_=0)), 0
                ).label("debits"),
                func.coalesce(
                    func.sum(case((LedgerPosting.side == "credit", LedgerPosting.amount_minor_units), else_=0)), 0
                ).label("credits"),
            ).where(LedgerPosting.transaction_id == transaction.id)
        ).one()
        if (
            int(totals.debits) != int(totals.credits)
            or int(totals.debits) != transaction.amount_minor_units
            or transaction.currency_code != wallet.currency_code
        ):
            raise WalletLedgerIntegrityError("Wallet ledger reconciliation failed.")
        net = int(wallet_net)
        history.append({
            "reference": transaction.reference,
            "transaction_type": transaction.transaction_type,
            "status": transaction.status,
            "direction": "credit" if net > 0 else "debit" if net < 0 else "neutral",
            "amount_minor_units": abs(net),
            "currency_code": transaction.currency_code,
            "description": transaction.description,
            "posted_at": transaction.posted_at.isoformat(),
        })

    return {
        "wallet_id": str(wallet.id),
        "account_status": wallet.status,
        "balance_minor_units": int(balance or 0),
        "currency_code": wallet.currency_code,
        "history": history,
        "funding_enabled": False,
        "withdrawals_enabled": False,
        "transfers_enabled": False,
    }
