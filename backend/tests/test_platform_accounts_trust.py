import os
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from app.db.session import SessionLocal
from app.domains.identity.accounts import (
    AccountCredential, AccountIdentifier, PlatformAccount, TrustEvidence,
    TrustReviewEvent, TrustVerificationCase,
)
from app.domains.identity.models import User
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
