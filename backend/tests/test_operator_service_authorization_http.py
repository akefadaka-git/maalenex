import os
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.domains.identity.models import Permission, Role, RolePermission, StaffSession, User
from app.domains.identity.security import issue_opaque_token, token_digest
from app.domains.organizations.models import Organization, OrganizationMembership
from app.domains.platform.models import ServiceRoleAssignment
from app.main import app
from scripts.seed_platform_services import seed

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires the isolated PostgreSQL CI service.",
)


def _create_service_principal(db, organization_ids, service_codes):
    suffix = uuid4().hex
    user = User(
        login_identifier=f"service-http-{suffix}@maalenex.invalid",
        display_name="Synthetic service HTTP principal",
        status="active",
    )
    role = Role(
        code=f"service-http-role-{suffix}",
        description="Synthetic HTTP service role",
    )
    permission_codes = {
        "fleet": "operator.fleet.manage",
        "transit": "operator.trip.manage",
    }
    permissions = {}
    for service_code in service_codes:
        permission_code = permission_codes[service_code]
        permission = db.scalar(select(Permission).where(Permission.code == permission_code))
        if permission is None:
            permission = Permission(
                code=permission_code,
                description=f"Synthetic {service_code.title()} management permission",
            )
            db.add(permission)
            db.flush()
        permissions[service_code] = permission
    db.add_all([user, role])
    db.flush()
    db.add_all(
        RolePermission(role_id=role.id, permission_id=permission.id)
        for permission in permissions.values()
    )
    for organization_id in organization_ids:
        db.add(OrganizationMembership(
            organization_id=organization_id,
            user_id=user.id,
            membership_status="active",
        ))
        for service_code in service_codes:
            db.add(ServiceRoleAssignment(
                user_id=user.id,
                organization_id=organization_id,
                service_code=service_code,
                role_id=role.id,
            )) if organization_id == organization_ids[0] else None
    now = db.scalar(select(func.now()))
    session_token = issue_opaque_token()
    csrf_token = issue_opaque_token()
    db.add(StaffSession(
        user_id=user.id,
        secret_hash=token_digest(session_token),
        csrf_token_hash=token_digest(csrf_token),
        expires_at=now + timedelta(hours=8),
    ))
    db.flush()
    return session_token, csrf_token


def test_authenticated_fleet_operator_route_enforces_service_and_tenant_boundary():
    seed()
    with SessionLocal() as db:
        suffix = uuid4().hex
        tenant_a = Organization(
            organization_type="operator",
            display_name=f"Synthetic Fleet tenant A {suffix}",
            status="approved",
        )
        tenant_b = Organization(
            organization_type="operator",
            display_name=f"Synthetic Fleet tenant B {suffix}",
            status="approved",
        )
        db.add_all([tenant_a, tenant_b])
        db.flush()
        session_token, csrf_token = _create_service_principal(
            db, [tenant_a.id, tenant_b.id], ["fleet"],
        )
        tenant_a_id, tenant_b_id = tenant_a.id, tenant_b.id
        db.commit()

    client = TestClient(app)
    client.cookies.set("mnm_staff_session", session_token, path="/")
    client.cookies.set("mnm_csrf", csrf_token, path="/")
    headers = {"X-CSRF-Token": csrf_token, "Origin": "http://localhost:5173"}

    allowed = client.post(
        f"/api/v1/operators/{tenant_a_id}/vehicles",
        headers=headers,
        json={"vehicle_reference": "SYN-FLEET-HTTP-A"},
    )
    assert allowed.status_code == 201, allowed.text

    denied = client.post(
        f"/api/v1/operators/{tenant_b_id}/vehicles",
        headers=headers,
        json={"vehicle_reference": "SYN-FLEET-HTTP-B"},
    )
    assert denied.status_code == 403, denied.text


def test_authenticated_transit_operator_route_rejects_cross_tenant_service_use():
    seed()
    with SessionLocal() as db:
        suffix = uuid4().hex
        tenant_a = Organization(
            organization_type="operator",
            display_name=f"Synthetic Transit tenant A {suffix}",
            status="approved",
        )
        tenant_b = Organization(
            organization_type="operator",
            display_name=f"Synthetic Transit tenant B {suffix}",
            status="approved",
        )
        db.add_all([tenant_a, tenant_b])
        db.flush()
        session_token, csrf_token = _create_service_principal(
            db, [tenant_a.id, tenant_b.id], ["transit"],
        )
        tenant_a_id, tenant_b_id = tenant_a.id, tenant_b.id
        db.commit()

    client = TestClient(app)
    client.cookies.set("mnm_staff_session", session_token, path="/")
    client.cookies.set("mnm_csrf", csrf_token, path="/")
    headers = {"X-CSRF-Token": csrf_token, "Origin": "http://localhost:5173"}
    trip_payload = {
        "route_id": str(uuid4()),
        "boarding_terminal_id": str(uuid4()),
        "vehicle_id": str(uuid4()),
        "seat_layout_version_id": str(uuid4()),
        "departure_at": "2027-01-01T09:00:00+03:00",
        "arrival_estimate_at": "2027-01-01T12:00:00+03:00",
    }

    # The assigned Transit grant reaches domain validation in the assigned tenant.
    allowed_tenant = client.post(
        f"/api/v1/operators/{tenant_a_id}/trips",
        headers=headers,
        json=trip_payload,
    )
    assert allowed_tenant.status_code == 409, allowed_tenant.text
    assert "Route is not published" in allowed_tenant.text

    # The same authenticated user is a member of tenant B, but has no Transit
    # service-role assignment there. Membership alone must not authorize it.
    denied_tenant = client.post(
        f"/api/v1/operators/{tenant_b_id}/trips",
        headers=headers,
        json=trip_payload,
    )
    assert denied_tenant.status_code == 403, denied_tenant.text
