from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
import pytest

from app.db.base import Base
from app.domains.audit.models import AuditEvent
from app.domains.identity.models import AuthLoginAttempt, Credential, StaffSession, User
from app.domains.identity.security import hash_secret
from app.domains.identity.service import (
    AuthenticationError, AuthenticationRateLimited, authenticate_staff,
    resolve_staff_session, verify_csrf,
)


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        User.__table__, Credential.__table__, AuthLoginAttempt.__table__,
        StaffSession.__table__, AuditEvent.__table__,
    ])
    with Session(engine) as session:
        yield session
    engine.dispose()


def seed_user(db):
    user = User(login_identifier="operator@example.test", display_name="Synthetic Operator", status="active")
    db.add(user)
    db.flush()
    db.add(Credential(user_id=user.id, credential_type="password",
                      secret_hash=hash_secret("synthetic-password"), status="active"))
    db.commit()
    return user


def test_staff_login_issues_scoped_cookie_and_csrf_secrets(db):
    user = seed_user(db)
    issued = authenticate_staff(
        db, login_identifier="OPERATOR@example.test",
        password="synthetic-password", client_ip="127.0.0.1",
    )
    db.commit()
    assert issued.user.id == user.id
    assert issued.session_token not in issued.session.secret_hash
    context = resolve_staff_session(db, raw_token=issued.session_token)
    assert context.user.id == user.id
    assert verify_csrf(context, cookie_token=issued.csrf_token, header_token=issued.csrf_token)
    assert not verify_csrf(context, cookie_token=issued.csrf_token, header_token="wrong")


def test_invalid_login_is_counted_and_locked_after_five_attempts(db):
    seed_user(db)
    for _ in range(5):
        with pytest.raises(AuthenticationError):
            authenticate_staff(
                db, login_identifier="operator@example.test",
                password="wrong-password", client_ip="127.0.0.1",
            )
        db.commit()
    with pytest.raises(AuthenticationRateLimited):
        authenticate_staff(
            db, login_identifier="operator@example.test",
            password="synthetic-password", client_ip="127.0.0.1",
        )
    attempt = db.scalar(select(AuthLoginAttempt))
    assert attempt.failed_count == 5
    assert attempt.locked_until is not None


def test_revoked_session_is_not_resolved(db):
    issued = authenticate_staff(
        db, login_identifier="operator@example.test",
        password="synthetic-password", client_ip="127.0.0.1",
    ) if db.scalar(select(User)) else None
    if issued is None:
        seed_user(db)
        issued = authenticate_staff(
            db, login_identifier="operator@example.test",
            password="synthetic-password", client_ip="127.0.0.1",
        )
    db.commit()
    issued.session.revoked_at = issued.session.created_at
    db.commit()
    with pytest.raises(AuthenticationError):
        resolve_staff_session(db, raw_token=issued.session_token)
