from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
import pytest

from app.db.base import Base
from app.domains.audit.models import AuditEvent
from app.domains.identity.models import User, Credential
from app.domains.identity.passenger_models import PassengerAccount, PassengerCredential, PassengerLoginAttempt, PassengerSession
from app.domains.identity.passenger_service import (
    PassengerAuthenticationError, PassengerRateLimited, create_passenger_session,
    register_passenger, resolve_passenger_session, verify_passenger_csrf,
)

@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        User.__table__, Credential.__table__, PassengerAccount.__table__,
        PassengerCredential.__table__, PassengerLoginAttempt.__table__,
        PassengerSession.__table__, AuditEvent.__table__,
    ])
    with Session(engine) as session:
        yield session
    engine.dispose()

def test_registration_and_login_use_isolated_passenger_identity(db):
    passenger = register_passenger(db, login_identifier="rider@example.test", display_name="Synthetic Rider", password="correct-horse-battery")
    issued = create_passenger_session(db, login_identifier="rider@example.test", password="correct-horse-battery", client_ip="127.0.0.1")
    db.commit()
    assert issued.passenger.id == passenger.id
    assert db.scalar(select(User.id)) is None
    context = resolve_passenger_session(db, raw_token=issued.session_token)
    assert context.passenger.id == passenger.id
    assert verify_passenger_csrf(context, cookie_token=issued.csrf_token, header_token=issued.csrf_token)
    assert not verify_passenger_csrf(context, cookie_token=issued.csrf_token, header_token="wrong")

def test_duplicate_registration_is_rejected(db):
    register_passenger(db, login_identifier="rider@example.test", display_name="First Rider", password="correct-horse-battery")
    db.commit()
    with pytest.raises(PassengerAuthenticationError, match="account_exists"):
        register_passenger(db, login_identifier="rider@example.test", display_name="Second Rider", password="correct-horse-battery")

def test_failed_login_throttles_after_five_attempts(db):
    register_passenger(db, login_identifier="rider@example.test", display_name="Synthetic Rider", password="correct-horse-battery")
    db.commit()
    for _ in range(5):
        with pytest.raises(PassengerAuthenticationError):
            create_passenger_session(db, login_identifier="rider@example.test", password="incorrect-password", client_ip="127.0.0.1")
        db.commit()
    with pytest.raises(PassengerRateLimited):
        create_passenger_session(db, login_identifier="rider@example.test", password="correct-horse-battery", client_ip="127.0.0.1")
    assert db.scalar(select(PassengerLoginAttempt)).failed_count == 5

def test_revoked_session_is_rejected(db):
    register_passenger(db, login_identifier="rider@example.test", display_name="Synthetic Rider", password="correct-horse-battery")
    issued = create_passenger_session(db, login_identifier="rider@example.test", password="correct-horse-battery", client_ip="127.0.0.1")
    db.commit()
    from datetime import datetime, timezone
    issued.session.revoked_at = datetime.now(timezone.utc)
    db.commit()
    with pytest.raises(PassengerAuthenticationError):
        resolve_passenger_session(db, raw_token=issued.session_token)
