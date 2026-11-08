from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.bookings.models import Booking, BookingPassenger, Passenger, SeatAllocation
from app.domains.audit.models import AuditEvent
from app.domains.audit.service import record_event
from app.domains.catalog.models import Location, Route, RouteStop, Terminal
from app.domains.fares.models import Fare, FareVersion
from app.domains.fares.service import FareConflict, decide_fare, propose_fare, publish_fare, submit_fare
from app.domains.fleet.models import SeatLayoutVersion, Vehicle, VehicleSeat
from app.domains.identity.authorization import has_permission
from app.domains.identity.models import Role, RoleAssignment, User
from app.domains.organizations.models import Organization, OrganizationInvitation, OrganizationMembership
from app.domains.organizations.service import create_candidate_operator
from app.domains.trips.models import Trip, TripSeat
from app.domains.support.models import SupportCase
from app.routers.auth import current_staff_context, require_csrf
from app.domains.identity.service import StaffContext
from app.domains.identity.security import issue_opaque_token, token_digest

router = APIRouter(tags=["platform-administration"])


class OperatorCreate(BaseModel):
    display_name: str = Field(min_length=2, max_length=200)


class OperatorReview(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=3, max_length=500)


class OperatorRoleAssignment(BaseModel):
    user_id: UUID
    role_code: Literal["synthetic_operator_manager"] = "synthetic_operator_manager"


class SupportResolution(BaseModel):
    resolution_code: str = Field(min_length=3, max_length=80)
    resolution_note: str = Field(min_length=3, max_length=1000)


class OperatorInvitationCreate(BaseModel):
    login_identifier: str = Field(min_length=5, max_length=254)
    display_name: str = Field(min_length=2, max_length=160)


class LocationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    location_type: str = Field(min_length=2, max_length=32)


class TerminalCreate(BaseModel):
    location_id: UUID
    name: str = Field(min_length=2, max_length=160)


class RouteCreate(BaseModel):
    code: str = Field(min_length=2, max_length=60)
    origin_location_id: UUID
    destination_location_id: UUID


class VehicleCreate(BaseModel):
    vehicle_reference: str = Field(min_length=2, max_length=80)


class SeatLayoutCreate(BaseModel):
    seat_codes: list[str] = Field(min_length=1, max_length=60)


class VehicleReview(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=3, max_length=500)


class TripCreate(BaseModel):
    route_id: UUID
    boarding_terminal_id: UUID
    vehicle_id: UUID
    seat_layout_version_id: UUID
    departure_at: datetime
    arrival_estimate_at: datetime | None = None


class FareCreate(BaseModel):
    route_id: UUID
    trip_id: UUID | None = None
    amount_minor_units: int = Field(ge=0)
    effective_from: datetime
    effective_to: datetime | None = None


class FareReview(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=3, max_length=500)


def _authorize(db: Session, context: StaffContext, permission: str,
               organization_id: UUID | None = None) -> None:
    if not has_permission(
        db, user_id=context.user.id, permission_code=permission,
        organization_id=organization_id,
    ):
        raise HTTPException(status_code=403, detail="Required permission is missing.")


def _audit(db: Session, *, context: StaffContext, event: str,
           resource_type: str, resource_id: UUID, action: str,
           outcome: str = "success", organization_id: UUID | None = None,
           reason: str | None = None, metadata: dict | None = None) -> None:
    record_event(
        db, event_type=event, actor_type="staff", actor_id=str(context.user.id),
        actor_role_snapshot=None, resource_type=resource_type,
        resource_id=str(resource_id), action=action, outcome=outcome,
        organization_id=organization_id, reason_code=reason, metadata=metadata,
    )


def _require_mutation(request: Request, context: StaffContext) -> None:
    require_csrf(request, context)


