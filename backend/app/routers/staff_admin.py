"""Role-scoped staff dashboards, access administration and scheduler monitoring."""
# ruff: noqa: B008, I001
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal, get_db
from app.domains.audit.models import AuditEvent
from app.domains.audit.service import record_event
from app.domains.bookings.models import Booking
from app.domains.catalog.models import Location, Route, Terminal
from app.domains.fares.models import Fare
from app.domains.fleet.models import Vehicle
from app.domains.identity.authorization import has_permission
from app.domains.identity.models import Permission, Role, RoleAssignment, RolePermission, User
from app.domains.identity.service import StaffContext
from app.domains.organizations.models import Organization, OrganizationInvitation, OrganizationMembership
from app.domains.support.passenger_models import PassengerSupportCase
from app.domains.support.report_models import PassengerReport
from app.domains.trips.models import Trip
from app.routers.auth import current_staff_context, require_csrf
from app.jobs.scheduler_service import run_scheduler_cycle, scheduler_snapshot

router = APIRouter(prefix="/admin", tags=["staff-admin"])


def _authorize(db: Session, context: StaffContext, permission: str) -> None:
    if not has_permission(db, user_id=context.user.id, permission_code=permission, organization_id=None):
        raise HTTPException(status_code=403, detail="Required platform permission is missing.")


def _access(db: Session, user_id: UUID) -> dict:
    rows = db.execute(
        select(RoleAssignment, Role, Permission)
        .join(Role, Role.id == RoleAssignment.role_id)
        .outerjoin(RolePermission, RolePermission.role_id == Role.id)
        .outerjoin(Permission, Permission.id == RolePermission.permission_id)
        .where(RoleAssignment.user_id == user_id, RoleAssignment.revoked_at.is_(None))
        .order_by(Role.code, Permission.code)
    ).all()
    assignments: dict[str, dict] = {}
    permissions: set[str] = set()
    for assignment, role, permission in rows:
        key = str(assignment.id)
        assignments.setdefault(key, {
            "assignment_id": key,
            "role_code": role.code,
            "role_description": role.description,
            "organization_id": str(assignment.organization_id) if assignment.organization_id else None,
            "assigned_at": assignment.assigned_at.isoformat(),
        })
        if permission is not None:
            permissions.add(permission.code)
    return {"roles": list(assignments.values()), "permissions": sorted(permissions)}


class RoleAssignmentRequest(BaseModel):
    role_code: str = Field(min_length=3, max_length=80)
    organization_id: UUID | None = None


