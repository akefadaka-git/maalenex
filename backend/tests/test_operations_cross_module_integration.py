from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.domains.audit.models import AuditEvent
from app.domains.catalog.models import Location, Route, RouteStop, Terminal
from app.domains.fares.models import Fare, FareApproval, FareVersion
from app.domains.fleet.models import SeatLayoutVersion, Vehicle, VehicleSeat
from app.domains.identity.models import Permission, Role, RoleAssignment, RolePermission, User
from app.domains.organizations.models import Organization
from app.domains.trips.models import Trip, TripSeat
from app.main import app
from app.routers import admin


@pytest.fixture
def operations_client(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    tables = [
        User.__table__, Role.__table__, Permission.__table__, RolePermission.__table__,
        RoleAssignment.__table__, Organization.__table__, Location.__table__,
        Terminal.__table__, Route.__table__, RouteStop.__table__, Vehicle.__table__,
        SeatLayoutVersion.__table__, VehicleSeat.__table__, Trip.__table__,
        TripSeat.__table__, Fare.__table__, FareVersion.__table__,
        FareApproval.__table__, AuditEvent.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    db = Session(engine)
    operator_a = Organization(
        organization_type="operator", display_name="Synthetic Operator A", status="approved",
    )
    operator_b = Organization(
        organization_type="operator", display_name="Synthetic Operator B", status="approved",
    )
    db.add_all([operator_a, operator_b])
    db.flush()

    users = {
        name: User(
            login_identifier=f"{name}@example.test",
            display_name=f"Synthetic {name}",
            status="active",
        )
        for name in (
            "operator", "catalog", "fleet_reviewer", "trip_manager",
            "fare_reviewer", "fare_publisher",
        )
    }
    db.add_all(users.values())
    db.flush()

    grants = {
        "operator": (
            "operator.fleet.manage", "operator.trip.manage", "operator.fare.propose",
        ),
        "catalog": ("platform.catalog.manage", "platform.catalog.publish"),
        "fleet_reviewer": ("platform.fleet.review",),
        "trip_manager": ("platform.trip.approve", "platform.trip.publish"),
        "fare_reviewer": ("platform.fare.approve",),
        "fare_publisher": ("platform.fare.publish",),
    }
    for name, codes in grants.items():
        role = Role(code=f"test_{name}_role", description=f"Integration role for {name}")
        db.add(role)
        db.flush()
        for code in codes:
            permission = db.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code, description=f"Test grant {code}")
                db.add(permission)
                db.flush()
            db.add(RolePermission(role_id=role.id, permission_id=permission.id))
        db.add(RoleAssignment(
            user_id=users[name].id, role_id=role.id,
            organization_id=operator_a.id if name == "operator" else None,
            assigned_by=users[name].id,
        ))
    db.commit()
    user_ids = {name: user.id for name, user in users.items()}
    organization_ids = {"a": operator_a.id, "b": operator_b.id}
    db.close()

    selected_user_id = {"value": user_ids["catalog"]}

    def override_db():
        with Session(engine) as request_db:
            yield request_db

    def override_staff_context():
        return SimpleNamespace(
            user=SimpleNamespace(id=selected_user_id["value"]),
            session=SimpleNamespace(),
        )

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[admin.current_staff_context] = override_staff_context
    monkeypatch.setattr(admin, "_require_mutation", lambda _request, _context: None)

    with TestClient(app) as client:
        yield client, selected_user_id, user_ids, organization_ids, engine

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(admin.current_staff_context, None)
    db.close()
    engine.dispose()


def test_catalog_to_fleet_dispatch_fare_and_trip_publication_chain(operations_client):
    client, selected, users, organizations, engine = operations_client
    operator_id = organizations["a"]
    other_operator_id = organizations["b"]

    # Catalog: publish locations, an origin terminal, and a route with ordered stops.
    selected["value"] = users["catalog"]
    locations = []
    for name in ("Origin", "Intermediate", "Destination"):
        response = client.post(
            "/api/v1/catalog/locations",
            json={"name": name, "location_type": "town"},
        )
        assert response.status_code == 201, response.text
        locations.append(response.json()["id"])
        published = client.post(f"/api/v1/catalog/locations/{locations[-1]}/publish")
        assert published.status_code == 200, published.text

    terminal = client.post(
        "/api/v1/catalog/terminals",
        json={"location_id": locations[0], "name": "Origin Terminal"},
    )
    assert terminal.status_code == 201, terminal.text
    terminal_id = terminal.json()["id"]
    assert client.post(f"/api/v1/catalog/terminals/{terminal_id}/publish").status_code == 200

    route_response = client.post(
        "/api/v1/catalog/routes",
        json={
            "code": f"INT-{uuid4().hex[:8].upper()}",
            "origin_location_id": locations[0],
            "destination_location_id": locations[2],
        },
    )
    assert route_response.status_code == 201, route_response.text
    route_id = route_response.json()["id"]
    stops_response = client.put(
        f"/api/v1/catalog/routes/{route_id}/stops",
        json={"stops": [
            {"location_id": locations[0], "boarding_allowed": True, "alighting_allowed": False},
            {"location_id": locations[1], "boarding_allowed": True, "alighting_allowed": True},
            {"location_id": locations[2], "boarding_allowed": False, "alighting_allowed": True},
        ]},
    )
    assert stops_response.status_code == 200, stops_response.text
    route_publish = client.post(f"/api/v1/catalog/routes/{route_id}/publish")
    assert route_publish.status_code == 200, route_publish.text
    with Session(engine) as db:
        ordered = list(db.scalars(
            select(RouteStop).where(RouteStop.route_id == UUID(route_id)).order_by(RouteStop.sequence_number)
        ))
        assert [str(item.location_id) for item in ordered] == locations
        assert all(item.status == "published" for item in ordered)

    # Tenant isolation: operator A cannot inspect or mutate operator B's workspace.
    selected["value"] = users["operator"]
    assert client.get(f"/api/v1/operators/{other_operator_id}/trips").status_code == 403
    assert client.get(f"/api/v1/operators/{other_operator_id}/dispatch/options").status_code == 403
    assert client.post(
        f"/api/v1/operators/{other_operator_id}/vehicles",
        json={"vehicle_reference": "CROSS-TENANT-001"},
    ).status_code == 403

    # Fleet: register and approve a vehicle, then create and approve its seat layout.
    vehicle_response = client.post(
        f"/api/v1/operators/{operator_id}/vehicles",
        json={"vehicle_reference": "INT-BUS-001"},
    )
    assert vehicle_response.status_code == 201, vehicle_response.text
    vehicle_id = vehicle_response.json()["id"]

    selected["value"] = users["fleet_reviewer"]
    vehicle_review = client.post(
        f"/api/v1/vehicles/{vehicle_id}/review",
        json={"decision": "approved", "reason": "Synthetic integration approval"},
    )
    assert vehicle_review.status_code == 200, vehicle_review.text

    selected["value"] = users["operator"]
    layout_response = client.post(
        f"/api/v1/vehicles/{vehicle_id}/seat-layouts",
        json={"seats": [
            {"seat_code": "A1", "row_label": "A", "column_index": 0, "seat_type": "standard"},
            {"seat_code": "A2", "row_label": "A", "column_index": 1, "seat_type": "accessible"},
        ]},
    )
    assert layout_response.status_code == 201, layout_response.text
    layout_id = layout_response.json()["id"]

    selected["value"] = users["fleet_reviewer"]
    layout_approval = client.post(f"/api/v1/seat-layouts/{layout_id}/approve")
    assert layout_approval.status_code == 200, layout_approval.text

    # Dispatch: create, submit and approve a trip from the published catalog and approved fleet.
    selected["value"] = users["operator"]
    departure = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    trip_response = client.post(
        f"/api/v1/operators/{operator_id}/trips",
        json={
            "route_id": route_id,
            "boarding_terminal_id": terminal_id,
            "vehicle_id": vehicle_id,
            "seat_layout_version_id": layout_id,
            "departure_at": departure,
        },
    )
    assert trip_response.status_code == 201, trip_response.text
    trip_id = trip_response.json()["id"]
    assert trip_response.json()["seat_count"] == 2
    submitted = client.post(f"/api/v1/trips/{trip_id}/submit")
    assert submitted.status_code == 200, submitted.text

    selected["value"] = users["trip_manager"]
    approved = client.post(f"/api/v1/trips/{trip_id}/approve")
    assert approved.status_code == 200, approved.text

    # Publication must fail closed until an effective published ETB fare exists.
    blocked_publish = client.post(f"/api/v1/trips/{trip_id}/publish")
    assert blocked_publish.status_code == 409
    assert "ETB fare" in blocked_publish.json()["detail"]

    # Fare: proposer, reviewer and publisher are distinct actors and permissions.
    selected["value"] = users["operator"]
    fare_response = client.post(
        f"/api/v1/operators/{operator_id}/fares",
        json={
            "route_id": route_id,
            "amount_minor_units": 12500,
            "effective_from": (datetime.now(UTC) - timedelta(minutes=5)).isoformat(),
        },
    )
    assert fare_response.status_code == 201, fare_response.text
    fare_id = fare_response.json()["fare_id"]
    version_id = fare_response.json()["id"]
    submitted_fare = client.post(
        f"/api/v1/fares/{fare_id}/versions/{version_id}/submit",
    )
    assert submitted_fare.status_code == 200, submitted_fare.text

    # Proposer cannot review; reviewer cannot publish; publisher cannot approve.
    assert client.post(
        f"/api/v1/fares/{fare_id}/versions/{version_id}/review",
        json={"decision": "approved", "reason": "Must be separately reviewed"},
    ).status_code == 403

    selected["value"] = users["fare_reviewer"]
    reviewed = client.post(
        f"/api/v1/fares/{fare_id}/versions/{version_id}/review",
        json={"decision": "approved", "reason": "Synthetic fare approval"},
    )
    assert reviewed.status_code == 200, reviewed.text
    assert client.post(
        f"/api/v1/fares/{fare_id}/versions/{version_id}/publish",
    ).status_code == 403

    selected["value"] = users["fare_publisher"]
    assert client.post(
        f"/api/v1/fares/{fare_id}/versions/{version_id}/review",
        json={"decision": "approved", "reason": "Publisher cannot approve"},
    ).status_code == 403
    published_fare = client.post(
        f"/api/v1/fares/{fare_id}/versions/{version_id}/publish",
    )
    assert published_fare.status_code == 200, published_fare.text
    assert published_fare.json()["status"] == "published"

    # Only the trip-publishing role may publish after the effective ETB fare exists.
    selected["value"] = users["trip_manager"]
    published_trip = client.post(f"/api/v1/trips/{trip_id}/publish")
    assert published_trip.status_code == 200, published_trip.text
    assert published_trip.json()["status"] == "published"

    # Verify durable state and audit evidence across every module boundary.
    with Session(engine) as db:
        assert db.get(Route, UUID(route_id)).status == "published"
        assert db.get(Vehicle, UUID(vehicle_id)).review_status == "approved"
        assert db.get(SeatLayoutVersion, UUID(layout_id)).status == "approved"
        assert db.get(Trip, UUID(trip_id)).status == "published"
        assert db.scalar(select(FareVersion).where(
            FareVersion.id == UUID(version_id),
        )).status == "published"
        assert db.scalar(select(Fare).where(Fare.id == UUID(fare_id))).status == "published"
        event_types = set(db.scalars(select(AuditEvent.event_type)))
        assert {
            "catalog.route.published", "fleet.vehicle.reviewed",
            "fleet.seat_layout.approved", "trip.created", "trip.submitted",
            "trip.approved", "fare.version.proposed", "fare.version.submitted",
            "fare.version.reviewed", "fare.version.published", "trip.published",
        }.issubset(event_types)
