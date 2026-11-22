"""Platform administration and staff workflow endpoints."""
# FastAPI dependency injection requires Depends instances in endpoint defaults.
# ruff: noqa: B008, I001
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.audit.models import AuditEvent
from app.domains.audit.service import record_event
from app.domains.bookings.models import Booking, BookingPassenger, Passenger, SeatAllocation
from app.domains.catalog.models import Location, Route, RouteStop, Terminal
from app.domains.fares.models import Fare, FareApproval, FareVersion
from app.domains.fares.service import FareConflict, decide_fare, propose_fare, publish_fare, submit_fare
from app.domains.fleet.models import SeatLayoutVersion, Vehicle, VehicleComplianceDocument, VehicleSeat
from app.domains.identity.authorization import has_permission
from app.domains.identity.models import Role, RoleAssignment, User
from app.domains.identity.security import issue_opaque_token, token_digest
from app.domains.identity.service import StaffContext
from app.domains.organizations.models import Organization, OrganizationInvitation, OrganizationMembership
from app.domains.organizations.service import create_candidate_operator
from app.domains.support.models import SupportCase
from app.domains.support.passenger_models import PassengerSupportCase
from app.domains.support.report_models import PassengerReport, PassengerReportAttachment
from app.domains.trips.models import Schedule, Trip, TripOperationalException, TripSeat
from app.routers.auth import current_staff_context, require_csrf

router = APIRouter(tags=["platform-administration"])


class OperatorCreate(BaseModel):
    display_name: str = Field(min_length=2, max_length=200)


class OperatorReview(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=3, max_length=500)


class OperatorRoleAssignment(BaseModel):
    user_id: UUID
    role_code: Literal["synthetic_operator_manager", "operator_manager", "operator_dispatcher", "operator_fleet_manager", "operator_fare_manager"] = "synthetic_operator_manager"


class SupportResolution(BaseModel):
    resolution_code: str = Field(min_length=3, max_length=80)
    resolution_note: str = Field(min_length=3, max_length=1000)


class ReportReview(BaseModel):
    status: Literal["under_review", "action_required", "resolved", "dismissed"]
    resolution_note: str = Field(min_length=3, max_length=1000)


class OperatorInvitationCreate(BaseModel):
    login_identifier: str = Field(min_length=5, max_length=254)
    display_name: str = Field(min_length=2, max_length=160)
    role_code: Literal["synthetic_operator_manager", "operator_manager", "operator_dispatcher", "operator_fleet_manager", "operator_fare_manager"] = "synthetic_operator_manager"


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





class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    location_type: str | None = Field(default=None, min_length=2, max_length=32)


class TerminalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    location_id: UUID | None = None


class RouteUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=60)
    origin_location_id: UUID | None = None
    destination_location_id: UUID | None = None


class RouteStopInput(BaseModel):
    location_id: UUID
    boarding_allowed: bool = False
    alighting_allowed: bool = False


class RouteStopsUpdate(BaseModel):
    stops: list[RouteStopInput] = Field(min_length=2, max_length=100)


class VehicleCreate(BaseModel):
    vehicle_reference: str = Field(min_length=2, max_length=80)


class VehicleUpdate(BaseModel):
    vehicle_reference: str = Field(min_length=2, max_length=80)


class SeatDefinition(BaseModel):
    seat_code: str = Field(min_length=1, max_length=16)
    row_label: str | None = Field(default=None, max_length=12)
    column_index: int = Field(ge=0, le=20)
    x: int | None = Field(default=None, ge=0, le=100)
    y: int | None = Field(default=None, ge=0, le=100)
    seat_type: Literal["standard", "premium", "accessible"] = "standard"
    is_sellable: bool = True


class LayoutMarker(BaseModel):
    kind: Literal["aisle", "door"]
    x: int = Field(ge=0, le=100)
    y: int = Field(ge=0, le=100)
    label: str | None = Field(default=None, max_length=40)


class SeatLayoutGeometry(BaseModel):
    width: int = Field(default=100, ge=1, le=100)
    height: int = Field(default=100, ge=1, le=100)
    markers: list[LayoutMarker] = Field(default_factory=list, max_length=30)


class SeatLayoutCreate(BaseModel):
    seat_codes: list[str] = Field(default_factory=list, max_length=60)
    seats: list[SeatDefinition] = Field(default_factory=list, max_length=60)
    geometry: SeatLayoutGeometry = Field(default_factory=SeatLayoutGeometry)


class VehicleReview(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=3, max_length=500)


class ComplianceEvidenceCreate(BaseModel):
    document_type: Literal["registration", "insurance", "roadworthiness", "operating_permit", "other"]
    evidence_reference: str = Field(min_length=8, max_length=255)
    issued_at: datetime | None = None
    expires_at: datetime | None = None


