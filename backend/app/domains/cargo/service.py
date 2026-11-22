"""Deterministic cargo lifecycle rules; no payment or dispatch side effects."""

from fastapi import HTTPException

TRANSITIONS = {
    "draft": {"accepted", "cancelled"},
    "accepted": {"assigned", "cancelled", "exception"},
    "assigned": {"in_transit", "cancelled", "exception"},
    "in_transit": {"delivered", "exception"},
    "exception": {"assigned", "in_transit", "cancelled"},
    "delivered": set(),
    "cancelled": set(),
}


def validate_transition(current: str, target: str) -> None:
    if target not in TRANSITIONS.get(current, set()):
        raise HTTPException(status_code=409, detail=f"Cargo transition {current} -> {target} is not permitted.")
