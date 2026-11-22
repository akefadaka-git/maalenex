"""Validation rules for carrier operations and cargo exception resolution."""
from fastapi import HTTPException

CARRIER_STATUSES = {"pending", "active", "restricted", "suspended"}
EXCEPTION_CODES = {"delivery_failed", "recipient_unavailable", "recipient_refused", "cargo_damaged", "cargo_missing", "delayed", "documentation_issue", "other"}
RESOLUTION_CODES = {"delivered", "returned_to_sender", "redelivered", "compensated", "no_action", "other"}
EXCEPTION_TRANSITIONS = {"open": {"investigating", "resolved"}, "investigating": {"resolved", "open"}, "resolved": {"closed"}, "closed": set()}


def validate_carrier_status(status: str) -> None:
    if status not in CARRIER_STATUSES:
        raise HTTPException(status_code=422, detail="Unsupported carrier operational status.")


def validate_exception_code(code: str) -> None:
    if code not in EXCEPTION_CODES:
        raise HTTPException(status_code=422, detail="Unsupported cargo exception code.")


def validate_resolution(code: str) -> None:
    if code not in RESOLUTION_CODES:
        raise HTTPException(status_code=422, detail="Unsupported cargo exception resolution code.")


def validate_exception_transition(current: str, target: str) -> None:
    if target not in EXCEPTION_TRANSITIONS.get(current, set()):
        raise HTTPException(status_code=409, detail=f"Exception transition {current} -> {target} is not permitted.")
