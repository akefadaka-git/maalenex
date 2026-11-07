from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from uuid import UUID, uuid4
import os

import pytest
from sqlalchemy import func, select
from app.db.session import SessionLocal
from app.domains.bookings.service import BookingConflict, accept_reservation, create_seat_hold
from app.domains.bookings.maintenance import expire_stale_holds
from app.domains.catalog.models import Location, Route, Terminal
from app.domains.fares.models import Fare, FareVersion
from app.domains.fleet.models import SeatLayoutVersion, Vehicle, VehicleSeat
from app.domains.identity.models import User
from app.domains.organizations.models import Organization
from app.domains.trips.models import Trip, TripSeat
from app.domains.reservations.models import BookingAccessGrant
from app.domains.bookings.access import revoke_booking_grants
from app.domains.identity.security import issue_opaque_token, token_digest
from app.domains.identity.models import Credential, Permission, Role, RoleAssignment, RolePermission, StaffSession
from app.domains.organizations.models import OrganizationInvitation, OrganizationMembership
from app.domains.support.models import SupportCase
from fastapi.testclient import TestClient
from app.main import app


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires the isolated PostgreSQL CI service.",
)


def _seed_single_seat_trip() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        operator = Organization(display_name="Synthetic concurrency operator", status="approved")
        origin = Location(name="Synthetic Jinka", location_type="city", status="published")
        destination = Location(name="Synthetic destination", location_type="city", status="published")
        db.add_all([operator, origin, destination])
        db.flush()

        terminal = Terminal(location_id=origin.id, name="Synthetic terminal", status="published")
        route = Route(
            code="SYN-" + uuid4().hex[:12].upper(),
            origin_location_id=origin.id, destination_location_id=destination.id,
            status="published",
        )
        db.add_all([terminal, route])
        db.flush()

        vehicle = Vehicle(
            organization_id=operator.id, vehicle_reference="SYN-" + uuid4().hex[:8],
            status="active", review_status="approved",
        )
        db.add(vehicle)
        db.flush()
        layout = SeatLayoutVersion(vehicle_id=vehicle.id, version_number=1, status="approved")
        db.add(layout)
        db.flush()
        vehicle_seat = VehicleSeat(
            seat_layout_version_id=layout.id, seat_code="A1",
            position_metadata={}, seat_type="standard", is_sellable=True,
        )
        db.add(vehicle_seat)
        db.flush()

        trip = Trip(
            organization_id=operator.id, route_id=route.id,
            boarding_terminal_id=terminal.id, vehicle_id=vehicle.id,
            seat_layout_version_id=layout.id, departure_at=now + timedelta(days=1),
            status="published",
        )
        db.add(trip)
        db.flush()
        trip_seat = TripSeat(
            trip_id=trip.id, vehicle_seat_id=vehicle_seat.id,
            seat_code_snapshot="A1", sellable_status="sellable",
        )
        proposer = User(
            login_identifier="synthetic-" + uuid4().hex + "@example.test",
            display_name="Synthetic Fare Proposer", status="active",
        )
        db.add_all([trip_seat, proposer])
        db.flush()
        fare = Fare(organization_id=operator.id, route_id=route.id, status="published")
        db.add(fare)
        db.flush()
        fare_version = FareVersion(
            fare_id=fare.id, version_number=1, amount_minor_units=125000,
            currency_code="ETB", effective_from=now - timedelta(hours=1),
            status="published", proposed_by=proposer.id,
        )
        db.add(fare_version)
        db.commit()
        return str(trip.id), str(trip_seat.id)


def test_postgres_concurrent_holds_cannot_allocate_the_same_trip_seat():
    trip_id, seat_id = _seed_single_seat_trip()
    barrier = Barrier(2)

    def attempt(index: int) -> str:
        with SessionLocal() as db:
            try:
                barrier.wait(timeout=10)
                booking = create_seat_hold(
                    db, trip_id=UUID(trip_id),
                    contact_name=f"Synthetic Passenger {index}",
                    contact_phone=f"+25190000000{index}",
                    passengers=[{"name": f"Passenger {index}"}],
                    seat_ids=[UUID(seat_id)],
                    idempotency_key="concurrency-" + uuid4().hex,
                    hold_minutes=10,
                )
                db.commit()
                return "created:" + str(booking.id)
            except BookingConflict:
                db.rollback()
                return "conflict"
            except Exception:
                db.rollback()
                raise

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, (1, 2)))

    assert sum(item.startswith("created:") for item in results) == 1, results
    assert results.count("conflict") == 1, results

    with SessionLocal() as db:
        from sqlalchemy import func, select
        from app.domains.bookings.models import SeatAllocation
        active = db.scalar(select(func.count(SeatAllocation.id)).where(
            SeatAllocation.trip_id == __import__("uuid").UUID(trip_id),
            SeatAllocation.trip_seat_id == __import__("uuid").UUID(seat_id),
            SeatAllocation.status == "active",
        ))
        assert active == 1


