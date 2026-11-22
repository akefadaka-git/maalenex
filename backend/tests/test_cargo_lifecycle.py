import pytest
from fastapi import HTTPException

from app.domains.cargo.service import TRANSITIONS, validate_transition


def test_cargo_lifecycle_allows_only_declared_forward_transitions() -> None:
    for current, targets in TRANSITIONS.items():
        for target in targets:
            validate_transition(current, target)


def test_cargo_lifecycle_rejects_terminal_and_skipped_transitions() -> None:
    for current, target in (("draft", "delivered"), ("delivered", "in_transit"),
                            ("cancelled", "accepted"), ("in_transit", "cancelled"),
                            ("unknown", "accepted")):
        with pytest.raises(HTTPException) as error:
            validate_transition(current, target)
        assert error.value.status_code == 409


def test_cargo_exception_requires_explicit_recovery_transition() -> None:
    validate_transition("in_transit", "exception")
    validate_transition("exception", "in_transit")
    with pytest.raises(HTTPException):
        validate_transition("exception", "delivered")
