"""Tenant-aware authorization and transaction-local PostgreSQL geo context."""
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.domains.identity.authorization import has_permission
from app.domains.organizations.models import OrganizationMembership


class GeoAuthorizationError(PermissionError):
    """Raised when a user cannot access geographic data for a tenant."""


def require_geo_permission(
    db: Session, *, user_id: UUID, organization_id: UUID, permission_code: str,
) -> None:
    """Require an active tenant membership plus scoped grant, or explicit platform grant."""
    if organization_id is None:
        raise GeoAuthorizationError("An organization context is required")

    membership = db.scalar(select(OrganizationMembership.id).where(
        OrganizationMembership.user_id == user_id,
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.membership_status == "active",
        OrganizationMembership.revoked_at.is_(None),
    ))
    if membership is not None and has_permission(
        db, user_id=user_id, permission_code=permission_code,
        organization_id=organization_id,
    ):
        return

    # Platform-wide authority is explicit: a NULL-organization platform grant.
    if permission_code.startswith("platform.") and has_permission(
        db, user_id=user_id, permission_code=permission_code,
        organization_id=None,
    ):
        return

    raise GeoAuthorizationError("Active organization membership and permission are required")


def set_geo_tenant_context(db: Session, *, organization_id: UUID) -> None:
    """Set PostgreSQL RLS context for the current transaction only."""
    if organization_id is None:
        raise GeoAuthorizationError("An organization context is required")
    db.execute(text("""
        SELECT pg_catalog.set_config(
            'app.current_organization_id', :organization_id, true
        )
    """), {"organization_id": str(organization_id)})


def authorize_geo_tenant_context(
    db: Session, *, user_id: UUID, organization_id: UUID, permission_code: str,
) -> None:
    """Authorize the tenant, then set its transaction-local RLS context."""
    require_geo_permission(
        db, user_id=user_id, organization_id=organization_id,
        permission_code=permission_code,
    )
    set_geo_tenant_context(db, organization_id=organization_id)