class ComplianceEvidenceReview(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str = Field(min_length=3, max_length=500)


class OperationalExceptionCreate(BaseModel):
    category: Literal["vehicle_breakdown", "late_departure", "route_disruption", "safety_concern", "passenger_incident", "other"]
    severity: Literal["normal", "high", "critical"] = "normal"
    description: str = Field(min_length=5, max_length=1000)


class OperationalExceptionResolution(BaseModel):
    resolution: str = Field(min_length=5, max_length=1000)


class TripCreate(BaseModel):
    route_id: UUID
    boarding_terminal_id: UUID
    vehicle_id: UUID
    seat_layout_version_id: UUID
    departure_at: datetime
    arrival_estimate_at: datetime | None = None


class TripDraftUpdate(TripCreate):
    pass


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
    elif membership.membership_status != "active":
        raise HTTPException(status_code=409, detail="Operator membership is not active.")
    duplicate = db.scalar(select(RoleAssignment.id).where(
        RoleAssignment.user_id == user.id, RoleAssignment.role_id == role.id,
        RoleAssignment.organization_id == organization_id,
        RoleAssignment.revoked_at.is_(None),
    ))
    if duplicate:
        raise HTTPException(status_code=409, detail="An equivalent active assignment already exists.")
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
    role = db.scalar(select(Role).where(Role.code == payload.role_code))
    if role is None:
        raise HTTPException(status_code=503, detail="Selected operator role has not been provisioned.")
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
    db.add_all([
        RouteStop(route_id=route.id, location_id=route.origin_location_id, sequence_number=1,
                  boarding_allowed=True, alighting_allowed=False, status="draft"),
        RouteStop(route_id=route.id, location_id=route.destination_location_id, sequence_number=2,
                  boarding_allowed=False, alighting_allowed=True, status="draft"),
    ])
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
    stops = list(db.scalars(select(RouteStop).where(
        RouteStop.route_id == route.id
    ).order_by(RouteStop.sequence_number).with_for_update()))
    if not stops:
        stops = [
            RouteStop(route_id=route.id, location_id=route.origin_location_id, sequence_number=1,
                      boarding_allowed=True, alighting_allowed=False, status="draft"),
            RouteStop(route_id=route.id, location_id=route.destination_location_id, sequence_number=2,
                      boarding_allowed=False, alighting_allowed=True, status="draft"),
        ]
        db.add_all(stops)
        db.flush()
    if len(stops) < 2 or stops[0].location_id != route.origin_location_id or stops[-1].location_id != route.destination_location_id:
        raise HTTPException(status_code=409, detail="Route stops must begin at the origin and end at the destination.")
    for stop in stops:
        stop.status = "published"
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
    if operator is None or operator.organization_type != "operator" or operator.status != "approved":
        raise HTTPException(status_code=409, detail="An approved operator organization is required for fleet setup.")
    vehicle_reference = payload.vehicle_reference.strip()
    if db.scalar(select(Vehicle.id).where(
        Vehicle.organization_id == organization_id,
        Vehicle.vehicle_reference == vehicle_reference,
    ).limit(1)):
        raise HTTPException(status_code=409, detail="Vehicle reference already exists for this operator.")
    vehicle = Vehicle(
        organization_id=organization_id, vehicle_reference=vehicle_reference,
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
    if vehicle.status != "active" or vehicle.review_status != "approved":
        raise HTTPException(status_code=409, detail="Vehicle must be approved before creating a seat layout.")
    if bool(payload.seat_codes) == bool(payload.seats):
        raise HTTPException(status_code=422, detail="Provide either seat_codes or structured seats.")
    if payload.seats:
        seat_rows = [{
            "seat_code": item.seat_code.strip().upper(),
            "row_label": item.row_label.strip().upper() if item.row_label else None,
            "column_index": item.column_index, "x": item.x, "y": item.y,
            "seat_type": item.seat_type.strip().lower(), "is_sellable": item.is_sellable,
        } for item in payload.seats]
    else:
        seat_rows = [{
            "seat_code": code.strip().upper(), "row_label": None,
            "column_index": index, "x": None, "y": None, "seat_type": "standard", "is_sellable": True,
        } for index, code in enumerate(payload.seat_codes)]
    codes = [item["seat_code"] for item in seat_rows]
    positions = [(item["row_label"], item["column_index"]) for item in seat_rows if item["row_label"] is not None]
    if any(not code or len(code) > 16 for code in codes) or len(set(codes)) != len(codes):
        raise HTTPException(status_code=422, detail="Seat codes must be unique and 1–16 characters.")
    if len(set(positions)) != len(positions):
        raise HTTPException(status_code=422, detail="Seat positions must be unique within each row.")
    latest = db.scalar(select(func.max(SeatLayoutVersion.version_number)).where(
        SeatLayoutVersion.vehicle_id == vehicle.id
    )) or 0
    layout = SeatLayoutVersion(
        vehicle_id=vehicle.id, version_number=latest + 1, status="draft",
        geometry_metadata=payload.geometry.model_dump(),
    )
    db.add(layout)
    db.flush()
    db.add_all([
        VehicleSeat(
            seat_layout_version_id=layout.id, seat_code=item["seat_code"],
            row_label=item["row_label"],
            position_metadata={
                "column_index": item["column_index"],
                "x": item["x"] if item["x"] is not None else min(100, item["column_index"] * 5),
                "y": item["y"] if item["y"] is not None else min(100, (ord(item["row_label"][0]) - 65) * 5) if item["row_label"] else 0,
            },
            seat_type=item["seat_type"], is_sellable=item["is_sellable"],
        )
        for item in seat_rows
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


@router.post("/vehicles/{vehicle_id}/compliance-documents", status_code=status.HTTP_201_CREATED)
def submit_vehicle_compliance_evidence(
    vehicle_id: UUID, payload: ComplianceEvidenceCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    _authorize(db, context, "operator.fleet.manage", vehicle.organization_id)
    reference = payload.evidence_reference.strip()
    if reference.startswith(("http://", "https://")) or ".." in reference or not reference.startswith("fleet-compliance/"):
        raise HTTPException(status_code=422, detail="Evidence reference must be an opaque key from the approved document store.")
    if payload.issued_at and payload.expires_at and payload.expires_at <= payload.issued_at:
        raise HTTPException(status_code=422, detail="Evidence expiry must be later than issue date.")
    document = VehicleComplianceDocument(
        vehicle_id=vehicle.id, document_type=payload.document_type,
        evidence_reference=reference, issued_at=payload.issued_at, expires_at=payload.expires_at,
        status="pending", submitted_by=context.user.id,
    )
    db.add(document)
    db.flush()
    _audit(db, context=context, event="fleet.compliance.submitted", resource_type="vehicle_compliance_document",
           resource_id=document.id, action="submit", organization_id=vehicle.organization_id,
           metadata={"document_type": document.document_type})
    db.commit()
    return {"id": str(document.id), "document_type": document.document_type, "status": document.status}


@router.post("/compliance-documents/{document_id}/review")
def review_vehicle_compliance_evidence(
    document_id: UUID, payload: ComplianceEvidenceReview, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.fleet.review")
    document = db.scalar(select(VehicleComplianceDocument).where(
        VehicleComplianceDocument.id == document_id
    ).with_for_update())
    if document is None:
        raise HTTPException(status_code=404, detail="Compliance evidence not found.")
    if document.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending compliance evidence can be reviewed.")
    expires_at = document.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if payload.decision == "approved" and expires_at and expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=409, detail="Expired evidence cannot be approved.")
    vehicle = db.get(Vehicle, document.vehicle_id)
    document.status = payload.decision
    document.reviewed_by = context.user.id
    document.review_reason = payload.reason.strip()
    document.reviewed_at = datetime.now(UTC)
    _audit(db, context=context, event="fleet.compliance.reviewed", resource_type="vehicle_compliance_document",
           resource_id=document.id, action="review", organization_id=vehicle.organization_id if vehicle else None,
           reason=document.review_reason, metadata={"decision": document.status})
    db.commit()
    return {"id": str(document.id), "status": document.status, "reviewed_at": document.reviewed_at.isoformat()}


@router.get("/vehicles/{vehicle_id}/history")
def get_vehicle_review_history(
    vehicle_id: UUID, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    if not has_permission(db, user_id=context.user.id, permission_code="platform.fleet.review", organization_id=None):
        _authorize(db, context, "operator.fleet.manage", vehicle.organization_id)
    documents = db.scalars(select(VehicleComplianceDocument).where(
        VehicleComplianceDocument.vehicle_id == vehicle.id
    ).order_by(VehicleComplianceDocument.created_at.desc())).all()
    layout_ids = db.scalars(select(SeatLayoutVersion.id).where(
        SeatLayoutVersion.vehicle_id == vehicle.id
    )).all()
    resource_ids = [str(vehicle.id), *[str(item.id) for item in documents], *[str(item) for item in layout_ids]]
    events = db.scalars(select(AuditEvent).where(
        AuditEvent.organization_id == vehicle.organization_id,
        AuditEvent.resource_id.in_(resource_ids),
    ).order_by(AuditEvent.occurred_at.desc()).limit(100)).all()
    return {
        "documents": [{
            "id": str(item.id), "document_type": item.document_type, "status": item.status,
            "evidence_reference": item.evidence_reference, "issued_at": item.issued_at.isoformat() if item.issued_at else None,
            "expires_at": item.expires_at.isoformat() if item.expires_at else None,
            "review_reason": item.review_reason, "created_at": item.created_at.isoformat() if item.created_at else None,
        } for item in documents],
        "events": [{
            "event_type": item.event_type, "occurred_at": item.occurred_at.isoformat(),
            "action": item.action, "outcome": item.outcome, "reason_code": item.reason_code,
            "metadata": item.metadata_redacted or {},
        } for item in events],
    }


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
    if operator is None or operator.organization_type != "operator" or operator.status != "approved":
        raise HTTPException(status_code=409, detail="An approved operator organization is required.")
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


@router.patch("/trips/{trip_id}")
def update_trip_draft(
    trip_id: UUID, payload: TripDraftUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    trip = db.scalar(select(Trip).where(Trip.id == trip_id).with_for_update())
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    _authorize(db, context, "operator.trip.manage", trip.organization_id)
    if trip.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft trips can be edited.")
    if payload.departure_at.tzinfo is None or (payload.arrival_estimate_at and payload.arrival_estimate_at.tzinfo is None):
        raise HTTPException(status_code=422, detail="Trip timestamps must include a timezone.")
    if payload.arrival_estimate_at is not None and payload.arrival_estimate_at <= payload.departure_at:
        raise HTTPException(status_code=422, detail="Arrival estimate must be later than departure.")
    route = db.get(Route, payload.route_id)
    terminal = db.get(Terminal, payload.boarding_terminal_id)
    vehicle = db.get(Vehicle, payload.vehicle_id)
    layout = db.get(SeatLayoutVersion, payload.seat_layout_version_id)
    if route is None or route.status != "published":
        raise HTTPException(status_code=409, detail="Route is not published.")
    if terminal is None or terminal.status != "published" or terminal.location_id != route.origin_location_id:
        raise HTTPException(status_code=409, detail="Boarding terminal must be published at the route origin.")
    if vehicle is None or vehicle.organization_id != trip.organization_id or vehicle.status != "active" or vehicle.review_status != "approved":
        raise HTTPException(status_code=409, detail="Vehicle must be approved and belong to this operator.")
    if layout is None or layout.vehicle_id != vehicle.id or layout.status != "approved":
        raise HTTPException(status_code=409, detail="Seat layout must be approved for the selected vehicle.")
    seats = db.scalars(select(VehicleSeat).where(
        VehicleSeat.seat_layout_version_id == layout.id,
        VehicleSeat.is_sellable.is_(True),
    ).order_by(VehicleSeat.seat_code)).all()
    if not seats:
        raise HTTPException(status_code=409, detail="Approved seat layout has no sellable seats.")
    trip.route_id = route.id
    trip.boarding_terminal_id = terminal.id
    trip.vehicle_id = vehicle.id
    trip.seat_layout_version_id = layout.id
    trip.departure_at = payload.departure_at
    trip.arrival_estimate_at = payload.arrival_estimate_at
    for existing in db.scalars(select(TripSeat).where(TripSeat.trip_id == trip.id)).all():
        db.delete(existing)
    db.flush()
    db.add_all([
        TripSeat(trip_id=trip.id, vehicle_seat_id=seat.id,
                 seat_code_snapshot=seat.seat_code, sellable_status="sellable")
        for seat in seats
    ])
    _audit(db, context=context, event="trip.draft.updated", resource_type="trip",
           resource_id=trip.id, action="update", organization_id=trip.organization_id,
           metadata={"seat_count": len(seats)})
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
    operator = db.get(Organization, organization_id)
    route = db.get(Route, payload.route_id)
    if operator is None or operator.organization_type != "operator" or operator.status != "approved":
        raise HTTPException(status_code=409, detail="An approved operator organization is required.")
    if route is None or route.status != "published":
        raise HTTPException(status_code=409, detail="Fare proposals require a published route.")
    if payload.trip_id is not None:
        trip = db.get(Trip, payload.trip_id)
        if trip is None or trip.organization_id != organization_id or trip.route_id != payload.route_id or trip.status not in {"approved", "published"}:
            raise HTTPException(status_code=409, detail="Trip-specific fare must reference an approved trip for this operator and route.")
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


@router.get("/support/passenger-cases")
def list_passenger_support_cases(
    case_status: Literal["open", "in_progress", "resolved", "closed"] | None = None,
    limit: int = 100,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.support.manage")
    statement = select(PassengerSupportCase).order_by(PassengerSupportCase.created_at.asc())
    if case_status:
        statement = statement.where(PassengerSupportCase.status == case_status)
    cases = db.scalars(statement.limit(max(1, min(limit, 200)))).all()
    return [{
        "id": str(case.id),
        "case_reference": case.case_reference,
        "passenger_id": str(case.passenger_id),
        "category": case.category,
        "subject": case.subject,
        "message": case.message,
        "status": case.status,
        "assigned_to": str(case.assigned_to) if case.assigned_to else None,
        "resolution_code": case.resolution_code,
        "resolution_note": case.resolution_note,
        "created_at": case.created_at.isoformat(),
        "resolved_at": case.resolved_at.isoformat() if case.resolved_at else None,
    } for case in cases]


@router.post("/support/passenger-cases/{case_id}/claim")
def claim_passenger_support_case(
    case_id: UUID,
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.support.manage")
    case = db.scalar(select(PassengerSupportCase).where(
        PassengerSupportCase.id == case_id
    ).with_for_update())
    if case is None or case.status not in {"open", "in_progress"}:
        raise HTTPException(status_code=409, detail="Passenger support case is not available.")
    if case.assigned_to not in {None, context.user.id}:
        raise HTTPException(status_code=409, detail="Passenger support case is assigned to another staff member.")
    case.assigned_to = context.user.id
    case.status = "in_progress"
    _audit(
        db, context=context, event="passenger.support.case.claimed",
        resource_type="passenger_support_case", resource_id=case.id,
        action="claim", metadata={"category": case.category},
    )
    db.commit()
    return {"case_reference": case.case_reference, "status": case.status}


@router.post("/support/passenger-cases/{case_id}/resolve")
def resolve_passenger_support_case(
    case_id: UUID,
    payload: SupportResolution,
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.support.manage")
    case = db.scalar(select(PassengerSupportCase).where(
        PassengerSupportCase.id == case_id
    ).with_for_update())
    if case is None or case.status not in {"open", "in_progress"}:
        raise HTTPException(status_code=409, detail="Passenger support case is not open.")
    if case.assigned_to not in {None, context.user.id}:
        raise HTTPException(status_code=403, detail="Passenger support case is assigned to another staff member.")
    case.assigned_to = context.user.id
    case.status = "resolved"
    case.resolution_code = payload.resolution_code.strip()
    case.resolution_note = payload.resolution_note.strip()
    case.resolved_at = datetime.now(UTC)
    _audit(
        db, context=context, event="passenger.support.case.resolved",
        resource_type="passenger_support_case", resource_id=case.id,
        action="resolve", metadata={"resolution_code": case.resolution_code},
    )
    db.commit()
    return {
        "case_reference": case.case_reference,
        "status": case.status,
        "resolution_code": case.resolution_code,
        "resolved_at": case.resolved_at.isoformat(),
    }


@router.get("/reports/passenger")
def list_passenger_reports(
    report_type: Literal["report", "complaint"] | None = None,
    report_status: Literal["submitted", "under_review", "action_required", "resolved", "dismissed"] | None = None,
    limit: int = 100,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.support.manage")
    statement = select(PassengerReport).order_by(PassengerReport.created_at.asc())
    if report_type:
        statement = statement.where(PassengerReport.report_type == report_type)
    if report_status:
        statement = statement.where(PassengerReport.status == report_status)
    records = db.scalars(statement.limit(max(1, min(limit, 200)))).all()
    return [{
        "id": str(item.id),
        "report_reference": item.report_reference,
        "passenger_id": str(item.passenger_id),
        "report_type": item.report_type,
        "category": item.category,
        "severity": item.severity,
        "subject": item.subject,
        "description": item.description,
        "status": item.status,
        "assigned_to": str(item.assigned_to) if item.assigned_to else None,
        "resolution_note": item.resolution_note,
        "created_at": item.created_at.isoformat(),
        "resolved_at": item.resolved_at.isoformat() if item.resolved_at else None,
        "attachments": [{
            "id": str(file.id), "file_name": file.original_filename,
            "content_type": file.content_type, "size_bytes": file.size_bytes,
            "sha256": file.sha256,
        } for file in db.scalars(select(PassengerReportAttachment).where(
            PassengerReportAttachment.report_id == item.id
        )).all()],
    } for item in records]


@router.get("/reports/passenger/{report_id}/attachments/{attachment_id}")
def download_passenger_report_evidence(
    report_id: UUID,
    attachment_id: UUID,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> FileResponse:
    _authorize(db, context, "platform.support.manage")
    report = db.get(PassengerReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Passenger report not found.")
    attachment = db.scalar(select(PassengerReportAttachment).where(
        PassengerReportAttachment.id == attachment_id,
        PassengerReportAttachment.report_id == report.id,
    ))
    if attachment is None:
        raise HTTPException(status_code=404, detail="Evidence attachment not found.")
    root = Path(os.environ.get(
        "MAALENEX_PRIVATE_UPLOAD_DIR", "/var/lib/maalenex/private-uploads"
    )).expanduser().resolve()
    target = (root / attachment.storage_key).resolve()
    if target.parent != root or not target.is_file():
        raise HTTPException(status_code=404, detail="Evidence attachment is unavailable.")
    _audit(
        db, context=context, event="passenger.report.attachment.downloaded",
        resource_type="passenger_report", resource_id=report.id,
        action="download_evidence",
        metadata={"attachment_id": str(attachment.id), "content_type": attachment.content_type},
    )
    db.commit()
    return FileResponse(
        target, media_type=attachment.content_type, filename=attachment.original_filename,
        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"},
    )


@router.post("/reports/passenger/{report_id}/claim")
def claim_passenger_report(
    report_id: UUID,
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.support.manage")
    report = db.scalar(select(PassengerReport).where(
        PassengerReport.id == report_id
    ).with_for_update())
    if report is None or report.status in {"resolved", "dismissed"}:
        raise HTTPException(status_code=409, detail="Passenger report is not available for review.")
    if report.assigned_to not in {None, context.user.id}:
        raise HTTPException(status_code=409, detail="Passenger report is assigned to another staff member.")
    report.assigned_to = context.user.id
    report.status = "under_review"
    _audit(
        db, context=context, event="passenger.report.claimed",
        resource_type="passenger_report", resource_id=report.id,
        action="claim", metadata={"report_type": report.report_type, "category": report.category},
    )
    db.commit()
    return {"report_reference": report.report_reference, "status": report.status}


@router.post("/reports/passenger/{report_id}/review")
def review_passenger_report(
    report_id: UUID,
    payload: ReportReview,
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.support.manage")
    report = db.scalar(select(PassengerReport).where(
        PassengerReport.id == report_id
    ).with_for_update())
    if report is None or report.status in {"resolved", "dismissed"}:
        raise HTTPException(status_code=409, detail="Passenger report is already closed or unavailable.")
    if report.assigned_to not in {None, context.user.id}:
        raise HTTPException(status_code=403, detail="Passenger report is assigned to another staff member.")
    report.assigned_to = context.user.id
    report.status = payload.status
    report.resolution_note = payload.resolution_note.strip()
    report.resolved_at = datetime.now(UTC) if payload.status in {"resolved", "dismissed"} else None
    _audit(
        db, context=context, event="passenger.report.status_changed",
        resource_type="passenger_report", resource_id=report.id,
        action="review", metadata={"status": report.status},
    )
    db.commit()
    return {
        "report_reference": report.report_reference,
        "status": report.status,
        "resolution_note": report.resolution_note,
        "resolved_at": report.resolved_at.isoformat() if report.resolved_at else None,
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



@router.get("/catalog/locations")
def list_catalog_locations(
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.catalog.manage")
    items = db.scalars(select(Location).order_by(Location.name, Location.id).limit(200)).all()
    return [
        {"id": str(item.id), "name": item.name, "location_type": item.location_type, "status": item.status}
        for item in items
    ]


@router.get("/catalog/terminals")
def list_catalog_terminals(
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.catalog.manage")
    items = db.scalars(select(Terminal).order_by(Terminal.name, Terminal.id).limit(200)).all()
    locations = {
        item.id: item.name
        for item in db.scalars(select(Location).where(Location.id.in_({item.location_id for item in items}))).all()
    } if items else {}
    return [
        {"id": str(item.id), "location_id": str(item.location_id),
         "location_name": locations.get(item.location_id, "Unknown location"),
         "name": item.name, "status": item.status}
        for item in items
    ]


@router.get("/catalog/routes")
def list_catalog_routes(
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.catalog.manage")
    items = db.scalars(select(Route).order_by(Route.code, Route.id).limit(200)).all()
    location_ids = {item.origin_location_id for item in items} | {item.destination_location_id for item in items}
    locations = {
        item.id: item.name
        for item in db.scalars(select(Location).where(Location.id.in_(location_ids))).all()
    } if location_ids else {}
    stop_rows = db.execute(
        select(RouteStop, Location.name).join(Location, Location.id == RouteStop.location_id)
        .where(RouteStop.route_id.in_([item.id for item in items]))
        .order_by(RouteStop.route_id, RouteStop.sequence_number)
    ).all() if items else []
    route_stops_by_route: dict[UUID, list[dict]] = {}
    for stop, location_name in stop_rows:
        route_stops_by_route.setdefault(stop.route_id, []).append({
            "id": str(stop.id), "location_id": str(stop.location_id),
            "location_name": location_name, "sequence_number": stop.sequence_number,
            "boarding_allowed": stop.boarding_allowed, "alighting_allowed": stop.alighting_allowed,
            "status": stop.status,
        })
    return [
        {"id": str(item.id), "code": item.code,
         "origin_location_id": str(item.origin_location_id),
         "origin_name": locations.get(item.origin_location_id, "Unknown location"),
         "destination_location_id": str(item.destination_location_id),
         "destination_name": locations.get(item.destination_location_id, "Unknown location"),
         "status": item.status,
         "stops": [
             {"id": str(stop.id), "location_id": str(stop.location_id),
              "location_name": stop.location_name, "sequence_number": stop.sequence_number,
              "boarding_allowed": stop.boarding_allowed, "alighting_allowed": stop.alighting_allowed,
              "status": stop.status}
             for stop in route_stops_by_route.get(item.id, [])
         ]}
        for item in items
    ]



@router.patch("/catalog/locations/{location_id}")
def update_catalog_location(
    location_id: UUID, payload: LocationUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    item = db.scalar(select(Location).where(Location.id == location_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Location not found.")
    if item.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft locations can be edited.")
    values = payload.model_dump(exclude_unset=True)
    if not values or any(value is None for value in values.values()):
        raise HTTPException(status_code=422, detail="Provide non-null fields to update.")
    for key, value in values.items():
        setattr(item, key, value.strip() if isinstance(value, str) else value)
    _audit(db, context=context, event="catalog.location.updated", resource_type="location",
           resource_id=item.id, action="update")
    db.commit()
    return {"id": str(item.id), "name": item.name, "location_type": item.location_type, "status": item.status}


@router.patch("/catalog/terminals/{terminal_id}")
def update_catalog_terminal(
    terminal_id: UUID, payload: TerminalUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    item = db.scalar(select(Terminal).where(Terminal.id == terminal_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Terminal not found.")
    if item.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft terminals can be edited.")
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=422, detail="At least one field is required.")
    if "location_id" in values:
        location = db.get(Location, values["location_id"])
        if location is None or location.status != "published":
            raise HTTPException(status_code=409, detail="Terminal location must be published.")
    for key, value in values.items():
        setattr(item, key, value.strip() if isinstance(value, str) else value)
    _audit(db, context=context, event="catalog.terminal.updated", resource_type="terminal",
           resource_id=item.id, action="update")
    db.commit()
    return {"id": str(item.id), "name": item.name, "location_id": str(item.location_id), "status": item.status}


@router.patch("/catalog/routes/{route_id}")
def update_catalog_route(
    route_id: UUID, payload: RouteUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    item = db.scalar(select(Route).where(Route.id == route_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Route not found.")
    if item.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft routes can be edited.")
    values = payload.model_dump(exclude_unset=True)
    if not values or any(value is None for value in values.values()):
        raise HTTPException(status_code=422, detail="Provide non-null fields to update.")
    origin = values.get("origin_location_id", item.origin_location_id)
    destination = values.get("destination_location_id", item.destination_location_id)
    if origin == destination:
        raise HTTPException(status_code=422, detail="Route origin and destination must differ.")
    published_locations = set(db.scalars(select(Location.id).where(
        Location.id.in_([origin, destination]), Location.status == "published"
    )).all())
    if published_locations != {origin, destination}:
        raise HTTPException(status_code=409, detail="Both route locations must be published.")
    if "code" in values:
        values["code"] = values["code"].strip().upper()
    for key, value in values.items():
        setattr(item, key, value)
    stops = list(db.scalars(select(RouteStop).where(
        RouteStop.route_id == item.id
    ).order_by(RouteStop.sequence_number).with_for_update()))
    if stops:
        stops[0].location_id = origin
        stops[-1].location_id = destination
    _audit(db, context=context, event="catalog.route.updated", resource_type="route",
           resource_id=item.id, action="update")
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Route code already exists.")
    return {"id": str(item.id), "code": item.code, "status": item.status}


@router.put("/catalog/routes/{route_id}/stops")
def replace_catalog_route_stops(
    route_id: UUID, payload: RouteStopsUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    route = db.scalar(select(Route).where(Route.id == route_id).with_for_update())
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found.")
    if route.status != "draft":
        raise HTTPException(status_code=409, detail="Stops can only be changed on draft routes.")
    location_ids = [stop.location_id for stop in payload.stops]
    if len(set(location_ids)) != len(location_ids):
        raise HTTPException(status_code=422, detail="A route cannot visit the same location more than once.")
    if location_ids[0] != route.origin_location_id or location_ids[-1] != route.destination_location_id:
        raise HTTPException(status_code=422, detail="The first and last stops must match the route origin and destination.")
    published_ids = set(db.scalars(select(Location.id).where(
        Location.id.in_(location_ids), Location.status == "published"
    )).all())
    if published_ids != set(location_ids):
        raise HTTPException(status_code=409, detail="Every route stop must reference a published location.")
    old_stops = list(db.scalars(select(RouteStop).where(
        RouteStop.route_id == route.id
    ).with_for_update()))
    for stop in old_stops:
        db.delete(stop)
    db.flush()
    stops = [
        RouteStop(
            route_id=route.id, location_id=stop.location_id, sequence_number=index,
            boarding_allowed=stop.boarding_allowed, alighting_allowed=stop.alighting_allowed,
            status="draft",
        )
        for index, stop in enumerate(payload.stops, start=1)
    ]
    db.add_all(stops)
    _audit(db, context=context, event="catalog.route.stops_replaced", resource_type="route",
           resource_id=route.id, action="update", metadata={"stop_count": len(stops)})
    db.commit()
    return {"route_id": str(route.id), "stops": len(stops)}


@router.post("/catalog/locations/{location_id}/archive")
def archive_catalog_location(
    location_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    item = db.scalar(select(Location).where(Location.id == location_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Location not found.")
    if item.status == "archived":
        raise HTTPException(status_code=409, detail="Location is already archived.")
    references = (
        db.scalar(select(Terminal.id).where(Terminal.location_id == item.id).limit(1))
        or db.scalar(select(Route.id).where(
            (Route.origin_location_id == item.id) | (Route.destination_location_id == item.id)
        ).limit(1))
        or db.scalar(select(RouteStop.id).where(RouteStop.location_id == item.id).limit(1))
    )
    if references:
        raise HTTPException(status_code=409, detail="Location is referenced by a terminal or route and cannot be archived.")
    item.status = "archived"
    _audit(db, context=context, event="catalog.location.archived", resource_type="location",
           resource_id=item.id, action="archive")
    db.commit()
    return {"id": str(item.id), "status": item.status}


@router.post("/catalog/terminals/{terminal_id}/archive")
def archive_catalog_terminal(
    terminal_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    item = db.scalar(select(Terminal).where(Terminal.id == terminal_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Terminal not found.")
    if item.status == "archived":
        raise HTTPException(status_code=409, detail="Terminal is already archived.")
    if db.scalar(select(Trip.id).where(Trip.boarding_terminal_id == item.id).limit(1)):
        raise HTTPException(status_code=409, detail="Terminal is referenced by a trip and cannot be archived.")
    item.status = "archived"
    _audit(db, context=context, event="catalog.terminal.archived", resource_type="terminal",
           resource_id=item.id, action="archive")
    db.commit()
    return {"id": str(item.id), "status": item.status}


@router.post("/catalog/routes/{route_id}/archive")
def archive_catalog_route(
    route_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.catalog.manage")
    item = db.scalar(select(Route).where(Route.id == route_id).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Route not found.")
    if item.status == "archived":
        raise HTTPException(status_code=409, detail="Route is already archived.")
    references = (
        db.scalar(select(Schedule.id).where(Schedule.route_id == item.id).limit(1))
        or db.scalar(select(Trip.id).where(Trip.route_id == item.id).limit(1))
        or db.scalar(select(Fare.id).where(Fare.route_id == item.id).limit(1))
    )
    if references:
        raise HTTPException(status_code=409, detail="Route is referenced by a schedule, trip or fare and cannot be archived.")
    item.status = "archived"
    for stop in db.scalars(select(RouteStop).where(RouteStop.route_id == item.id).with_for_update()):
        stop.status = "archived"
    _audit(db, context=context, event="catalog.route.archived", resource_type="route",
           resource_id=item.id, action="archive")
    db.commit()
    return {"id": str(item.id), "status": item.status}



def _fleet_payload(db: Session, vehicles: list[Vehicle]) -> list[dict]:
    if not vehicles:
        return []
    organization_ids = {item.organization_id for item in vehicles}
    organizations = {
        item.id: item.display_name
        for item in db.scalars(select(Organization).where(Organization.id.in_(organization_ids))).all()
    }
    layouts = list(db.scalars(select(SeatLayoutVersion).where(
        SeatLayoutVersion.vehicle_id.in_([item.id for item in vehicles])
    ).order_by(SeatLayoutVersion.vehicle_id, SeatLayoutVersion.version_number.desc())).all())
    layout_ids = [item.id for item in layouts]
    counts = dict(db.execute(
        select(VehicleSeat.seat_layout_version_id, func.count(VehicleSeat.id))
        .where(VehicleSeat.seat_layout_version_id.in_(layout_ids))
        .group_by(VehicleSeat.seat_layout_version_id)
    ).all()) if layout_ids else {}
    by_vehicle: dict[UUID, list[dict]] = {}
    for layout in layouts:
        by_vehicle.setdefault(layout.vehicle_id, []).append({
            "id": str(layout.id), "version_number": layout.version_number,
            "status": layout.status, "seat_count": counts.get(layout.id, 0),
        })
    return [{
        "id": str(vehicle.id), "organization_id": str(vehicle.organization_id),
        "organization_name": organizations.get(vehicle.organization_id, "Unknown operator"),
        "vehicle_reference": vehicle.vehicle_reference, "status": vehicle.status,
        "review_status": vehicle.review_status, "created_at": vehicle.created_at.isoformat() if vehicle.created_at else None,
        "seat_layouts": by_vehicle.get(vehicle.id, []),
    } for vehicle in vehicles]


@router.get("/admin/fleet/vehicles")
def list_platform_fleet(
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.fleet.review")
    vehicles = db.scalars(select(Vehicle).order_by(Vehicle.created_at.desc(), Vehicle.id).limit(300)).all()
    return _fleet_payload(db, vehicles)


@router.get("/operators/{organization_id}/fleet")
def list_operator_fleet(
    organization_id: UUID, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "operator.fleet.manage", organization_id)
    operator = db.get(Organization, organization_id)
    if operator is None or operator.organization_type != "operator":
        raise HTTPException(status_code=404, detail="Operator organization not found.")
    vehicles = db.scalars(select(Vehicle).where(
        Vehicle.organization_id == organization_id
    ).order_by(Vehicle.created_at.desc(), Vehicle.id).limit(300)).all()
    return _fleet_payload(db, vehicles)


@router.get("/vehicles/{vehicle_id}/seat-layouts")
def list_vehicle_seat_layouts(
    vehicle_id: UUID, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    if not has_permission(db, user_id=context.user.id, permission_code="platform.fleet.review", organization_id=None):
        _authorize(db, context, "operator.fleet.manage", vehicle.organization_id)
    layouts = db.scalars(select(SeatLayoutVersion).where(
        SeatLayoutVersion.vehicle_id == vehicle.id
    ).order_by(SeatLayoutVersion.version_number.desc())).all()
    results = []
    for layout in layouts:
        seats = db.scalars(select(VehicleSeat).where(
            VehicleSeat.seat_layout_version_id == layout.id
        ).order_by(VehicleSeat.row_label, VehicleSeat.seat_code)).all()
        results.append({
            "id": str(layout.id), "version_number": layout.version_number, "status": layout.status,
            "geometry": layout.geometry_metadata or {"width": 100, "height": 100, "markers": []},
            "effective_from": layout.effective_from.isoformat() if layout.effective_from else None,
            "effective_to": layout.effective_to.isoformat() if layout.effective_to else None,
            "seats": [{
                "id": str(seat.id), "seat_code": seat.seat_code, "row_label": seat.row_label,
                "column_index": (seat.position_metadata or {}).get("column_index", 0),
                "x": (seat.position_metadata or {}).get("x", 0),
                "y": (seat.position_metadata or {}).get("y", 0),
                "seat_type": seat.seat_type, "is_sellable": seat.is_sellable,
            } for seat in seats],
        })
    return results


@router.patch("/vehicles/{vehicle_id}")
def update_fleet_vehicle(
    vehicle_id: UUID, payload: VehicleUpdate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    vehicle = db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id).with_for_update())
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    _authorize(db, context, "operator.fleet.manage", vehicle.organization_id)
    if vehicle.status != "draft" or vehicle.review_status != "pending":
        raise HTTPException(status_code=409, detail="Only pending vehicle drafts can be edited.")
    reference = payload.vehicle_reference.strip()
    duplicate = db.scalar(select(Vehicle.id).where(
        Vehicle.organization_id == vehicle.organization_id,
        Vehicle.vehicle_reference == reference, Vehicle.id != vehicle.id,
    ).limit(1))
    if duplicate:
        raise HTTPException(status_code=409, detail="Vehicle reference already exists for this operator.")
    vehicle.vehicle_reference = reference
    _audit(db, context=context, event="fleet.vehicle.updated", resource_type="vehicle",
           resource_id=vehicle.id, action="update", organization_id=vehicle.organization_id)
    db.commit()
    return {"id": str(vehicle.id), "vehicle_reference": vehicle.vehicle_reference,
            "status": vehicle.status, "review_status": vehicle.review_status}


@router.put("/seat-layouts/{layout_id}")
def update_draft_seat_layout(
    layout_id: UUID, payload: SeatLayoutCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    layout = db.scalar(select(SeatLayoutVersion).where(
        SeatLayoutVersion.id == layout_id
    ).with_for_update())
    if layout is None:
        raise HTTPException(status_code=404, detail="Seat layout not found.")
    vehicle = db.get(Vehicle, layout.vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found.")
    _authorize(db, context, "operator.fleet.manage", vehicle.organization_id)
    if layout.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft seat layouts can be edited.")
    if vehicle.status != "active" or vehicle.review_status != "approved":
        raise HTTPException(status_code=409, detail="Vehicle must remain approved to edit its seat layout.")
    if bool(payload.seat_codes) == bool(payload.seats):
        raise HTTPException(status_code=422, detail="Provide either seat_codes or structured seats.")
    layout.geometry_metadata = payload.geometry.model_dump()
    if payload.seats:
        seat_rows = [{
            "seat_code": item.seat_code.strip().upper(),
            "row_label": item.row_label.strip().upper() if item.row_label else None,
            "column_index": item.column_index, "x": item.x, "y": item.y,
            "seat_type": item.seat_type, "is_sellable": item.is_sellable,
        } for item in payload.seats]
    else:
        seat_rows = [{
            "seat_code": code.strip().upper(), "row_label": None,
            "column_index": index, "x": None, "y": None, "seat_type": "standard", "is_sellable": True,
        } for index, code in enumerate(payload.seat_codes)]
    codes = [item["seat_code"] for item in seat_rows]
    positions = [(item["row_label"], item["column_index"]) for item in seat_rows if item["row_label"] is not None]
    if any(not code or len(code) > 16 for code in codes) or len(set(codes)) != len(codes):
        raise HTTPException(status_code=422, detail="Seat codes must be unique and 1–16 characters.")
    if len(set(positions)) != len(positions):
        raise HTTPException(status_code=422, detail="Seat positions must be unique within each row.")
    for seat in db.scalars(select(VehicleSeat).where(
        VehicleSeat.seat_layout_version_id == layout.id
    ).with_for_update()):
        db.delete(seat)
    db.flush()
    db.add_all([
        VehicleSeat(
            seat_layout_version_id=layout.id, seat_code=item["seat_code"],
            row_label=item["row_label"],
            position_metadata={
                "column_index": item["column_index"],
                "x": item["x"] if item["x"] is not None else min(100, item["column_index"] * 5),
                "y": item["y"] if item["y"] is not None else min(100, (ord(item["row_label"][0]) - 65) * 5) if item["row_label"] else 0,
            },
            seat_type=item["seat_type"], is_sellable=item["is_sellable"],
        ) for item in seat_rows
    ])
    _audit(db, context=context, event="fleet.seat_layout.updated",
           resource_type="seat_layout_version", resource_id=layout.id,
           action="update", organization_id=vehicle.organization_id,
           metadata={"seat_count": len(seat_rows)})
    db.commit()
    return {"id": str(layout.id), "version_number": layout.version_number,
            "seat_count": len(seat_rows), "status": layout.status}


def _trip_payload(db: Session, trips: list[Trip]) -> list[dict]:
    if not trips:
        return []
    route_ids = {item.route_id for item in trips}
    terminal_ids = {item.boarding_terminal_id for item in trips}
    vehicle_ids = {item.vehicle_id for item in trips}
    organization_ids = {item.organization_id for item in trips}
    trip_ids = [item.id for item in trips]
    routes = {item.id: item for item in db.scalars(select(Route).where(Route.id.in_(route_ids))).all()}
    terminals = {item.id: item for item in db.scalars(select(Terminal).where(Terminal.id.in_(terminal_ids))).all()}
    vehicles = {item.id: item for item in db.scalars(select(Vehicle).where(Vehicle.id.in_(vehicle_ids))).all()}
    organizations = {item.id: item for item in db.scalars(select(Organization).where(Organization.id.in_(organization_ids))).all()}
    seat_counts = dict(db.execute(
        select(TripSeat.trip_id, func.count(TripSeat.id))
        .where(TripSeat.trip_id.in_(trip_ids)).group_by(TripSeat.trip_id)
    ).all())
    return [{
        "id": str(trip.id), "organization_id": str(trip.organization_id),
        "organization_name": organizations[trip.organization_id].display_name if trip.organization_id in organizations else "Unknown operator",
        "route_id": str(trip.route_id), "route_code": routes[trip.route_id].code if trip.route_id in routes else "Unknown route",
        "boarding_terminal_id": str(trip.boarding_terminal_id),
        "boarding_terminal_name": terminals[trip.boarding_terminal_id].name if trip.boarding_terminal_id in terminals else "Unknown terminal",
        "vehicle_id": str(trip.vehicle_id),
        "vehicle_reference": vehicles[trip.vehicle_id].vehicle_reference if trip.vehicle_id in vehicles else "Unknown vehicle",
        "seat_layout_version_id": str(trip.seat_layout_version_id),
        "departure_at": trip.departure_at.isoformat(),
        "arrival_estimate_at": trip.arrival_estimate_at.isoformat() if trip.arrival_estimate_at else None,
        "status": trip.status, "seat_count": seat_counts.get(trip.id, 0),
        "published_at": trip.published_at.isoformat() if trip.published_at else None,
    } for trip in trips]


@router.get("/operators/{organization_id}/dispatch/options")
def get_operator_dispatch_options(
    organization_id: UUID, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _authorize(db, context, "operator.trip.manage", organization_id)
    operator = db.get(Organization, organization_id)
    if operator is None or operator.organization_type != "operator" or operator.status != "approved":
        raise HTTPException(status_code=409, detail="An approved operator organization is required.")
    routes = db.scalars(select(Route).where(Route.status == "published").order_by(Route.code).limit(300)).all()
    published_locations = select(Location.id).where(Location.status == "published")
    terminals = db.scalars(select(Terminal).where(
        Terminal.status == "published", Terminal.location_id.in_(published_locations)
    ).order_by(Terminal.name).limit(300)).all()
    vehicles = db.scalars(select(Vehicle).where(
        Vehicle.organization_id == organization_id, Vehicle.status == "active",
        Vehicle.review_status == "approved",
    ).order_by(Vehicle.vehicle_reference).limit(200)).all()
    vehicle_ids = [vehicle.id for vehicle in vehicles]
    layouts = db.scalars(select(SeatLayoutVersion).where(
        SeatLayoutVersion.vehicle_id.in_(vehicle_ids), SeatLayoutVersion.status == "approved"
    ).order_by(SeatLayoutVersion.vehicle_id, SeatLayoutVersion.version_number.desc())).all() if vehicle_ids else []
    layout_counts = dict(db.execute(
        select(VehicleSeat.seat_layout_version_id, func.count(VehicleSeat.id))
        .where(VehicleSeat.seat_layout_version_id.in_([item.id for item in layouts]),
               VehicleSeat.is_sellable.is_(True))
        .group_by(VehicleSeat.seat_layout_version_id)
    ).all()) if layouts else {}
    layouts_by_vehicle: dict[UUID, list[dict]] = {}
    for layout in layouts:
        layouts_by_vehicle.setdefault(layout.vehicle_id, []).append({
            "id": str(layout.id), "version_number": layout.version_number,
            "seat_count": layout_counts.get(layout.id, 0),
        })
    return {
        "routes": [{
            "id": str(route.id), "code": route.code,
            "origin_location_id": str(route.origin_location_id),
            "destination_location_id": str(route.destination_location_id),
        } for route in routes],
        "terminals": [{
            "id": str(terminal.id), "location_id": str(terminal.location_id),
            "name": terminal.name,
        } for terminal in terminals],
        "vehicles": [{
            "id": str(vehicle.id), "vehicle_reference": vehicle.vehicle_reference,
            "seat_layouts": layouts_by_vehicle.get(vehicle.id, []),
        } for vehicle in vehicles],
    }


@router.get("/operators/{organization_id}/trips")
def list_operator_trips(
    organization_id: UUID, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "operator.trip.manage", organization_id)
    trips = db.scalars(select(Trip).where(
        Trip.organization_id == organization_id
    ).order_by(Trip.departure_at.desc(), Trip.id).limit(300)).all()
    return _trip_payload(db, trips)


@router.get("/admin/dispatch/trips")
def list_platform_dispatch_trips(
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.trip.approve")
    trips = db.scalars(select(Trip).order_by(Trip.departure_at.desc(), Trip.id).limit(500)).all()
    return _trip_payload(db, trips)


@router.post("/trips/{trip_id}/exceptions", status_code=status.HTTP_201_CREATED)
def report_trip_operational_exception(
    trip_id: UUID, payload: OperationalExceptionCreate, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    _authorize(db, context, "operator.trip.manage", trip.organization_id)
    if trip.status in {"completed", "cancelled"}:
        raise HTTPException(status_code=409, detail="Operational exceptions cannot be added to completed or cancelled trips.")
    exception = TripOperationalException(
        trip_id=trip.id, organization_id=trip.organization_id,
        category=payload.category, severity=payload.severity,
        description=payload.description.strip(), status="open", created_by=context.user.id,
    )
    db.add(exception)
    db.flush()
    _audit(db, context=context, event="trip.exception.reported", resource_type="trip_operational_exception",
           resource_id=exception.id, action="report", organization_id=trip.organization_id,
           metadata={"trip_id": str(trip.id), "category": exception.category, "severity": exception.severity})
    db.commit()
    return {"id": str(exception.id), "trip_id": str(trip.id), "status": exception.status}


@router.get("/trips/{trip_id}/exceptions")
def list_trip_operational_exceptions(
    trip_id: UUID, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    if not has_permission(db, user_id=context.user.id, permission_code="platform.trip.approve", organization_id=None):
        _authorize(db, context, "operator.trip.manage", trip.organization_id)
    items = db.scalars(select(TripOperationalException).where(
        TripOperationalException.trip_id == trip.id,
        TripOperationalException.organization_id == trip.organization_id,
    ).order_by(TripOperationalException.created_at.desc())).all()
    return [{
        "id": str(item.id), "category": item.category, "severity": item.severity,
        "description": item.description, "status": item.status,
        "resolution": item.resolution,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "resolved_at": item.resolved_at.isoformat() if item.resolved_at else None,
    } for item in items]


@router.post("/trip-exceptions/{exception_id}/resolve")
def resolve_trip_operational_exception(
    exception_id: UUID, payload: OperationalExceptionResolution, request: Request,
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> dict:
    _require_mutation(request, context)
    _authorize(db, context, "platform.trip.approve")
    item = db.scalar(select(TripOperationalException).where(
        TripOperationalException.id == exception_id
    ).with_for_update())
    if item is None:
        raise HTTPException(status_code=404, detail="Operational exception not found.")
    if item.status != "open":
        raise HTTPException(status_code=409, detail="Only open operational exceptions can be resolved.")
    item.status = "resolved"
    item.reviewed_by = context.user.id
    item.resolution = payload.resolution.strip()
    item.resolved_at = datetime.now(UTC)
    _audit(db, context=context, event="trip.exception.resolved", resource_type="trip_operational_exception",
           resource_id=item.id, action="resolve", organization_id=item.organization_id,
           reason=item.resolution, metadata={"trip_id": str(item.trip_id)})
    db.commit()
    return {"id": str(item.id), "status": item.status, "resolved_at": item.resolved_at.isoformat()}


def _fare_payload(db: Session, fares: list[Fare]) -> list[dict]:
    if not fares:
        return []
    route_ids = {item.route_id for item in fares}
    trip_ids = {item.trip_id for item in fares if item.trip_id is not None}
    organization_ids = {item.organization_id for item in fares}
    routes = {item.id: item for item in db.scalars(select(Route).where(Route.id.in_(route_ids))).all()}
    trips = {item.id: item for item in db.scalars(select(Trip).where(Trip.id.in_(trip_ids))).all()} if trip_ids else {}
    organizations = {item.id: item for item in db.scalars(select(Organization).where(Organization.id.in_(organization_ids))).all()}
    versions = db.scalars(select(FareVersion).where(
        FareVersion.fare_id.in_([item.id for item in fares])
    ).order_by(FareVersion.fare_id, FareVersion.version_number.desc())).all()
    version_ids = [item.id for item in versions]
    approvals = db.scalars(select(FareApproval).where(
        FareApproval.fare_version_id.in_(version_ids)
    ).order_by(FareApproval.decided_at.desc())).all() if version_ids else []
    by_version: dict[UUID, list[dict]] = {}
    for approval in approvals:
        by_version.setdefault(approval.fare_version_id, []).append({
            "id": str(approval.id), "decision": approval.decision,
            "reviewer_id": str(approval.reviewer_user_id), "reason": approval.reason,
            "decided_at": approval.decided_at.isoformat() if approval.decided_at else None,
        })
    by_fare: dict[UUID, list[dict]] = {}
    for version in versions:
        by_fare.setdefault(version.fare_id, []).append({
            "id": str(version.id), "version_number": version.version_number,
            "amount_minor_units": version.amount_minor_units, "currency_code": version.currency_code,
            "effective_from": version.effective_from.isoformat(),
            "effective_to": version.effective_to.isoformat() if version.effective_to else None,
            "status": version.status, "proposed_by": str(version.proposed_by),
            "approved_by": str(version.approved_by) if version.approved_by else None,
            "published_by": str(version.published_by) if version.published_by else None,
            "published_at": version.published_at.isoformat() if version.published_at else None,
            "approval_history": by_version.get(version.id, []),
        })
    return [{
        "id": str(fare.id), "organization_id": str(fare.organization_id),
        "organization_name": organizations[fare.organization_id].display_name if fare.organization_id in organizations else "Unknown operator",
        "route_id": str(fare.route_id), "route_code": routes[fare.route_id].code if fare.route_id in routes else "Unknown route",
        "trip_id": str(fare.trip_id) if fare.trip_id else None,
        "trip_departure_at": trips[fare.trip_id].departure_at.isoformat() if fare.trip_id in trips else None,
        "status": fare.status, "versions": by_fare.get(fare.id, []),
    } for fare in fares]


@router.get("/operators/{organization_id}/fare/options")
def get_operator_fare_options(
    organization_id: UUID, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _authorize(db, context, "operator.fare.propose", organization_id)
    operator = db.get(Organization, organization_id)
    if operator is None or operator.organization_type != "operator" or operator.status != "approved":
        raise HTTPException(status_code=409, detail="An approved operator organization is required.")
    routes = db.scalars(select(Route).where(Route.status == "published").order_by(Route.code).limit(300)).all()
    routes_by_id = {item.id: item for item in routes}
    trips = db.scalars(select(Trip).where(
        Trip.organization_id == organization_id, Trip.status.in_(["approved", "published"])
    ).order_by(Trip.departure_at.desc()).limit(300)).all()
    return {
        "routes": [{"id": str(item.id), "code": item.code} for item in routes],
        "trips": [{"id": str(item.id), "route_id": str(item.route_id),
                   "route_code": routes_by_id[item.route_id].code if item.route_id in routes_by_id else "Unknown route",
                   "departure_at": item.departure_at.isoformat(), "status": item.status}
                  for item in trips],
    }


@router.get("/operators/{organization_id}/fares")
def list_operator_fares(
    organization_id: UUID, context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "operator.fare.propose", organization_id)
    fares = db.scalars(select(Fare).where(
        Fare.organization_id == organization_id
    ).order_by(Fare.id.desc()).limit(300)).all()
    return _fare_payload(db, fares)


@router.get("/admin/fares")
def list_platform_fares(
    context: StaffContext = Depends(current_staff_context), db: Session = Depends(get_db),
) -> list[dict]:
    _authorize(db, context, "platform.fare.approve")
    fares = db.scalars(select(Fare).order_by(Fare.id.desc()).limit(500)).all()
    return _fare_payload(db, fares)