@router.post("/operators", status_code=status.HTTP_201_CREATED)
def create_operator(
    payload: OperatorCreate, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.operator.create")
    operator = create_candidate_operator(db, display_name=payload.display_name, actor_id=context.user.id)
    db.commit()
    return {"id": str(operator.id), "display_name": operator.display_name, "status": operator.status}


@router.post("/operators/{organization_id}/review")
def review_operator(
    organization_id: UUID, payload: OperatorReview, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.operator.review")
    operator = db.scalar(select(Organization).where(Organization.id == organization_id).with_for_update())
    if operator is None or operator.status not in {"candidate", "submitted", "under_review"}:
        raise HTTPException(status_code=409, detail="Operator is not awaiting review.")
    operator.status = payload.decision
    _audit(db, context=context, event="operator.review.completed", resource_type="organization",
           resource_id=operator.id, action="review", organization_id=operator.id,
           reason=f"operator_{payload.decision}", metadata={"review_reason": payload.reason})
    db.commit()
    return {"id": str(operator.id), "status": operator.status}


@router.post("/operators/{organization_id}/role-assignments", status_code=status.HTTP_201_CREATED)
def assign_operator_role(
    organization_id: UUID, payload: OperatorRoleAssignment, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.access.manage")
    operator = db.get(Organization, organization_id)
    user = db.get(User, payload.user_id)
    role = db.scalar(select(Role).where(Role.code == payload.role_code))
    if operator is None or user is None or user.status != "active" or role is None:
        raise HTTPException(status_code=404, detail="Operator, active user or role not found.")
    if operator.status != "approved":
        raise HTTPException(status_code=409, detail="Operator must be approved before staff assignment.")
    membership = db.scalar(select(OrganizationMembership).where(
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.user_id == user.id,
        OrganizationMembership.revoked_at.is_(None),
    ))
    if membership is None:
        membership = OrganizationMembership(organization_id=organization_id, user_id=user.id, membership_status="active")
        db.add(membership)
        db.flush()
    assignment = RoleAssignment(
        user_id=user.id, role_id=role.id, organization_id=organization_id,
        assigned_by=context.user.id,
    )
    db.add(assignment)
    db.flush()
    _audit(db, context=context, event="organization.role.assigned",
           resource_type="role_assignment", resource_id=assignment.id,
           action="assign", organization_id=organization_id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An equivalent active assignment already exists.")
    return {"id": str(assignment.id), "organization_id": str(organization_id), "user_id": str(user.id), "role": role.code}


@router.post("/operators/{organization_id}/invitations", status_code=status.HTTP_201_CREATED)
def create_operator_invitation(
    organization_id: UUID, payload: OperatorInvitationCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.access.manage")
    if settings.app_env not in {"development", "test"} or not settings.synthetic_data_only:
        raise HTTPException(status_code=503, detail="Invitation delivery is not configured.")
    operator = db.get(Organization, organization_id)
    if operator is None or operator.organization_type != "operator" or operator.status != "approved":
        raise HTTPException(status_code=409, detail="Only approved operator organizations can receive staff invitations.")
    login = payload.login_identifier.strip().lower()
    if "@" not in login or any(character.isspace() for character in login):
        raise HTTPException(status_code=422, detail="A valid login email is required.")
    if db.scalar(select(User.id).where(User.login_identifier == login)) is not None:
        raise HTTPException(status_code=409, detail="A staff account already exists for this login.")
    role = db.scalar(select(Role).where(Role.code == "synthetic_operator_manager"))
    if role is None:
        raise HTTPException(status_code=503, detail="Operator manager role has not been provisioned.")
    now = db.scalar(select(func.now()))
    stale = list(db.scalars(select(OrganizationInvitation).where(
        OrganizationInvitation.organization_id == organization_id,
        OrganizationInvitation.login_identifier == login,
        OrganizationInvitation.accepted_at.is_(None),
        OrganizationInvitation.revoked_at.is_(None),
    ).with_for_update()))
    for old_invitation in stale:
        old_invitation.revoked_at = now
    token = issue_opaque_token()
    invitation = OrganizationInvitation(
        organization_id=organization_id, login_identifier=login,
        display_name=payload.display_name.strip(), role_id=role.id,
        token_hash=token_digest(token), created_by=context.user.id,
        expires_at=now + timedelta(hours=48),
    )
    db.add(invitation)
    db.flush()
    _audit(
        db, context=context, event="organization.invitation.created",
        resource_type="organization_invitation", resource_id=invitation.id,
        action="invite", organization_id=organization_id,
        metadata={"role": role.code},
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An active invitation already exists for this login.")
    return {
        "invitation_id": str(invitation.id),
        "login_identifier": invitation.login_identifier,
        "expires_at": invitation.expires_at.isoformat(),
        "delivery": "disabled_synthetic_token_only",
        "synthetic_invitation_token": token,
    }


@router.post("/operators/{organization_id}/invitations/{invitation_id}/revoke")
def revoke_operator_invitation(
    organization_id: UUID, invitation_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.access.manage")
    invitation = db.scalar(select(OrganizationInvitation).where(
        OrganizationInvitation.id == invitation_id,
        OrganizationInvitation.organization_id == organization_id,
    ).with_for_update())
    if invitation is None or invitation.accepted_at is not None or invitation.revoked_at is not None:
        raise HTTPException(status_code=409, detail="Invitation is not revocable.")
    invitation.revoked_at = db.scalar(select(func.now()))
    _audit(
        db, context=context, event="organization.invitation.revoked",
        resource_type="organization_invitation", resource_id=invitation.id,
        action="revoke", organization_id=organization_id,
    )
    db.commit()
    return {"invitation_id": str(invitation.id), "revoked": True}


@router.post("/operators/{organization_id}/memberships/{membership_id}/revoke")
def revoke_operator_membership(
    organization_id: UUID, membership_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.access.manage")
    membership = db.scalar(select(OrganizationMembership).where(
        OrganizationMembership.id == membership_id,
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.revoked_at.is_(None),
    ).with_for_update())
    if membership is None:
        raise HTTPException(status_code=404, detail="Active organization membership not found.")
    now = db.scalar(select(func.now()))
    membership.revoked_at = now
    membership.membership_status = "revoked"
    assignments = list(db.scalars(select(RoleAssignment).where(
        RoleAssignment.user_id == membership.user_id,
        RoleAssignment.organization_id == organization_id,
        RoleAssignment.revoked_at.is_(None),
    ).with_for_update()))
    for assignment in assignments:
        assignment.revoked_at = now
    _audit(
        db, context=context, event="organization.membership.revoked",
        resource_type="organization_membership", resource_id=membership.id,
        action="revoke", organization_id=organization_id,
        metadata={"role_assignments_revoked": len(assignments)},
    )
    db.commit()
    return {"membership_id": str(membership.id), "revoked_role_assignments": len(assignments)}


@router.post("/catalog/locations", status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    location = Location(name=payload.name.strip(), location_type=payload.location_type.strip(), status="draft")
    db.add(location)
    db.flush()
    _audit(db, context=context, event="catalog.location.created", resource_type="location",
           resource_id=location.id, action="create")
    db.commit()
    return {"id": str(location.id), "name": location.name, "status": location.status}


@router.post("/catalog/locations/{location_id}/publish")
def publish_location(
    location_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.publish")
    location = db.scalar(select(Location).where(Location.id == location_id).with_for_update())
    if location is None or location.status != "draft":
        raise HTTPException(status_code=409, detail="Location is not a draft.")
    location.status = "published"
    _audit(db, context=context, event="catalog.location.published", resource_type="location",
           resource_id=location.id, action="publish")
    db.commit()
    return {"id": str(location.id), "status": location.status}


@router.post("/catalog/terminals", status_code=status.HTTP_201_CREATED)
def create_terminal(
    payload: TerminalCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    location = db.get(Location, payload.location_id)
    if location is None or location.status != "published":
        raise HTTPException(status_code=409, detail="Terminal location must be published.")
    terminal = Terminal(location_id=location.id, name=payload.name.strip(), status="draft")
    db.add(terminal)
    db.flush()
    _audit(db, context=context, event="catalog.terminal.created", resource_type="terminal",
           resource_id=terminal.id, action="create")
    db.commit()
    return {"id": str(terminal.id), "name": terminal.name, "status": terminal.status}


@router.post("/catalog/terminals/{terminal_id}/publish")
def publish_terminal(
    terminal_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.publish")
    terminal = db.scalar(select(Terminal).where(Terminal.id == terminal_id).with_for_update())
    if terminal is None or terminal.status != "draft":
        raise HTTPException(status_code=409, detail="Terminal is not a draft.")
    terminal.status = "published"
    _audit(db, context=context, event="catalog.terminal.published", resource_type="terminal",
           resource_id=terminal.id, action="publish")
    db.commit()
    return {"id": str(terminal.id), "status": terminal.status}


@router.post("/catalog/routes", status_code=status.HTTP_201_CREATED)
def create_route(
    payload: RouteCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    if payload.origin_location_id == payload.destination_location_id:
        raise HTTPException(status_code=422, detail="Route origin and destination must differ.")
    locations = list(db.scalars(select(Location).where(
        Location.id.in_([payload.origin_location_id, payload.destination_location_id]),
        Location.status == "published",
    )))
    if len(locations) != 2:
        raise HTTPException(status_code=409, detail="Both route locations must be published.")
    route = Route(
        code=payload.code.strip().upper(), origin_location_id=payload.origin_location_id,
        destination_location_id=payload.destination_location_id, status="draft",
    )
    db.add(route)
    db.flush()
    _audit(db, context=context, event="catalog.route.created", resource_type="route",
           resource_id=route.id, action="create")
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Route code already exists.")
    return {"id": str(route.id), "code": route.code, "status": route.status}


@router.post("/catalog/routes/{route_id}/publish")
def publish_route(
    route_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.publish")
    route = db.scalar(select(Route).where(Route.id == route_id).with_for_update())
    if route is None or route.status != "draft":
        raise HTTPException(status_code=409, detail="Route is not a draft.")
    route.status = "published"
    db.add_all([
        RouteStop(route_id=route.id, location_id=route.origin_location_id, sequence_number=1,
                  boarding_allowed=True, alighting_allowed=False, status="published"),
        RouteStop(route_id=route.id, location_id=route.destination_location_id, sequence_number=2,
                  boarding_allowed=False, alighting_allowed=True, status="published"),
    ])
    _audit(db, context=context, event="catalog.route.published", resource_type="route",
           resource_id=route.id, action="publish")
    db.commit()
    return {"id": str(route.id), "status": route.status}


@router.post("/operators/{organization_id}/vehicles", status_code=status.HTTP_201_CREATED)
def create_vehicle(
    organization_id: UUID, payload: VehicleCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "operator.fleet.manage", organization_id)
    operator = db.get(Organization, organization_id)
    if operator is None or operator.status != "approved":
        raise HTTPException(status_code=409, detail="Operator must be approved before fleet setup.")
    vehicle = Vehicle(
        organization_id=organization_id, vehicle_reference=payload.vehicle_reference.strip(),
        status="draft", review_status="pending",
    )
    db.add(vehicle)
    db.flush()
    _audit(db, context=context, event="fleet.vehicle.created", resource_type="vehicle",
           resource_id=vehicle.id, action="create", organization_id=organization_id)
    db.commit()
    return {"id": str(vehicle.id), "status": vehicle.status, "review_status": vehicle.review_status}


@router.post("/vehicles/{vehicle_id}/seat-layouts", status_code=status.HTTP_201_CREATED)
def create_seat_layout(
    vehicle_id: UUID, payload: SeatLayoutCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    _authorize(db, context, "operator.fleet.manage", vehicle.organization_id)
    codes = [item.strip().upper() for item in payload.seat_codes]
    if any(not item or len(item) > 16 for item in codes) or len(set(codes)) != len(codes):
        raise HTTPException(status_code=422, detail="Seat codes must be unique and 1–16 characters.")
    latest = db.scalar(select(func.max(SeatLayoutVersion.version_number)).where(
        SeatLayoutVersion.vehicle_id == vehicle.id
    )) or 0
    layout = SeatLayoutVersion(vehicle_id=vehicle.id, version_number=latest + 1, status="draft")
    db.add(layout)
    db.flush()
    db.add_all([
        VehicleSeat(seat_layout_version_id=layout.id, seat_code=code, position_metadata={},
                    seat_type="standard", is_sellable=True)
        for code in codes
    ])
    _audit(db, context=context, event="fleet.seat_layout.created", resource_type="seat_layout_version",
           resource_id=layout.id, action="create", organization_id=vehicle.organization_id)
    db.commit()
    return {"id": str(layout.id), "version_number": layout.version_number, "seat_count": len(codes), "status": layout.status}


@router.post("/vehicles/{vehicle_id}/review")
def review_vehicle(
    vehicle_id: UUID, payload: VehicleReview, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.fleet.review")
    vehicle = db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id).with_for_update())
    if vehicle is None or vehicle.review_status != "pending":
        raise HTTPException(status_code=409, detail="Vehicle is not awaiting review.")
    vehicle.review_status = payload.decision
    vehicle.status = "active" if payload.decision == "approved" else "rejected"
    _audit(db, context=context, event="fleet.vehicle.reviewed", resource_type="vehicle",
           resource_id=vehicle.id, action="review", organization_id=vehicle.organization_id, reason=payload.reason)
    db.commit()
    return {"id": str(vehicle.id), "status": vehicle.status, "review_status": vehicle.review_status}


@router.post("/seat-layouts/{layout_id}/approve")
def approve_seat_layout(
    layout_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.fleet.review")
    layout = db.scalar(select(SeatLayoutVersion).where(SeatLayoutVersion.id == layout_id).with_for_update())
    if layout is None or layout.status != "draft":
        raise HTTPException(status_code=409, detail="Seat layout is not a draft.")
    vehicle = db.get(Vehicle, layout.vehicle_id)
    if vehicle is None or vehicle.review_status != "approved":
        raise HTTPException(status_code=409, detail="Vehicle must be approved before its seat layout.")
    layout.status = "approved"
    _audit(db, context=context, event="fleet.seat_layout.approved",
           resource_type="seat_layout_version", resource_id=layout.id,
           action="approve", organization_id=vehicle.organization_id)
    db.commit()
    return {"id": str(layout.id), "status": layout.status}


@router.post("/operators/{organization_id}/trips", status_code=status.HTTP_201_CREATED)
def create_trip(
    organization_id: UUID, payload: TripCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "operator.trip.manage", organization_id)
    if payload.departure_at.tzinfo is None or (payload.arrival_estimate_at and payload.arrival_estimate_at.tzinfo is None):
        raise HTTPException(status_code=422, detail="Trip timestamps must include a timezone.")
    if payload.arrival_estimate_at is not None and payload.arrival_estimate_at <= payload.departure_at:
        raise HTTPException(status_code=422, detail="Arrival estimate must be later than departure.")
    operator = db.get(Organization, organization_id)
    route = db.get(Route, payload.route_id)
    terminal = db.get(Terminal, payload.boarding_terminal_id)
    vehicle = db.get(Vehicle, payload.vehicle_id)
    layout = db.get(SeatLayoutVersion, payload.seat_layout_version_id)
    if operator is None or operator.status != "approved":
        raise HTTPException(status_code=409, detail="Operator is not approved.")
    if route is None or route.status != "published":
        raise HTTPException(status_code=409, detail="Route is not published.")
    if terminal is None or terminal.status != "published" or terminal.location_id != route.origin_location_id:
        raise HTTPException(status_code=409, detail="Boarding terminal must be published at the route origin.")
    if vehicle is None or vehicle.organization_id != organization_id or vehicle.status != "active" or vehicle.review_status != "approved":
        raise HTTPException(status_code=409, detail="Vehicle must be approved and belong to this operator.")
    if layout is None or layout.vehicle_id != vehicle.id or layout.status != "approved":
        raise HTTPException(status_code=409, detail="Seat layout must be approved for the selected vehicle.")
    trip = Trip(
        organization_id=organization_id, route_id=route.id,
        boarding_terminal_id=terminal.id, vehicle_id=vehicle.id,
        seat_layout_version_id=layout.id, departure_at=payload.departure_at,
        arrival_estimate_at=payload.arrival_estimate_at, status="draft",
    )
    db.add(trip)
    db.flush()
    seats = db.scalars(select(VehicleSeat).where(
        VehicleSeat.seat_layout_version_id == layout.id,
        VehicleSeat.is_sellable.is_(True),
    ).order_by(VehicleSeat.seat_code)).all()
    if not seats:
        raise HTTPException(status_code=409, detail="Approved seat layout has no sellable seats.")
    db.add_all([
        TripSeat(trip_id=trip.id, vehicle_seat_id=seat.id,
                 seat_code_snapshot=seat.seat_code, sellable_status="sellable")
        for seat in seats
    ])
    _audit(db, context=context, event="trip.created", resource_type="trip",
           resource_id=trip.id, action="create", organization_id=organization_id)
    db.commit()
    return {"id": str(trip.id), "status": trip.status, "seat_count": len(seats)}


@router.post("/trips/{trip_id}/submit")
def submit_trip(
    trip_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    trip = db.scalar(select(Trip).where(Trip.id == trip_id).with_for_update())
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    _authorize(db, context, "operator.trip.manage", trip.organization_id)
    if trip.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft trips can be submitted.")
    trip.status = "submitted"
    _audit(db, context=context, event="trip.submitted", resource_type="trip",
           resource_id=trip.id, action="submit", organization_id=trip.organization_id)
    db.commit()
    return {"id": str(trip.id), "status": trip.status}


@router.post("/trips/{trip_id}/approve")
def approve_trip(
    trip_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.trip.approve")
    trip = db.scalar(select(Trip).where(Trip.id == trip_id).with_for_update())
    if trip is None or trip.status != "submitted":
        raise HTTPException(status_code=409, detail="Only submitted trips can be approved.")
    trip.status = "approved"
    _audit(db, context=context, event="trip.approved", resource_type="trip",
           resource_id=trip.id, action="approve", organization_id=trip.organization_id)
    db.commit()
    return {"id": str(trip.id), "status": trip.status}



@router.get("/trips/{trip_id}/manifest")
def read_trip_manifest(
    trip_id: UUID,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    _authorize(db, context, "operator.trip.manifest.read", trip.organization_id)
    rows = db.execute(
        select(
            Booking.booking_reference,
            Passenger.display_name,
            TripSeat.seat_code_snapshot,
            BookingPassenger.passenger_sequence,
        )
        .join(BookingPassenger, BookingPassenger.booking_id == Booking.id)
        .join(Passenger, Passenger.id == BookingPassenger.passenger_id)
        .join(SeatAllocation, SeatAllocation.booking_passenger_id == BookingPassenger.id)
        .join(TripSeat, TripSeat.id == SeatAllocation.trip_seat_id)
        .where(
            Booking.trip_id == trip_id,
            Booking.status == "reserved",
            BookingPassenger.trip_seat_id == TripSeat.id,
            TripSeat.trip_id == trip_id,
            SeatAllocation.trip_id == trip_id,
            SeatAllocation.status == "active",
        )
        .order_by(TripSeat.seat_code_snapshot, BookingPassenger.passenger_sequence)
    ).all()
    _audit(
        db, context=context, event="trip.manifest.accessed",
        resource_type="trip", resource_id=trip.id, action="read_manifest",
        organization_id=trip.organization_id,
        metadata={"manifest_passenger_count": len(rows)},
    )
    db.commit()
    return {
        "trip_id": str(trip.id),
        "boarding_terminal_id": str(trip.boarding_terminal_id),
        "passenger_count": len(rows),
        "manifest": [
            {
                "booking_reference": booking_reference,
                "passenger_name": passenger_name,
                "seat_code": seat_code,
                "sequence": sequence,
            }
            for booking_reference, passenger_name, seat_code, sequence in rows
        ],
        "contact_phone_included": False,
        "boarding_authorized": False,
    }


@router.post("/trips/{trip_id}/publish")
def publish_trip(
    trip_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.trip.publish")
    trip = db.scalar(select(Trip).where(Trip.id == trip_id).with_for_update())
    if trip is None or trip.status != "approved":
        raise HTTPException(status_code=409, detail="Only approved trips can be published.")
    fare = db.scalar(select(FareVersion).join(Fare, Fare.id == FareVersion.fare_id).where(
        Fare.organization_id == trip.organization_id, Fare.route_id == trip.route_id,
        (Fare.trip_id == trip.id) | (Fare.trip_id.is_(None)),
        FareVersion.status == "published", FareVersion.currency_code == "ETB",
        FareVersion.effective_from <= func.now(),
        (FareVersion.effective_to.is_(None)) | (FareVersion.effective_to > func.now()),
    ).order_by(Fare.trip_id.is_not(None).desc(), FareVersion.effective_from.desc()).limit(1))
    if fare is None:
        raise HTTPException(status_code=409, detail="A published ETB fare is required before trip publication.")
    trip.status = "published"
    trip.published_at = db.scalar(select(func.now()))
    _audit(db, context=context, event="trip.published", resource_type="trip",
           resource_id=trip.id, action="publish", organization_id=trip.organization_id)
    db.commit()
    return {"id": str(trip.id), "status": trip.status}


@router.post("/operators/{organization_id}/fares", status_code=status.HTTP_201_CREATED)
def create_fare(
    organization_id: UUID, payload: FareCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "operator.fare.propose", organization_id)
    try:
        version = propose_fare(
            db, organization_id=organization_id, route_id=payload.route_id,
            trip_id=payload.trip_id, proposed_by=context.user.id,
            amount_minor_units=payload.amount_minor_units,
            effective_from=payload.effective_from, effective_to=payload.effective_to,
        )
        db.commit()
    except (ValueError, FareConflict) as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc))
    return {"id": str(version.id), "fare_id": str(version.fare_id), "version_number": version.version_number, "status": version.status}


@router.post("/fares/{fare_id}/versions/{version_id}/submit")
def submit_fare_version(
    fare_id: UUID, version_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    version = db.get(FareVersion, version_id)
    fare = db.get(Fare, fare_id)
    if fare is None or version is None or version.fare_id != fare.id:
        raise HTTPException(status_code=404, detail="Fare version not found.")
    _authorize(db, context, "operator.fare.propose", fare.organization_id)
    try:
        updated = submit_fare(db, fare_version_id=version.id, proposer_id=context.user.id)
        db.commit()
    except FareConflict as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))
    return {"id": str(updated.id), "status": updated.status}


@router.post("/fares/{fare_id}/versions/{version_id}/review")
def review_fare_version(
    fare_id: UUID, version_id: UUID, payload: FareReview, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.fare.approve")
    fare = db.get(Fare, fare_id)
    version = db.get(FareVersion, version_id)
    if fare is None or version is None or version.fare_id != fare.id:
        raise HTTPException(status_code=404, detail="Fare version not found.")
    try:
        approval = decide_fare(
            db, fare_version_id=version.id, reviewer_id=context.user.id,
            decision=payload.decision, reason=payload.reason,
        )
        db.commit()
    except (ValueError, FareConflict) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))
    return {"approval_id": str(approval.id), "fare_version_id": str(version.id), "decision": approval.decision}


@router.post("/fares/{fare_id}/versions/{version_id}/publish")
def publish_fare_version(
    fare_id: UUID, version_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.fare.publish")
    fare = db.get(Fare, fare_id)
    version = db.get(FareVersion, version_id)
    if fare is None or version is None or version.fare_id != fare.id:
        raise HTTPException(status_code=404, detail="Fare version not found.")
    try:
        published = publish_fare(db, fare_version_id=version.id, publisher_id=context.user.id)
        db.commit()
    except FareConflict as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))
    return {"id": str(published.id), "status": published.status}


@router.get("/support/cases")
def list_support_cases(
    case_status: Literal["open", "in_progress", "resolved", "closed"] | None = None,
    limit: int = 100,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.support.manage")
    statement = select(SupportCase).order_by(SupportCase.created_at.asc())
    if case_status:
        statement = statement.where(SupportCase.status == case_status)
    cases = db.scalars(statement.limit(max(1, min(limit, 200)))).all()
    return [{
        "id": str(case.id),
        "case_reference": case.case_reference,
        "booking_id": str(case.booking_id),
        "category": case.category,
        "subject": case.subject,
        "message": case.message,
        "status": case.status,
        "assigned_to": str(case.assigned_to) if case.assigned_to else None,
        "created_at": case.created_at.isoformat(),
    } for case in cases]


@router.post("/support/cases/{case_id}/claim")
def claim_support_case(
    case_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.support.manage")
    case = db.scalar(select(SupportCase).where(
        SupportCase.id == case_id
    ).with_for_update())
    if case is None or case.status not in {"open", "in_progress"}:
        raise HTTPException(status_code=409, detail="Support case is not available for assignment.")
    if case.assigned_to not in {None, context.user.id}:
        raise HTTPException(status_code=409, detail="Support case is assigned to another staff member.")
    case.assigned_to = context.user.id
    case.status = "in_progress"
    _audit(
        db, context=context, event="support.case.claimed",
        resource_type="support_case", resource_id=case.id,
        action="claim", metadata={"category": case.category},
    )
    db.commit()
    return {"case_reference": case.case_reference, "status": case.status}


@router.post("/support/cases/{case_id}/resolve")
def resolve_support_case(
    case_id: UUID, payload: SupportResolution, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.support.manage")
    case = db.scalar(select(SupportCase).where(
        SupportCase.id == case_id
    ).with_for_update())
    if case is None or case.status not in {"open", "in_progress"}:
        raise HTTPException(status_code=409, detail="Support case is not open.")
    if case.assigned_to not in {None, context.user.id}:
        raise HTTPException(status_code=403, detail="Support case is assigned to another staff member.")
    now = db.scalar(select(func.now()))
    case.assigned_to = context.user.id
    case.status = "resolved"
    case.resolution_code = payload.resolution_code.strip()
    case.resolution_note = payload.resolution_note.strip()
    case.resolved_at = now
    _audit(
        db, context=context, event="support.case.resolved",
        resource_type="support_case", resource_id=case.id,
        action="resolve", metadata={"resolution_code": case.resolution_code},
    )
    db.commit()
    return {
        "case_reference": case.case_reference,
        "status": case.status,
        "resolved_at": case.resolved_at.isoformat(),
    }


@router.get("/audit/events")
def list_audit_events(
    limit: int = 100, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.audit.read")
    bounded = max(1, min(limit, 200))
    events = db.scalars(select(AuditEvent).order_by(AuditEvent.occurred_at.desc()).limit(bounded)).all()
    return [{
        "id": str(item.id), "event_type": item.event_type,
        "occurred_at": item.occurred_at.isoformat(), "actor_type": item.actor_type,
        "actor_id": item.actor_id, "resource_type": item.resource_type,
        "resource_id": item.resource_id, "action": item.action,
        "outcome": item.outcome, "reason_code": item.reason_code,
        "metadata": item.metadata_redacted,
    } for item in events]
