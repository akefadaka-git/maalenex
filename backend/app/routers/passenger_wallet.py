"""Authenticated passenger wallet balance and ledger history."""
# FastAPI dependency injection requires Depends instances in endpoint defaults.
# ruff: noqa: B008
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.identity.passenger_service import PassengerContext
from app.domains.wallet.passenger_service import (
    passenger_wallet_snapshot,
    WalletLedgerIntegrityError,
    WalletUnavailable,
)
from app.routers.passenger_auth import current_passenger_context


router = APIRouter(prefix="/passenger/wallet", tags=["passenger-wallet"])


@router.get("")
def get_passenger_wallet(
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = passenger_wallet_snapshot(db, context.passenger.id)
        db.commit()
        return result
    except WalletLedgerIntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Wallet ledger reconciliation is required. The balance is temporarily unavailable.",
        )
    except WalletUnavailable as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))
