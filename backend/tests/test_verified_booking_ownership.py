from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.domains.audit.models import AuditEvent
from app.domains.bookings.models import Booking, BookingContact, SeatAllocation, SeatHold
from app.domains.bookings.service import BookingConflict, cancel_unconfirmed_booking, claim_booking_for_passenger
from app.domains.identity.passenger_models import PassengerAccount
from app.domains.notifications.models import PassengerNotification, PassengerNotificationPreference


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[
        PassengerAccount.__table__, BookingContact.__table__, Booking.__table__,
        PassengerNotification.__table__, PassengerNotificationPreference.__table__, SeatHold.__table__, SeatAllocation.__table__,
        AuditEvent.__table__,
    ])
    with Session(engine) as session:
        yield session
    engine.dispose()


def _booking(db):
    contact = BookingContact(name="Synthetic Rider", phone_normalized="+251911000001")
    db.add(contact)
    db.flush()
    booking = Booking(
        booking_reference="SYNTHETIC12345", booking_contact_id=contact.id,
        trip_id=uuid4(), status="held", currency_code="ETB", version=1,
    )
    db.add(booking)
    db.flush()
    return booking


def test_booking_claim_links_only_the_authenticated_account_and_notifies(db):
    passenger = PassengerAccount(
        login_identifier="claim-rider@example.test", display_name="Claim Rider",
        status="active",
    )
    db.add(passenger)
    booking = _booking(db)
    db.flush()

    claimed = claim_booking_for_passenger(
        db, booking_id=booking.id, passenger_id=passenger.id,
    )
    db.commit()

    assert claimed.passenger_account_id == passenger.id
    notices = db.query(PassengerNotification).filter_by(passenger_id=passenger.id).all()
    assert len(notices) == 1
    assert notices[0].notification_type == "booking_status"
    assert notices[0].resource_reference == str(booking.id)


def test_booking_cannot_be_claimed_by_a_second_passenger(db):
    first = PassengerAccount(
        login_identifier="first-rider@example.test", display_name="First",
        status="active",
    )
    second = PassengerAccount(
        login_identifier="second-rider@example.test", display_name="Second",
        status="active",
    )
    db.add_all([first, second])
    booking = _booking(db)
    db.flush()
    claim_booking_for_passenger(db, booking_id=booking.id, passenger_id=first.id)
    db.commit()

    with pytest.raises(BookingConflict, match="already linked"):
        claim_booking_for_passenger(db, booking_id=booking.id, passenger_id=second.id)



def test_unconfirmed_booking_cancellation_releases_seats_and_notifies(db):
    passenger = PassengerAccount(
        login_identifier="cancel-rider@example.test", display_name="Cancel Rider",
        status="active",
    )
    db.add(passenger)
    booking = _booking(db)
    booking.passenger_account_id = passenger.id
    seat_id = uuid4()
    booking.expires_at = datetime.now(UTC) + timedelta(minutes=5)
    db.add(SeatHold(
        booking_id=booking.id, trip_id=booking.trip_id, trip_seat_id=seat_id,
        status="active", expires_at=booking.expires_at,
    ))
    db.add(SeatAllocation(
        booking_id=booking.id, booking_passenger_id=uuid4(),
        trip_id=booking.trip_id, trip_seat_id=seat_id, status="active",
    ))
    db.flush()

    cancelled = cancel_unconfirmed_booking(
        db, booking_id=booking.id, actor_type="passenger", actor_id=str(passenger.id),
    )
    db.commit()

    assert cancelled.status == "cancelled"
    assert db.query(SeatHold).filter_by(booking_id=booking.id).one().status == "cancelled"
    assert db.query(SeatAllocation).filter_by(booking_id=booking.id).one().status == "cancelled"
    notice = db.query(PassengerNotification).filter_by(passenger_id=passenger.id).one()
    assert notice.notification_type == "booking_status"
    assert "cancelled" in notice.body


def test_reserved_booking_cancellation_fails_closed_until_policy_exists(db):
    booking = _booking(db)
    booking.status = "reserved"
    db.flush()

    with pytest.raises(BookingConflict, match="approved cancellation policy"):
        cancel_unconfirmed_booking(
            db, booking_id=booking.id, actor_type="guest", actor_id=None,
        )
