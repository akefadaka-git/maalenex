import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.db.session import SessionLocal
from app.domains.identity.authorization import has_permission, has_service_permission
from app.domains.identity.models import (
    Permission, Role, RoleAssignment, RolePermission, User,
)
from app.domains.identity.service import StaffContext
from app.domains.organizations.models import Organization, OrganizationMembership
from app.domains.platform.models import ServiceRoleAssignment
from app.routers.admin import _authorize
from scripts.seed_platform_services import seed

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires the isolated PostgreSQL CI service.",
)


def test_service_permission_requires_matching_service_active_membership_and_organization():
    seed()
    with SessionLocal.begin() as db:
        suffix = uuid4().hex
        user = User(
            login_identifier=f"service-role-{suffix}@maalenex.invalid",
            display_name="Synthetic service role user", status="active",
        )
        organization = Organization(
            organization_type="operator", display_name=f"Synthetic operator {suffix}", status="approved"
        )
        other_organization = Organization(
            organization_type="merchant", display_name=f"Synthetic merchant {suffix}", status="approved"
        )
        role = Role(code=f"transit.reader.{suffix}", description="Synthetic Transit reader")
        permission = Permission(code=f"transit.trips.read.{suffix}", description="Read Transit trips")
        db.add_all([user, organization, other_organization, role, permission])
        db.flush()
        membership = OrganizationMembership(
            organization_id=organization.id, user_id=user.id,
            membership_status="active",
        )
        other_membership = OrganizationMembership(
            organization_id=other_organization.id, user_id=user.id,
            membership_status="active",
        )
        db.add_all([
            membership, other_membership,
            RolePermission(role_id=role.id, permission_id=permission.id),
        ])
        assignment = ServiceRoleAssignment(
            user_id=user.id, organization_id=organization.id,
            service_code="transit", role_id=role.id,
        )
        db.add(assignment)
        db.flush()

        assert has_service_permission(
            db, user_id=user.id, organization_id=organization.id,
            service_code="transit", permission_code=permission.code,
        )
        # Even membership in another tenant does not transfer this service grant.
        assert not has_service_permission(
            db, user_id=user.id, organization_id=other_organization.id,
            service_code="transit", permission_code=permission.code,
        )
        assert not has_service_permission(
            db, user_id=user.id, organization_id=organization.id,
            service_code="move", permission_code=permission.code,
        )

        assignment.revoked_at = datetime.now(timezone.utc)
        db.flush()
        assert not has_service_permission(
            db, user_id=user.id, organization_id=organization.id,
            service_code="transit", permission_code=permission.code,
        )
        assignment.revoked_at = None
        membership.revoked_at = datetime.now(timezone.utc)
        membership.membership_status = "revoked"
        db.flush()
        assert not has_service_permission(
            db, user_id=user.id, organization_id=organization.id,
            service_code="transit", permission_code=permission.code,
        )


def test_organization_route_guard_denies_cross_tenant_and_inactive_membership():
    with SessionLocal.begin() as db:
        suffix = uuid4().hex
        user = User(
            login_identifier=f"tenant-guard-{suffix}@maalenex.invalid",
            display_name="Synthetic tenant guard user", status="active",
        )
        organization = Organization(
            organization_type="operator", display_name=f"Tenant A {suffix}", status="approved"
        )
        other_organization = Organization(
            organization_type="operator", display_name=f"Tenant B {suffix}", status="approved"
        )
        role = Role(code=f"tenant.operator.{suffix}", description="Synthetic tenant operator")
        permission = Permission(
            code=f"operator.fleet.manage.{suffix}", description="Manage tenant fleet"
        )
        db.add_all([user, organization, other_organization, role, permission])
        db.flush()
        membership = OrganizationMembership(
            organization_id=organization.id, user_id=user.id, membership_status="active",
        )
        other_membership = OrganizationMembership(
            organization_id=other_organization.id, user_id=user.id, membership_status="active",
        )
        assignment = RoleAssignment(
            user_id=user.id, role_id=role.id, organization_id=organization.id,
        )
        db.add_all([
            membership, other_membership, assignment,
            RolePermission(role_id=role.id, permission_id=permission.id),
        ])
        db.flush()

        context = StaffContext(user=user, session=None)
        permission_code = permission.code

        # The same principal is an active member of both tenants, but the grant
        # is bound only to Tenant A.
        assert has_permission(
            db, user_id=user.id, permission_code=permission_code,
            organization_id=organization.id,
        )
        assert not has_permission(
            db, user_id=user.id, permission_code=permission_code,
            organization_id=other_organization.id,
        )
        with pytest.raises(HTTPException) as denied:
            _authorize(db, context, permission_code, other_organization.id)
        assert denied.value.status_code == 403

        # A revoked membership invalidates an otherwise-unrevoked tenant role.
        membership.membership_status = "revoked"
        membership.revoked_at = datetime.now(timezone.utc)
        db.flush()
        assert not has_permission(
            db, user_id=user.id, permission_code=permission_code,
            organization_id=organization.id,
        )
        with pytest.raises(HTTPException) as revoked:
            _authorize(db, context, permission_code, organization.id)
        assert revoked.value.status_code == 403

        # An inactive principal cannot use a stale assignment either.
        user.status = "suspended"
        membership.membership_status = "active"
        membership.revoked_at = None
        db.flush()
        assert not has_permission(
            db, user_id=user.id, permission_code=permission_code,
            organization_id=organization.id,
        )