@router.get("/dashboard")
def staff_dashboard(
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    access = _access(db, context.user.id)
    permissions = set(access["permissions"])
    if not permissions:
        raise HTTPException(status_code=403, detail="No active staff role is assigned.")
    module_map = [
        ("operations", "Operations", {"platform.operator.review", "platform.operator.create"}),
        ("catalog", "Catalog", {"platform.catalog.manage", "platform.catalog.publish"}),
        ("fleet", "Fleet", {"platform.fleet.review", "operator.fleet.manage"}),
        ("dispatch", "Dispatch", {"platform.trip.approve", "platform.trip.publish", "operator.trip.manage"}),
        ("fares", "Fares", {"platform.fare.approve", "platform.fare.publish", "operator.fare.propose"}),
        ("support", "Support and safety", {"platform.support.manage"}),
        ("access", "Staff access", {"platform.access.manage"}),
        ("audit", "Audit", {"platform.audit.read"}),
        ("scheduler", "Scheduler operations", {"platform.scheduler.read"}),
    ]
    modules = [{"key": key, "label": label} for key, label, required in module_map if permissions.intersection(required)]
    platform_scope = "platform.dashboard.read" in permissions
    organization_ids = sorted({
        UUID(role["organization_id"]) for role in access["roles"] if role["organization_id"]
    }, key=str)
    stats: dict[str, int] = {}
    if platform_scope:
        if permissions.intersection({"platform.operator.create", "platform.operator.review"}):
            stats["operators"] = db.scalar(select(func.count()).select_from(Organization)) or 0
        if "platform.fleet.review" in permissions:
            stats["vehicles"] = db.scalar(select(func.count()).select_from(Vehicle)) or 0
        if permissions.intersection({"platform.trip.approve", "platform.trip.publish"}):
            stats["trips"] = db.scalar(select(func.count()).select_from(Trip)) or 0
            stats["bookings"] = db.scalar(select(func.count()).select_from(Booking)) or 0
        if "platform.fare.approve" in permissions or "platform.fare.publish" in permissions:
            stats["fares"] = db.scalar(select(func.count()).select_from(Fare)) or 0
        if "platform.support.manage" in permissions:
            stats["support_cases"] = db.scalar(select(func.count()).select_from(PassengerSupportCase)) or 0
            stats["reports"] = db.scalar(select(func.count()).select_from(PassengerReport)) or 0
        if "platform.audit.read" in permissions:
            stats["audit_events"] = db.scalar(select(func.count()).select_from(AuditEvent)) or 0
        if permissions.intersection({"platform.catalog.manage", "platform.catalog.publish"}):
            stats["locations"] = db.scalar(select(func.count()).select_from(Location)) or 0
            stats["terminals"] = db.scalar(select(func.count()).select_from(Terminal)) or 0
            stats["routes"] = db.scalar(select(func.count()).select_from(Route)) or 0
        if "platform.access.manage" in permissions:
            stats["staff_accounts"] = db.scalar(select(func.count()).select_from(User)) or 0
            stats["active_role_assignments"] = db.scalar(select(func.count()).select_from(RoleAssignment).where(RoleAssignment.revoked_at.is_(None))) or 0
    elif organization_ids:
        if "operator.fleet.manage" in permissions:
            stats["vehicles"] = db.scalar(select(func.count()).select_from(Vehicle).where(Vehicle.organization_id.in_(organization_ids))) or 0
        if "operator.trip.manage" in permissions:
            stats["trips"] = db.scalar(select(func.count()).select_from(Trip).where(Trip.organization_id.in_(organization_ids))) or 0
            stats["bookings"] = db.scalar(select(func.count()).select_from(Booking).join(Trip, Trip.id == Booking.trip_id).where(Trip.organization_id.in_(organization_ids))) or 0
        if "operator.fare.propose" in permissions:
            stats["fares"] = db.scalar(select(func.count()).select_from(Fare).where(Fare.organization_id.in_(organization_ids))) or 0
    return {
        "staff": {"id": str(context.user.id), "display_name": context.user.display_name, "login_identifier": context.user.login_identifier},
        "roles": access["roles"], "permissions": access["permissions"],
        "modules": modules, "scope": "platform" if platform_scope else "organization",
        "stats": stats,
        "safety_boundaries": {
            "synthetic_data_only": settings.synthetic_data_only,
            "real_money_enabled": False, "ticketing_enabled": False,
            "boarding_authorized": False, "production_operations_enabled": False,
        },
    }


@router.get("/access/roles")
def list_access_roles(
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _authorize(db, context, "platform.access.manage")
    rows = db.execute(select(Role, Permission.code).outerjoin(
        RolePermission, RolePermission.role_id == Role.id
    ).outerjoin(Permission, Permission.id == RolePermission.permission_id).order_by(Role.code, Permission.code)).all()
    result: dict[str, dict] = {}
    for role, permission in rows:
        item = result.setdefault(str(role.id), {
            "id": str(role.id), "code": role.code, "description": role.description,
            "scope": "platform" if role.code.startswith(("platform_", "synthetic_platform_")) else "organization",
            "permissions": [],
        })
        if permission:
            item["permissions"].append(permission)
    return {"items": list(result.values())}


@router.get("/access/users")
def list_access_users(
    limit: int = 100,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _authorize(db, context, "platform.access.manage")
    users = list(db.scalars(select(User).order_by(User.created_at.desc()).limit(max(1, min(limit, 200)))))
    return {"items": [{
        "id": str(user.id), "display_name": user.display_name,
        "login_identifier": user.login_identifier, "status": user.status,
        "roles": _access(db, user.id)["roles"],
    } for user in users]}



@router.get("/access/organizations")
def list_access_organizations(
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _authorize(db, context, "platform.access.manage")
    organizations = db.scalars(select(Organization).where(
        Organization.organization_type == "operator",
        Organization.status == "approved",
    ).order_by(Organization.display_name)).all()
    return {"items": [{
        "id": str(item.id), "display_name": item.display_name, "status": item.status,
    } for item in organizations]}


@router.get("/access/invitations")
def list_access_invitations(
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _authorize(db, context, "platform.access.manage")
    now = db.scalar(select(func.now()))
    rows = db.execute(
        select(OrganizationInvitation, Organization, Role)
        .join(Organization, Organization.id == OrganizationInvitation.organization_id)
        .join(Role, Role.id == OrganizationInvitation.role_id)
        .where(
            OrganizationInvitation.accepted_at.is_(None),
            OrganizationInvitation.revoked_at.is_(None),
            OrganizationInvitation.expires_at > now,
        )
        .order_by(OrganizationInvitation.created_at.desc()).limit(200)
    ).all()
    return {"items": [{
        "id": str(invitation.id), "organization_id": str(organization.id),
        "organization_name": organization.display_name,
        "login_identifier": invitation.login_identifier,
        "display_name": invitation.display_name, "role_code": role.code,
        "created_at": invitation.created_at.isoformat(),
        "expires_at": invitation.expires_at.isoformat(),
    } for invitation, organization, role in rows]}


@router.post("/access/users/{user_id}/roles", status_code=201)
def assign_access_role(
    user_id: UUID, payload: RoleAssignmentRequest, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    _authorize(db, context, "platform.access.manage")
    if user_id == context.user.id:
        raise HTTPException(status_code=409, detail="Self-assignment is not permitted; a second authorized administrator is required.")
    user = db.get(User, user_id)
    role = db.scalar(select(Role).where(Role.code == payload.role_code))
    if user is None or user.status != "active" or role is None:
        raise HTTPException(status_code=404, detail="Active staff user or role not found.")
    is_platform_role = role.code.startswith(("platform_", "synthetic_platform_"))
    is_operator_role = role.code.startswith("operator_") or role.code == "synthetic_operator_manager"
    if role.code == "synthetic_platform_admin":
        raise HTTPException(status_code=403, detail="Synthetic platform administrator provisioning is restricted to the local interactive bootstrap.")
    if not is_platform_role and not is_operator_role:
        raise HTTPException(status_code=422, detail="Role scope is not assignable through this endpoint.")
    if is_platform_role and payload.organization_id is not None:
        raise HTTPException(status_code=422, detail="Platform roles cannot be organization-scoped.")
    if is_operator_role and payload.organization_id is None:
        raise HTTPException(status_code=422, detail="Operator roles require an organization scope.")
    if payload.organization_id is not None:
        org = db.get(Organization, payload.organization_id)
        membership = db.scalar(select(OrganizationMembership.id).where(
            OrganizationMembership.organization_id == payload.organization_id,
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.revoked_at.is_(None),
        ))
        if org is None or org.organization_type != "operator" or org.status != "approved" or membership is None:
            raise HTTPException(status_code=409, detail="An active membership in an approved operator organization is required.")
    duplicate = db.scalar(select(RoleAssignment.id).where(
        RoleAssignment.user_id == user_id, RoleAssignment.role_id == role.id,
        RoleAssignment.organization_id == payload.organization_id,
        RoleAssignment.revoked_at.is_(None),
    ))
    if duplicate:
        raise HTTPException(status_code=409, detail="Equivalent active role assignment already exists.")
    assignment = RoleAssignment(
        user_id=user_id, role_id=role.id, organization_id=payload.organization_id,
        assigned_by=context.user.id,
    )
    db.add(assignment)
    db.flush()
    record_event(
        db, event_type="staff.role.assigned", actor_type="staff", actor_id=str(context.user.id),
        actor_role_snapshot=",".join(item["role_code"] for item in _access(db, context.user.id)["roles"]), resource_type="role_assignment",
        resource_id=str(assignment.id), action="assign", outcome="success",
        organization_id=payload.organization_id,
        metadata={"role_code": role.code, "target_user_id": str(user_id)},
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Role assignment conflicts with an existing record.")
    return {
        "assignment_id": str(assignment.id), "user_id": str(user_id),
        "role_code": role.code,
        "organization_id": str(payload.organization_id) if payload.organization_id else None,
    }


@router.delete("/access/role-assignments/{assignment_id}")
def revoke_access_role(
    assignment_id: UUID, request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    _authorize(db, context, "platform.access.manage")
    active_admin_assignments = list(db.scalars(select(RoleAssignment.id).join(
        RolePermission, RolePermission.role_id == RoleAssignment.role_id
    ).join(Permission, Permission.id == RolePermission.permission_id).where(
        RoleAssignment.revoked_at.is_(None), RoleAssignment.organization_id.is_(None),
        Permission.code == "platform.access.manage",
    ).order_by(RoleAssignment.id).with_for_update()))
    assignment = db.scalar(select(RoleAssignment).where(
        RoleAssignment.id == assignment_id, RoleAssignment.revoked_at.is_(None)
    ).with_for_update())
    if assignment is None:
        raise HTTPException(status_code=404, detail="Active role assignment not found.")
    if assignment.user_id == context.user.id:
        raise HTTPException(status_code=409, detail="Self-revocation is not permitted.")
    if assignment.id in active_admin_assignments and len(active_admin_assignments) <= 1:
        raise HTTPException(status_code=409, detail="Cannot revoke the last active platform access administrator.")
    assignment.revoked_at = db.scalar(select(func.now()))
    record_event(
        db, event_type="staff.role.revoked", actor_type="staff", actor_id=str(context.user.id),
        actor_role_snapshot="platform_access_manager", resource_type="role_assignment",
        resource_id=str(assignment.id), action="revoke", outcome="success",
        organization_id=assignment.organization_id, metadata={"target_user_id": str(assignment.user_id)},
    )
    db.commit()
    return {"assignment_id": str(assignment.id), "revoked": True}


@router.get("/operations/scheduler")
def read_scheduler_operations(
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    _authorize(db, context, "platform.scheduler.read")
    snapshot = scheduler_snapshot(db, stale_after_seconds=settings.scheduler_lease_seconds)
    return {
        **snapshot,
        "runtime": {
            "app_env": settings.app_env,
            "synthetic_data_only": settings.synthetic_data_only,
            "scheduler_enabled": settings.scheduler_enabled,
            "remote_database_allowed": False,
            "production_operations_enabled": False,
        },
    }


@router.post("/operations/scheduler/run-once")
def run_scheduler_once(
    request: Request,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> dict:
    require_csrf(request, context)
    if settings.app_env not in {"development", "test"} or not settings.synthetic_data_only or not settings.scheduler_enabled:
        raise HTTPException(status_code=409, detail="Scheduler manual execution is disabled by the current safety configuration.")
    _authorize(db, context, "platform.scheduler.manage")
    result = run_scheduler_cycle(
        SessionLocal, worker_id=f"admin-once-{uuid4()}",
        batch_size=settings.scheduler_batch_size,
        lease_seconds=settings.scheduler_lease_seconds,
    )
    return result