def test_postgres_maintenance_expires_holds_and_releases_allocations():
    from app.domains.bookings.models import Booking, SeatAllocation, SeatHold

    trip_id, seat_id = _seed_single_seat_trip()
    with SessionLocal() as db:
        booking = create_seat_hold(
            db, trip_id=UUID(trip_id), contact_name="Synthetic Contact",
            contact_phone="+251900000001", passengers=[{"name": "Synthetic Passenger"}],
            seat_ids=[UUID(seat_id)], idempotency_key="maintenance-" + uuid4().hex,
            hold_minutes=10,
        )
        booking_id = booking.id
        past = db.scalar(select(func.now())) - timedelta(minutes=1)
        booking.expires_at = past
        hold = db.scalar(select(SeatHold).where(SeatHold.booking_id == booking_id))
        hold.expires_at = past
        db.commit()
        assert expire_stale_holds(db, batch_size=50) == 1
        db.commit()
        db.refresh(booking)
        db.refresh(hold)
        allocation = db.scalar(select(SeatAllocation).where(SeatAllocation.booking_id == booking_id))
        assert booking.status == "expired"
        assert hold.status == "expired"
        assert allocation.status == "expired"


def test_postgres_guest_can_revoke_all_active_booking_access_grants():
    trip_id, seat_id = _seed_single_seat_trip()
    with SessionLocal() as db:
        booking = create_seat_hold(
            db, trip_id=UUID(trip_id), contact_name="Synthetic Contact",
            contact_phone="+251900000002", passengers=[{"name": "Synthetic Passenger"}],
            seat_ids=[UUID(seat_id)], idempotency_key="revoke-" + uuid4().hex,
            hold_minutes=10,
        )
        now = db.scalar(select(func.now()))
        grant = BookingAccessGrant(
            booking_id=booking.id, credential_hash="a" * 64,
            csrf_token_hash="b" * 64, scope="manage",
            expires_at=now + timedelta(hours=1),
        )
        db.add(grant)
        db.flush()
        assert revoke_booking_grants(db, booking_id=booking.id) == 1
        db.commit()
        db.refresh(grant)
        assert grant.revoked_at is not None


def test_postgres_operator_invitation_is_single_use_and_creates_scoped_membership():
    token = issue_opaque_token()
    with SessionLocal() as db:
        operator = Organization(display_name="Synthetic invited operator", status="approved")
        inviter = User(
            login_identifier="inviter-" + uuid4().hex + "@example.test",
            display_name="Synthetic Inviter", status="active",
        )
        role = Role(code="synthetic_operator_manager", description="Synthetic operator manager")
        db.add_all([operator, inviter, role])
        db.flush()
        invitation = OrganizationInvitation(
            organization_id=operator.id,
            login_identifier="invitee-" + uuid4().hex + "@example.test",
            display_name="Synthetic Invitee",
            role_id=role.id, token_hash=token_digest(token),
            created_by=inviter.id,
            expires_at=db.scalar(select(func.now())) + timedelta(hours=1),
        )
        db.add(invitation)
        db.commit()
        organization_id = operator.id
        login_identifier = invitation.login_identifier

    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/operator-invitations/accept",
        json={"token": token, "password": "Synthetic-Password-2026!"},
    )
    assert response.status_code == 201, response.text
    assert response.json()["login_identifier"] == login_identifier
    replay = client.post(
        "/api/v1/auth/operator-invitations/accept",
        json={"token": token, "password": "Synthetic-Password-2026!"},
    )
    assert replay.status_code == 404

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.login_identifier == login_identifier))
        membership = db.scalar(select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.revoked_at.is_(None),
        ))
        assignment = db.scalar(select(RoleAssignment).where(
            RoleAssignment.organization_id == organization_id,
            RoleAssignment.user_id == user.id,
            RoleAssignment.revoked_at.is_(None),
        ))
        credential = db.scalar(select(Credential).where(Credential.user_id == user.id))
        assert user.status == "active"
        assert membership is not None and assignment is not None and credential is not None


def test_postgres_guest_support_case_and_access_revocation_flow():
    trip_id, seat_id = _seed_single_seat_trip()
    access_token = issue_opaque_token()
    csrf_token = issue_opaque_token()
    with SessionLocal() as db:
        booking = create_seat_hold(
            db, trip_id=UUID(trip_id), contact_name="Synthetic Contact",
            contact_phone="+251900000003", passengers=[{"name": "Synthetic Passenger"}],
            seat_ids=[UUID(seat_id)], idempotency_key="support-" + uuid4().hex,
            hold_minutes=10,
        )
        booking_id = booking.id
        accept_reservation(db, booking_id=booking_id)
        db.add(BookingAccessGrant(
            booking_id=booking_id,
            credential_hash=token_digest(access_token),
            csrf_token_hash=token_digest(csrf_token),
            scope="manage",
            expires_at=db.scalar(select(func.now())) + timedelta(hours=1),
        ))
        db.commit()

    client = TestClient(app)
    cookie_path = f"/api/v1/bookings/{booking_id}"
    client.cookies.set("mnm_booking_access", access_token, path=cookie_path)
    client.cookies.set("mnm_booking_csrf", csrf_token, path="/")
    headers = {"Origin": "http://localhost:5173", "X-CSRF-Token": csrf_token}
    qr = client.get(f"/api/v1/bookings/{booking_id}/reservation/qr.svg")
    assert qr.status_code == 200, qr.text
    assert "image/svg+xml" in qr.headers["content-type"]
    assert "<svg" in qr.text
    assert qr.headers["cache-control"] == "no-store, private"
    created = client.post(
        f"/api/v1/bookings/{booking_id}/support-cases",
        headers=headers,
        json={
            "category": "reservation_status",
            "subject": "Synthetic reservation question",
            "message": "Please confirm the current reservation status for this synthetic test.",
        },
    )
    assert created.status_code == 201, created.text
    listed = client.get(f"/api/v1/bookings/{booking_id}/support-cases")
    assert listed.status_code == 200
    assert listed.json()[0]["case_reference"] == created.json()["case_reference"]

    revoked = client.post(
        f"/api/v1/bookings/{booking_id}/access/revoke", headers=headers,
    )
    assert revoked.status_code == 200, revoked.text
    assert revoked.json()["access_revoked"] is True
    denied = client.get(f"/api/v1/bookings/{booking_id}")
    assert denied.status_code == 401


