import pytest
from fastapi import HTTPException

from app.domains.cargo.dispatch_service import (
    DISPATCH_TRANSITIONS,
    EVENT_TYPES,
    validate_dispatch_transition,
    validate_tracking_event,
)


def test_dispatch_transition_graph_accepts_only_declared_edges() -> None:
    for current, targets in DISPATCH_TRANSITIONS.items():
        for target in targets:
            validate_dispatch_transition(current, target)


def test_dispatch_terminal_states_and_skipped_edges_are_rejected() -> None:
    for current, target in (
        ("offered", "delivered"),
        ("rejected", "accepted"),
        ("delivered", "in_transit"),
        ("failed", "accepted"),
        ("cancelled", "picked_up"),
        ("unknown", "accepted"),
    ):
        with pytest.raises(HTTPException) as error:
            validate_dispatch_transition(current, target)
        assert error.value.status_code == 409


def test_tracking_event_catalog_is_bounded_and_explicit() -> None:
    for event in EVENT_TYPES:
        validate_tracking_event(event)
    with pytest.raises(HTTPException) as error:
        validate_tracking_event("delete_history")
    assert error.value.status_code == 422
