"""Authoritative Move ride lifecycle."""
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.domains.audit.service import record_event
from app.domains.identity.accounts import PlatformAccount
from app.domains.move.models import MoveRide

def request_move_ride(db: Session, *, passenger_account_id: UUID) -> MoveRide:
    passenger = db.scalar(select(PlatformAccount).where(PlatformAccount.id == passenger_account_id).with_for_update())
    if passenger is None or passenger.status != "active":
        raise ValueError("An active passenger account is required.")
    ride = MoveRide(passenger_account_id=passenger_account_id, status="requested")
    db.add(ride); db.flush()
    record_event(db, event_type="move.ride.requested", actor_type="account", actor_id=str(passenger_account_id), resource_type="move_ride", resource_id=str(ride.id), action="request", outcome="success")
    return ride

def assign_move_driver(db: Session, *, ride_id: UUID, driver_account_id: UUID) -> MoveRide:
    """Trusted dispatch operation; caller must enforce dispatcher authorization."""
    ride = db.scalar(select(MoveRide).where(MoveRide.id == ride_id).with_for_update())
    driver = db.scalar(select(PlatformAccount).where(PlatformAccount.id == driver_account_id).with_for_update())
    if ride is None or ride.status != "requested":
        raise ValueError("Only a requested ride can be assigned.")
    if driver is None or driver.status != "active" or driver_account_id == ride.passenger_account_id:
        raise ValueError("An active, distinct driver account is required.")
    ride.driver_account_id = driver_account_id; ride.status = "matched"; ride.matched_at = db.scalar(select(func.now())); db.flush()
    record_event(db, event_type="move.ride.matched", actor_type="system", actor_id=None, resource_type="move_ride", resource_id=str(ride.id), action="assign_driver", outcome="success")
    return ride

def transition_move_ride(db: Session, *, ride_id: UUID, actor_account_id: UUID, next_status: str, cancellation_reason_code: str | None = None) -> MoveRide:
    ride = db.scalar(select(MoveRide).where(MoveRide.id == ride_id).with_for_update())
    now = db.scalar(select(func.now()))
    if ride is None: raise ValueError("Move ride does not exist.")
    transitions = {"matched": ("accepted", ride.driver_account_id), "accepted": ("arrived", ride.driver_account_id), "arrived": ("in_progress", ride.driver_account_id), "in_progress": ("completed", ride.driver_account_id)}
    if next_status == "cancelled":
        if actor_account_id not in {ride.passenger_account_id, ride.driver_account_id}: raise ValueError("Only a ride participant may cancel this ride.")
        if ride.status not in {"requested", "matched", "accepted", "arrived"}: raise ValueError("This ride can no longer be cancelled.")
        if not cancellation_reason_code or len(cancellation_reason_code) > 80: raise ValueError("A cancellation reason code is required.")
        ride.status = "cancelled"; ride.cancelled_at = now; ride.cancellation_reason_code = cancellation_reason_code
    else:
        expected = transitions.get(ride.status)
        if expected is None or expected[0] != next_status or expected[1] != actor_account_id: raise ValueError("Move ride transition is not permitted for this actor or state.")
        ride.status = next_status; setattr(ride, f"{next_status}_at", now)
    record_event(db, event_type=f"move.ride.{next_status}", actor_type="account", actor_id=str(actor_account_id), resource_type="move_ride", resource_id=str(ride.id), action=next_status, outcome="success", metadata={"reason_code": cancellation_reason_code})
    db.flush(); return ride