def _create_staff_session(db, *, organization_id=None, permission_code="platform.support.manage"):
    user = User(
        login_identifier="synthetic-staff-" + uuid4().hex + "@example.test",
        display_name="Synthetic Staff Reviewer", status="active",
    )
    role = Role(code="synthetic-role-" + uuid4().hex[:12], description="Synthetic test role")
    permission = Permission(code=permission_code, description="Synthetic test permission")
    db.add_all([user, role, permission])
    db.flush()
    db.add_all([
        RolePermission(role_id=role.id, permission_id=permission.id),
        RoleAssignment(
            user_id=user.id, role_id=role.id,
            organization_id=organization_id, assigned_by=user.id,
        ),
    ])
    session_token = issue_opaque_token()
    csrf_token = issue_opaque_token()
    now = db.scalar(select(func.now()))
    db.add(StaffSession(
        user_id=user.id, secret_hash=token_digest(session_token),
        csrf_token_hash=token_digest(csrf_token),
        expires_at=now + timedelta(hours=8),
    ))
    db.flush()
    return session_token, csrf_token


def test_postgres_support_staff_can_claim_and_resolve_cases():
    trip_id, seat_id = _seed_single_seat_trip()
    with SessionLocal() as db:
        booking = create_seat_hold(
            db, trip_id=UUID(trip_id), contact_name="Synthetic Contact",
            contact_phone="+251900000004", passengers=[{"name": "Synthetic Passenger"}],
            seat_ids=[UUID(seat_id)], idempotency_key="support-staff-" + uuid4().hex,
        )
        case = SupportCase(
            case_reference="MNM-SUP-" + uuid4().hex[:16].upper(),
            booking_id=booking.id, category="reservation_status",
            subject="Synthetic support case",
            message="Synthetic support message for staff workflow verification.",
            status="open",
        )
        db.add(case)
        session_token, csrf_token = _create_staff_session(db)
        case_id = case.id
        case_reference = case.case_reference
        db.commit()

    client = TestClient(app)
    client.cookies.set("mnm_staff_session", session_token, path="/")
    client.cookies.set("mnm_csrf", csrf_token, path="/")
    headers = {"X-CSRF-Token": csrf_token, "Origin": "http://localhost:5173"}
    listed = client.get("/api/v1/support/cases")
    assert listed.status_code == 200, listed.text
    assert any(item["case_reference"] == case_reference for item in listed.json())
    claimed = client.post(f"/api/v1/support/cases/{case_id}/claim", headers=headers)
    assert claimed.status_code == 200, claimed.text
    resolved = client.post(
        f"/api/v1/support/cases/{case_id}/resolve",
        headers=headers,
        json={"resolution_code": "information_provided", "resolution_note": "Synthetic case resolved."},
    )
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()["status"] == "resolved"


def test_postgres_manifest_is_operator_scoped_and_excludes_contact_phone():
    trip_id, seat_id = _seed_single_seat_trip()
    with SessionLocal() as db:
        trip = db.get(Trip, UUID(trip_id))
        booking = create_seat_hold(
            db, trip_id=UUID(trip_id), contact_name="Private Synthetic Contact",
            contact_phone="+251900000005", passengers=[{"name": "Manifest Passenger"}],
            seat_ids=[UUID(seat_id)], idempotency_key="manifest-" + uuid4().hex,
        )
        accept_reservation(db, booking_id=booking.id)
        session_token, csrf_token = _create_staff_session(
            db, organization_id=trip.organization_id,
            permission_code="operator.trip.manifest.read",
        )
        db.commit()

    client = TestClient(app)
    client.cookies.set("mnm_staff_session", session_token, path="/")
    client.cookies.set("mnm_csrf", csrf_token, path="/")
    response = client.get(f"/api/v1/trips/{trip_id}/manifest")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["passenger_count"] == 1
    assert payload["manifest"][0]["passenger_name"] == "Manifest Passenger"
    assert payload["contact_phone_included"] is False
    assert "+251900000005" not in response.text
    assert payload["boarding_authorized"] is False
