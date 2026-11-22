import os
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.domains.audit.models import AuditEvent
from app.domains.catalog.models import Location, Route, RouteStop, Terminal
from app.domains.fares.models import Fare, FareApproval, FareVersion
from app.domains.fleet.models import SeatLayoutVersion, Vehicle, VehicleComplianceDocument, VehicleSeat
from app.domains.identity.models import Permission, Role, RoleAssignment, RolePermission, User
from app.domains.organizations.models import Organization
from app.domains.trips.models import Schedule, Trip, TripOperationalException, TripSeat
from app.main import app
from app.routers import admin


@pytest.fixture(params=(
    ["sqlite", "postgresql"]
    if os.getenv("DATABASE_URL", "").startswith(("postgresql://", "postgresql+"))
    else ["sqlite"]
))
def operations_client(request, monkeypatch):
    if request.param == "postgresql":
        engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    else:
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
        )
    tables = [
        User.__table__, Role.__table__, Permission.__table__, RolePermission.__table__,
        RoleAssignment.__table__, Organization.__table__, Location.__table__,
        Terminal.__table__, Route.__table__, RouteStop.__table__, Vehicle.__table__,
        SeatLayoutVersion.__table__, VehicleSeat.__table__, VehicleComplianceDocument.__table__, Schedule.__table__, Trip.__table__, TripOperationalException.__table__,
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
    Base.metadata.drop_all(engine, tables=tables)
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
    evidence = client.post(
        f"/api/v1/vehicles/{vehicle_id}/compliance-documents",
        json={
            "document_type": "insurance",
            "evidence_reference": f"fleet-compliance/operator-a/{uuid4().hex}",
            "issued_at": datetime.now(UTC).isoformat(),
            "expires_at": (datetime.now(UTC) + timedelta(days=365)).isoformat(),
        },
    )
    assert evidence.status_code == 201, evidence.text
    evidence_id = evidence.json()["id"]
    selected["value"] = users["fleet_reviewer"]
    evidence_review = client.post(
        f"/api/v1/compliance-documents/{evidence_id}/review",
        json={"decision": "approved", "reason": "Synthetic insurance evidence verified"},
    )
    assert evidence_review.status_code == 200, evidence_review.text
    history = client.get(f"/api/v1/vehicles/{vehicle_id}/history")
    assert history.status_code == 200, history.text
    assert history.json()["documents"][0]["status"] == "approved"
    assert any(item["event_type"] == "fleet.compliance.reviewed" for item in history.json()["events"])

    selected["value"] = users["operator"]
    layout_response = client.post(
        f"/api/v1/vehicles/{vehicle_id}/seat-layouts",
        json={
            "geometry": {"width": 100, "height": 100, "markers": [
                {"kind": "door", "x": 0, "y": 10, "label": "Front door"},
                {"kind": "aisle", "x": 50, "y": 50},
            ]},
            "seats": [
                {"seat_code": "A1", "row_label": "A", "column_index": 0, "x": 10, "y": 20, "seat_type": "standard"},
                {"seat_code": "A2", "row_label": "A", "column_index": 1, "x": 30, "y": 20, "seat_type": "accessible", "is_sellable": False},
            ],
        },
    )
    assert layout_response.status_code == 201, layout_response.text
    layout_id = layout_response.json()["id"]

    selected["value"] = users["fleet_reviewer"]
    layout_approval = client.post(f"/api/v1/seat-layouts/{layout_id}/approve")
    assert layout_approval.status_code == 200, layout_approval.text
    layout_detail = client.get(f"/api/v1/vehicles/{vehicle_id}/seat-layouts")
    assert layout_detail.status_code == 200, layout_detail.text
    assert layout_detail.json()[0]["geometry"]["markers"][0]["kind"] == "door"
    assert layout_detail.json()[0]["seats"][0]["x"] == 10

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
    assert trip_response.json()["seat_count"] == 1
    edited_departure = datetime.now(UTC) + timedelta(days=3)
    edited = client.patch(
        f"/api/v1/trips/{trip_id}",
        json={
            "route_id": route_id, "boarding_terminal_id": terminal_id,
            "vehicle_id": vehicle_id, "seat_layout_version_id": layout_id,
            "departure_at": edited_departure.isoformat(),
            "arrival_estimate_at": (edited_departure + timedelta(hours=5)).isoformat(),
        },
    )
    assert edited.status_code == 200, edited.text
    assert edited.json()["seat_count"] == 1
    exception = client.post(
        f"/api/v1/trips/{trip_id}/exceptions",
        json={"category": "late_departure", "severity": "high", "description": "Synthetic road closure delay"},
    )
    assert exception.status_code == 201, exception.text
    exception_id = exception.json()["id"]
    assert client.get(f"/api/v1/trips/{trip_id}/exceptions").status_code == 200
    submitted = client.post(f"/api/v1/trips/{trip_id}/submit")
    assert submitted.status_code == 200, submitted.text

    selected["value"] = users["trip_manager"]
    approved = client.post(f"/api/v1/trips/{trip_id}/approve")
    assert approved.status_code == 200, approved.text
    resolved_exception = client.post(
        f"/api/v1/trip-exceptions/{exception_id}/resolve",
        json={"resolution": "Synthetic replacement vehicle arranged"},
    )
    assert resolved_exception.status_code == 200, resolved_exception.text
    assert resolved_exception.json()["status"] == "resolved"

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
    selected["value"] = users["fare_reviewer"]
    fare_register = client.get("/api/v1/admin/fares")
    assert fare_register.status_code == 200, fare_register.text
    fare_record = next(item for item in fare_register.json() if item["id"] == fare_id)
    assert fare_record["versions"][0]["approval_history"][0]["reason"] == "Synthetic fare approval"

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
        assert db.scalar(select(func.count(TripSeat.id)).where(TripSeat.trip_id == UUID(trip_id))) == 1
        assert db.get(Trip, UUID(trip_id)).status == "published"
        assert db.scalar(select(FareVersion).where(
            FareVersion.id == UUID(version_id),
        )).status == "published"
        assert db.scalar(select(Fare).where(Fare.id == UUID(fare_id))).status == "published"
        event_types = set(db.scalars(select(AuditEvent.event_type)))
        assert {
            "catalog.route.published", "fleet.vehicle.reviewed", "fleet.compliance.submitted",
            "fleet.compliance.reviewed", "fleet.seat_layout.approved", "trip.created", "trip.exception.reported",
            "trip.exception.resolved", "trip.submitted",
            "trip.draft.updated", "trip.approved", "fare.version.proposed", "fare.version.submitted",
            "fare.version.reviewed", "fare.version.published", "trip.published",
        }.issubset(event_types)

def test_cross_tenant_resource_integrity_and_fare_ownership(operations_client):
    client, selected, users, organizations, engine = operations_client
    operator_a = organizations["a"]
    operator_b = organizations["b"]
    now = datetime.now(UTC)

    # Seed a shared published route, but keep fleet, trip and fare ownership
    # explicitly split between two approved operator organizations.
    with Session(engine) as db:
        origin = Location(name="Ownership Origin", location_type="town", status="published")
        destination = Location(name="Ownership Destination", location_type="town", status="published")
        db.add_all([origin, destination])
        db.flush()
        route = Route(
            code=f"OWN-{uuid4().hex[:8].upper()}",
            origin_location_id=origin.id,
            destination_location_id=destination.id,
            status="published",
        )
        terminal = Terminal(location_id=origin.id, name="Ownership Terminal", status="published")
        db.add_all([route, terminal])
        db.flush()

        vehicle_a = Vehicle(
            organization_id=operator_a, vehicle_reference="OWN-A-001",
            status="active", review_status="approved",
        )
        vehicle_b = Vehicle(
            organization_id=operator_b, vehicle_reference="OWN-B-001",
            status="active", review_status="approved",
        )
        db.add_all([vehicle_a, vehicle_b])
        db.flush()
        layout_a = SeatLayoutVersion(vehicle_id=vehicle_a.id, version_number=1, status="approved")
        layout_b = SeatLayoutVersion(vehicle_id=vehicle_b.id, version_number=1, status="approved")
        db.add_all([layout_a, layout_b])
        db.flush()
        db.add_all([
            VehicleSeat(
                seat_layout_version_id=layout_a.id, seat_code="A1",
                row_label="A", position_metadata={"column_index": 0},
                seat_type="standard", is_sellable=True,
            ),
            VehicleSeat(
                seat_layout_version_id=layout_b.id, seat_code="B1",
                row_label="B", position_metadata={"column_index": 0},
                seat_type="standard", is_sellable=True,
            ),
        ])
        trip_a = Trip(
            organization_id=operator_a, route_id=route.id,
            boarding_terminal_id=terminal.id, vehicle_id=vehicle_a.id,
            seat_layout_version_id=layout_a.id, departure_at=now + timedelta(days=2),
            status="approved",
        )
        trip_b = Trip(
            organization_id=operator_b, route_id=route.id,
            boarding_terminal_id=terminal.id, vehicle_id=vehicle_b.id,
            seat_layout_version_id=layout_b.id, departure_at=now + timedelta(days=2),
            status="approved",
        )
        db.add_all([trip_a, trip_b])
        db.flush()

        fare_a = Fare(organization_id=operator_a, route_id=route.id, trip_id=None, status="draft")
        fare_b = Fare(organization_id=operator_b, route_id=route.id, trip_id=trip_b.id, status="published")
        db.add_all([fare_a, fare_b])
        db.flush()
        version_b = FareVersion(
            fare_id=fare_b.id, version_number=1, amount_minor_units=15000,
            currency_code="ETB", effective_from=now - timedelta(minutes=1),
            effective_to=None, status="published", proposed_by=users["operator"],
            approved_by=users["fare_reviewer"], published_by=users["fare_publisher"],
        )
        db.add(version_b)
        db.commit()

        ids = {
            "route": str(route.id), "terminal": str(terminal.id),
            "vehicle_a": str(vehicle_a.id), "vehicle_b": str(vehicle_b.id),
            "layout_a": str(layout_a.id), "layout_b": str(layout_b.id),
            "trip_a": str(trip_a.id), "trip_b": str(trip_b.id),
            "fare_a": str(fare_a.id), "fare_b": str(fare_b.id),
            "version_b": str(version_b.id),
        }

    # Operator A cannot inspect or mutate Operator B's vehicle or layout by ID.
    selected["value"] = users["operator"]
    assert client.get(f"/api/v1/vehicles/{ids['vehicle_b']}/seat-layouts").status_code == 403
    assert client.patch(
        f"/api/v1/vehicles/{ids['vehicle_b']}",
        json={"vehicle_reference": "CROSS-TENANT-EDIT"},
    ).status_code == 403
    assert client.post(
        f"/api/v1/vehicles/{ids['vehicle_b']}/seat-layouts",
        json={"seats": [{"seat_code": "X1", "row_label": "X", "column_index": 0}]},
    ).status_code == 403
    assert client.put(
        f"/api/v1/seat-layouts/{ids['layout_b']}",
        json={"seats": [{"seat_code": "X1", "row_label": "X", "column_index": 0}]},
    ).status_code == 403
    assert client.get(f"/api/v1/operators/{operator_b}/fares").status_code == 403
    assert client.get(f"/api/v1/operators/{operator_b}/trips").status_code == 403
    assert client.post(
        f"/api/v1/fares/{ids['fare_b']}/versions/{ids['version_b']}/submit",
    ).status_code == 403
    assert client.post(f"/api/v1/trips/{ids['trip_b']}/submit").status_code == 403
    assert client.patch(
        f"/api/v1/trips/{ids['trip_b']}",
        json={
            "route_id": ids["route"], "boarding_terminal_id": ids["terminal"],
            "vehicle_id": ids["vehicle_b"], "seat_layout_version_id": ids["layout_b"],
            "departure_at": (now + timedelta(days=4)).isoformat(),
            "arrival_estimate_at": (now + timedelta(days=4, hours=5)).isoformat(),
        },
    ).status_code == 403

    # A trip cannot combine Operator A with Operator B's vehicle or layout.
    departure = (now + timedelta(days=3)).isoformat()
    cross_vehicle = client.post(
        f"/api/v1/operators/{operator_a}/trips",
        json={
            "route_id": ids["route"], "boarding_terminal_id": ids["terminal"],
            "vehicle_id": ids["vehicle_b"], "seat_layout_version_id": ids["layout_b"],
            "departure_at": departure,
        },
    )
    assert cross_vehicle.status_code == 409
    cross_layout = client.post(
        f"/api/v1/operators/{operator_a}/trips",
        json={
            "route_id": ids["route"], "boarding_terminal_id": ids["terminal"],
            "vehicle_id": ids["vehicle_a"], "seat_layout_version_id": ids["layout_b"],
            "departure_at": departure,
        },
    )
    assert cross_layout.status_code == 409

    # An Operator A fare cannot be attached to Operator B's trip.
    cross_tenant_fare = client.post(
        f"/api/v1/operators/{operator_a}/fares",
        json={
            "route_id": ids["route"], "trip_id": ids["trip_b"],
            "amount_minor_units": 9900, "effective_from": (now - timedelta(minutes=1)).isoformat(),
        },
    )
    assert cross_tenant_fare.status_code == 409

    # URL fare/version pairs must resolve to the same parent fare.
    selected["value"] = users["fare_reviewer"]
    mismatched_review = client.post(
        f"/api/v1/fares/{ids['fare_a']}/versions/{ids['version_b']}/review",
        json={"decision": "approved", "reason": "Cross-owner mismatch must fail"},
    )
    assert mismatched_review.status_code == 404
    selected["value"] = users["fare_publisher"]
    mismatched_publish = client.post(
        f"/api/v1/fares/{ids['fare_a']}/versions/{ids['version_b']}/publish",
    )
    assert mismatched_publish.status_code == 404

    # A published fare belonging to Operator B must never satisfy Operator A's
    # trip-publication prerequisite, even when route and effective window match.
    selected["value"] = users["trip_manager"]
    wrong_tenant_fare = client.post(f"/api/v1/trips/{ids['trip_a']}/publish")
    assert wrong_tenant_fare.status_code == 409
    assert "ETB fare" in wrong_tenant_fare.json()["detail"]

