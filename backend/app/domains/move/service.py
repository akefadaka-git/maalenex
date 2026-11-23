"""Authoritative Move ride lifecycle."""
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.audit.service import record_event
from app.domains.identity.accounts import (
    AccountServiceRoleAssignment, PlatformAccount, TrustEvidence, TrustVerificationCase,
)
from app.domains.identity.models import Role
from app.domains.location.models import LocationSession
from app.domains.organizations.models import Organization
from app.domains.move.models import MoveRide
from app.domains.platform.models import ServiceAreaAvailability


def request_move_ride(db: Session, *, passenger_account_id: UUID, pickup_area_code: str, dropoff_area_code: str) -> MoveRide:
    passenger = db.scalar(
        select(PlatformAccount)
        .where(PlatformAccount.id == passenger_account_id)
        .with_for_update()
    )
    if passenger is None or passenger.status != "active":
        raise ValueError("An active passenger account is required.")
    if not pickup_area_code or not dropoff_area_code:
        raise ValueError("Pickup and destination service areas are required.")
    now = db.scalar(select(func.now()))
    for area_code in {pickup_area_code, dropoff_area_code}:
        policy = db.scalar(select(ServiceAreaAvailability).where(
            ServiceAreaAvailability.service_code == "move",
            ServiceAreaAvailability.area_code == area_code,
            ServiceAreaAvailability.is_enabled.is_(True),
            ServiceAreaAvailability.availability_status.in_(("active", "pilot", "synthetic_test") if settings.app_env == "test" else ("active", "pilot")),
            or_(ServiceAreaAvailability.valid_from.is_(None), ServiceAreaAvailability.valid_from <= now),
            or_(ServiceAreaAvailability.valid_until.is_(None), ServiceAreaAvailability.valid_until > now),
        ))
        if policy is None:
            raise ValueError(f"Move is not authorized to serve area {area_code}.")
    ride = MoveRide(
        passenger_account_id=passenger_account_id, pickup_area_code=pickup_area_code,
        dropoff_area_code=dropoff_area_code, status="requested",
    )
    db.add(ride)
    db.flush()
    record_event(
        db, event_type="move.ride.requested", actor_type="account",
        actor_id=str(passenger_account_id), resource_type="move_ride",
        resource_id=str(ride.id), action="request", outcome="success",
    )
    return ride


def assign_move_driver(
    db: Session, *, ride_id: UUID, driver_account_id: UUID,
    dispatcher_user_id: UUID | None = None,
) -> MoveRide:
    """Trusted dispatch operation; caller must enforce dispatcher authorization."""
    ride = db.scalar(select(MoveRide).where(MoveRide.id == ride_id).with_for_update())
    driver = db.scalar(
        select(PlatformAccount)
        .where(PlatformAccount.id == driver_account_id)
        .with_for_update()
    )
    if ride is None or ride.status != "requested":
        raise ValueError("Only a requested ride can be assigned.")
    if driver is None or driver.status != "active" or driver_account_id == ride.passenger_account_id:
        raise ValueError("An active, distinct driver account is required.")
    now = db.scalar(select(func.now()))
    eligible = db.scalar(
        select(AccountServiceRoleAssignment.id)
        .join(Role, Role.id == AccountServiceRoleAssignment.role_id)
        .join(Organization, Organization.id == AccountServiceRoleAssignment.organization_id)
        .join(
            TrustVerificationCase,
            TrustVerificationCase.account_id == AccountServiceRoleAssignment.account_id,
        )
        .join(TrustEvidence, TrustEvidence.case_id == TrustVerificationCase.id)
        .where(
            AccountServiceRoleAssignment.account_id == driver_account_id,
            AccountServiceRoleAssignment.service_code == "move",
            AccountServiceRoleAssignment.revoked_at.is_(None),
            Role.code == "move_driver",
            Organization.status == "approved",
            TrustVerificationCase.subject_type == "individual",
            TrustVerificationCase.status == "approved",
            TrustEvidence.status == "accepted",
            or_(TrustEvidence.expires_at.is_(None), TrustEvidence.expires_at > now),
        )
        .limit(1)
    )
    if eligible is None:
        raise ValueError(
            "Driver must have an approved individual trust case, accepted current evidence, "
            "an active Move driver role, and an approved operating organization."
        )
    ride.driver_account_id = driver_account_id
    ride.status = "matched"
    ride.matched_at = db.scalar(select(func.now()))
    db.flush()
    record_event(
        db, event_type="move.ride.matched",
        actor_type="staff" if dispatcher_user_id else "system",
        actor_id=str(dispatcher_user_id) if dispatcher_user_id else None,
        resource_type="move_ride", resource_id=str(ride.id),
        action="assign_driver", outcome="success",
    )
    return ride


def transition_move_ride(
    db: Session, *, ride_id: UUID, actor_account_id: UUID, next_status: str,
    cancellation_reason_code: str | None = None,
) -> MoveRide:
    """Enforce participant ownership and monotonic state transitions."""
    ride = db.scalar(select(MoveRide).where(MoveRide.id == ride_id).with_for_update())
    now = db.scalar(select(func.now()))
    if ride is None:
        raise ValueError("Move ride does not exist.")
    transitions = {
        "matched": ("accepted", ride.driver_account_id),
        "accepted": ("arrived", ride.driver_account_id),
        "arrived": ("in_progress", ride.driver_account_id),
        "in_progress": ("completed", ride.driver_account_id),
    }
    if next_status == "cancelled":
        if actor_account_id not in {ride.passenger_account_id, ride.driver_account_id}:
            raise ValueError("Only a ride participant may cancel this ride.")
        if ride.status not in {"requested", "matched", "accepted", "arrived"}:
            raise ValueError("This ride can no longer be cancelled.")
        if not cancellation_reason_code or len(cancellation_reason_code) > 80:
            raise ValueError("A cancellation reason code is required.")
        ride.status = "cancelled"
        ride.cancelled_at = now
        ride.cancellation_reason_code = cancellation_reason_code
    else:
        expected = transitions.get(ride.status)
        if expected is None or expected[0] != next_status or expected[1] != actor_account_id:
            raise ValueError("Move ride transition is not permitted for this actor or state.")
        ride.status = next_status
        timestamp_field = {"accepted": "accepted_at", "arrived": "arrived_at", "in_progress": "started_at", "completed": "completed_at"}[next_status]
        setattr(ride, timestamp_field, now)
    terminated_sessions = 0
    if next_status in {"completed", "cancelled"}:
        sessions = db.scalars(
            select(LocationSession).where(
                LocationSession.service_code == "move",
                LocationSession.resource_type == "move_ride",
                LocationSession.resource_id == str(ride.id),
                LocationSession.status == "active",
            ).with_for_update()
        ).all()
        for session in sessions:
            session.status = "completed"
            session.ended_at = now
        terminated_sessions = len(sessions)

    record_event(
        db, event_type=f"move.ride.{next_status}", actor_type="account",
        actor_id=str(actor_account_id), resource_type="move_ride",
        resource_id=str(ride.id), action=next_status, outcome="success",
        metadata={
            "reason_code": cancellation_reason_code,
            "location_sessions_terminated": terminated_sessions,
        },
    )
    db.flush()
    return ride
