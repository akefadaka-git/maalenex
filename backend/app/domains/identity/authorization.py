from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.domains.identity.models import Permission, RoleAssignment, RolePermission, User
from app.domains.organizations.models import Organization, OrganizationMembership
from app.domains.platform.models import ServiceRoleAssignment


def has_permission(
    db: Session, *, user_id: UUID, permission_code: str,
    organization_id: UUID | None,
) -> bool:
    statement = (
        select(Permission.id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(RoleAssignment, RoleAssignment.role_id == RolePermission.role_id)
        .join(User, User.id == RoleAssignment.user_id)
        .where(
            RoleAssignment.user_id == user_id,
            RoleAssignment.revoked_at.is_(None),
            User.status == "active",
            Permission.code == permission_code,
        )
    )
    if organization_id is None:
        # Platform-wide grants are explicit and cannot be inferred from a null tenant.
        statement = statement.where(
            RoleAssignment.organization_id.is_(None), Permission.code.like("platform.%")
        )
    else:
        # Tenant grants require both an exact organization match and a live membership.
        statement = (
            statement
            .join(OrganizationMembership, and_(
                OrganizationMembership.organization_id == RoleAssignment.organization_id,
                OrganizationMembership.user_id == RoleAssignment.user_id,
            ))
            .join(Organization, Organization.id == RoleAssignment.organization_id)
            .where(
                RoleAssignment.organization_id == organization_id,
                OrganizationMembership.membership_status == "active",
                OrganizationMembership.revoked_at.is_(None),
                Organization.status == "approved",
            )
        )
    return db.scalar(statement.limit(1)) is not None


def has_service_permission(
    db: Session, *, user_id: UUID, organization_id: UUID,
    service_code: str, permission_code: str,
) -> bool:
    """Require an active principal, organization membership and service-scoped grant."""
    statement = (
        select(Permission.id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(ServiceRoleAssignment, ServiceRoleAssignment.role_id == RolePermission.role_id)
        .join(OrganizationMembership, and_(
            OrganizationMembership.organization_id == ServiceRoleAssignment.organization_id,
            OrganizationMembership.user_id == ServiceRoleAssignment.user_id,
        ))
        .join(Organization, Organization.id == ServiceRoleAssignment.organization_id)
        .join(User, User.id == ServiceRoleAssignment.user_id)
        .where(
            ServiceRoleAssignment.user_id == user_id,
            ServiceRoleAssignment.organization_id == organization_id,
            ServiceRoleAssignment.service_code == service_code,
            ServiceRoleAssignment.revoked_at.is_(None),
            OrganizationMembership.membership_status == "active",
            OrganizationMembership.revoked_at.is_(None),
            Organization.status == "approved",
            User.status == "active",
            Permission.code == permission_code,
        )
    )
    return db.scalar(statement.limit(1)) is not None
