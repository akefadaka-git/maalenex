import pytest
from fastapi import HTTPException

from app.domains.cargo.carrier_service import (
    CARRIER_STATUSES,
    EXCEPTION_CODES,
    EXCEPTION_TRANSITIONS,
    RESOLUTION_CODES,
    validate_carrier_status,
    validate_exception_code,
    validate_exception_transition,
    validate_resolution,
)


def test_carrier_operational_status_catalog_is_explicit() -> None:
    for status in CARRIER_STATUSES:
        validate_carrier_status(status)
    with pytest.raises(HTTPException) as error:
        validate_carrier_status("commercially_licensed")
    assert error.value.status_code == 422


def test_exception_classification_and_resolution_catalogs_are_bounded() -> None:
    for code in EXCEPTION_CODES:
        validate_exception_code(code)
    for code in RESOLUTION_CODES:
        validate_resolution(code)
    with pytest.raises(HTTPException) as error:
        validate_exception_code("delete_case")
    assert error.value.status_code == 422


def test_exception_lifecycle_accepts_only_declared_transitions() -> None:
    for current, targets in EXCEPTION_TRANSITIONS.items():
        for target in targets:
            validate_exception_transition(current, target)
    for current, target in (
        ("open", "closed"),
        ("closed", "open"),
        ("resolved", "investigating"),
        ("unknown", "resolved"),
    ):
        with pytest.raises(HTTPException) as error:
            validate_exception_transition(current, target)
        assert error.value.status_code == 409
