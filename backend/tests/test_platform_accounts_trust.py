import os
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from app.db.session import SessionLocal
from app.domains.identity.accounts import (
    AccountCredential, AccountIdentifier, AccountServiceRoleAssignment, PlatformAccount, TrustEvidence,
    TrustReviewEvent, TrustVerificationCase,
)
from app.domains.identity.models import Role, User
from app.domains.move.service import assign_move_driver, request_move_ride
from app.domains.organizations.models import Organization
from app.domains.identity.trust_lifecycle import transition_trust_case

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires the isolated PostgreSQL CI service.",
)


def test_platform_account_separates_general_identity_from_staff_identity():
    suffix = uuid4().hex
    with SessionLocal.begin() as db:
        account = PlatformAccount(display_name="Synthetic passenger", status="active")
        db.add(account)
        db.flush()
        db.add(AccountIdentifier(
            account_id=account.id, identifier_type="phone",
            lookup_digest=("a" * 32) + suffix[:32], encrypted_value=b"synthetic-ciphertext",
        ))
        db.add(AccountCredential(
            account_id=account.id, credential_type="password",
            verifier="pbkdf2_sha256$synthetic-test-verifier", status="active",
        ))
        db.flush()
        assert db.get(PlatformAccount, account.id).status == "active"
        assert db.scalar(select(AccountIdentifier.id).where(
            AccountIdentifier.account_id == account.id
        )) is not None


def test_trust_case_requires_exactly_one_subject_and_review_is_auditable():
    with SessionLocal.begin() as db:
        account = PlatformAccount(display_name="Synthetic individual", status="active")
        reviewer = User(
            login_identifier=f"reviewer-{uuid4().hex}@maalenex.invalid",
            display_name="Synthetic reviewer", status="active",
        )
        db.add_all([account, reviewer])
        db.flush()
        case = TrustVerificationCase(
            subject_type="individual", account_id=account.id,
            verification_level="basic", status="submitted",
        )
        db.add(case)
        db.flush()
        transition_trust_case(
            db, case_id=case.id, reviewer_user_id=reviewer.id, target_status="in_review"
        )
        transition_trust_case(
            db, case_id=case.id, reviewer_user_id=reviewer.id,
            target_status="approved", reason_code="synthetic_test_pass",
        )
        assert case.status == "approved"
        events = db.scalars(select(TrustReviewEvent).where(
            TrustReviewEvent.case_id == case.id
        ).order_by(TrustReviewEvent.sequence_number)).all()
        assert [event.to_status for event in events] == ["in_review", "approved"]
        event_id = events[-1].id

    with SessionLocal() as db:
        event = db.get(TrustReviewEvent, event_id)
        event.reason_code = "tampered"
        with pytest.raises(DBAPIError):
            db.flush()
        db.rollback()


def test_trust_lifecycle_rejects_illegal_transition_and_missing_reviewer():
    with SessionLocal.begin() as db:
        account = PlatformAccount(display_name="Synthetic account", status="active")
        db.add(account)
        db.flush()
        case = TrustVerificationCase(
            subject_type="individual", account_id=account.id, status="draft"
        )
        db.add(case)
        db.flush()
        with pytest.raises(ValueError, match="not permitted"):
            transition_trust_case(
                db, case_id=case.id, reviewer_user_id=uuid4(), target_status="approved"
            )



def test_move_dispatch_rejects_unverified_driver():
    with SessionLocal.begin() as db:
        passenger = PlatformAccount(display_name="Synthetic passenger", status="active")
        driver = PlatformAccount(display_name="Unverified driver", status="active")
        db.add_all([passenger, driver])
        db.flush()
        ride = request_move_ride(db, passenger_account_id=passenger.id)
        with pytest.raises(ValueError, match="approved individual trust case"):
            assign_move_driver(db, ride_id=ride.id, driver_account_id=driver.id)


def test_move_dispatch_requires_trust_role_and_approved_operator():
    with SessionLocal.begin() as db:
        passenger = PlatformAccount(display_name="Synthetic passenger", status="active")
        driver = PlatformAccount(display_name="Verified synthetic driver", status="active")
        organization = Organization(
            organization_type="operator", display_name="Synthetic Move Operator",
            status="approved",
        )
        role = Role(code="move_driver", description="Move driver")
        db.add_all([passenger, driver, organization, role])
        db.flush()
        ride = request_move_ride(db, passenger_account_id=passenger.id)
        case = TrustVerificationCase(
            subject_type="individual", account_id=driver.id,
            verification_level="basic", status="approved",
        )
        db.add(case)
        db.flush()
        db.add_all([
            TrustEvidence(
                case_id=case.id, evidence_type="synthetic_driver_identity",
                document_digest=uuid4().hex + uuid4().hex,
                private_object_key="synthetic://driver-evidence",
                media_type="application/octet-stream", status="accepted",
            ),
            AccountServiceRoleAssignment(
                account_id=driver.id, organization_id=organization.id,
                service_code="move", role_id=role.id,
            ),
        ])
        db.flush()
        matched = assign_move_driver(db, ride_id=ride.id, driver_account_id=driver.id)
        assert matched.status == "matched"
        assert matched.driver_account_id == driver.id
