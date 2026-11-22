"""Deterministic dispatch lifecycle and event validation."""
from fastapi import HTTPException

DISPATCH_TRANSITIONS = {
    "offered": {"accepted", "rejected", "cancelled"},
    "accepted": {"picked_up", "cancelled", "failed"},
    "picked_up": {"in_transit", "failed"},
    "in_transit": {"delivered", "failed"},
    "rejected": set(), "delivered": set(), "failed": set(), "cancelled": set(),
}

EVENT_TYPES = {"accepted", "rejected", "picked_up", "departed", "checkpoint", "arrived", "delivered", "failed", "cancelled", "exception"}


def validate_dispatch_transition(current: str, target: str) -> None:
    if target not in DISPATCH_TRANSITIONS.get(current, set()):
        raise HTTPException(status_code=409, detail=f"Dispatch transition {current} -> {target} is not permitted.")


def validate_tracking_event(event_type: str) -> None:
    if event_type not in EVENT_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported cargo tracking event type.")
