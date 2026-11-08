import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.db.session import SessionLocal
from app.domains.identity.authorization import has_service_permission
from app.domains.identity.models import Permission, Role, RolePermission, User
from app.domains.organizations.models import Organization, OrganizationMembership
from app.domains.platform.models import ServiceRoleAssignment
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
        db.add_all([
            membership,
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
        assert not has_service_permission(
            db, user_id=user.id, organization_id=organization.id,
            service_code="move", permission_code=permission.code,
        )
        assert not has_service_permission(
            db, user_id=user.id, organization_id=other_organization.id,
            service_code="transit", permission_code=permission.code,
        )

        assignment.revoked_at = datetime.now(timezone.utc)
        db.flush()
        assert not has_service_permission(
            db, user_id=user.id, organization_id=organization.id,
            service_code="transit", permission_code=permission.code,
        )
        assignment.revoked_at = None
        membership.revoked_at = datetime.now(timezone.utc)
        db.flush()
        assert not has_service_permission(
            db, user_id=user.id, organization_id=organization.id,
            service_code="transit", permission_code=permission.code,
        )
