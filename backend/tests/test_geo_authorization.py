from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.domains.geo.security import (
    GeoAuthorizationError,
    require_geo_permission,
)
from app.domains.identity.models import Permission, Role, RoleAssignment, RolePermission, User
from app.domains.organizations.models import Organization, OrganizationMembership


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine, tables=[
        User.__table__, Role.__table__, Permission.__table__,
        RolePermission.__table__, RoleAssignment.__table__,
        Organization.__table__, OrganizationMembership.__table__,
    ])
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_tenant_permission_requires_active_membership_and_org_scoped_role(db):
    user = User(login_identifier="geo@example.test", display_name="Geo User", status="active")
    org = Organization(display_name="Tenant A", organization_type="operator", status="active")
    role = Role(code="operator_fleet_manager", description="Fleet manager")
    permission = Permission(code="platform.tracking.read", description="Read tracking")
    db.add_all([user, org, role, permission])
    db.flush()
    db.add_all([
        OrganizationMembership(
            user_id=user.id, organization_id=org.id,
            membership_status="active", revoked_at=None,
        ),
        RolePermission(role_id=role.id, permission_id=permission.id),
        RoleAssignment(
            user_id=user.id, role_id=role.id, organization_id=org.id,
            revoked_at=None,
        ),
    ])
    db.flush()

    require_geo_permission(
        db, user_id=user.id, organization_id=org.id,
        permission_code="platform.tracking.read",
    )


def test_revoked_membership_cannot_authorize_tenant_even_with_role_grant(db):
    user = User(login_identifier="revoked@example.test", display_name="Revoked", status="active")
    org = Organization(display_name="Tenant B", organization_type="operator", status="active")
    role = Role(code="operator_fleet_manager", description="Fleet manager")
    permission = Permission(code="platform.tracking.read", description="Read tracking")
    db.add_all([user, org, role, permission])
    db.flush()
    db.add_all([
        OrganizationMembership(
            user_id=user.id, organization_id=org.id,
            membership_status="active", revoked_at=__import__("datetime").datetime.now(),
        ),
        RolePermission(role_id=role.id, permission_id=permission.id),
        RoleAssignment(
            user_id=user.id, role_id=role.id, organization_id=org.id,
            revoked_at=None,
        ),
    ])
    db.flush()

    with pytest.raises(GeoAuthorizationError):
        require_geo_permission(
            db, user_id=user.id, organization_id=org.id,
            permission_code="platform.tracking.read",
        )


def test_explicit_platform_permission_can_select_tenant_without_membership(db):
    user = User(login_identifier="platform@example.test", display_name="Platform", status="active")
    org = Organization(display_name="Tenant C", organization_type="operator", status="active")
    role = Role(code="platform_dispatch_manager", description="Platform dispatch")
    permission = Permission(code="platform.tracking.read", description="Read tracking")
    db.add_all([user, org, role, permission])
    db.flush()
    db.add_all([
        RolePermission(role_id=role.id, permission_id=permission.id),
        RoleAssignment(user_id=user.id, role_id=role.id, organization_id=None, revoked_at=None),
    ])
    db.flush()

    require_geo_permission(
        db, user_id=user.id, organization_id=org.id,
        permission_code="platform.tracking.read",
    )


def test_missing_tenant_context_is_rejected(db):
    with pytest.raises(GeoAuthorizationError):
        require_geo_permission(
            db, user_id=uuid4(), organization_id=None,
            permission_code="platform.tracking.read",
        )
