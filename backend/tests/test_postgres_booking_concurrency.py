from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domains.bookings.service import BookingConflict, create_seat_hold
from app.domains.catalog.models import Location, Route, Terminal
from app.domains.fares.models import Fare, FareVersion
from app.domains.fleet.models import SeatLayoutVersion, Vehicle, VehicleSeat
from app.domains.identity.models import User
from app.domains.organizations.models import Organization
from app.domains.trips.models import Trip, TripSeat


pytestmark = pytest.mark.skipif(
    __import__("os").environ.get("RUN_POSTGRES_INTEGRATION") != "1",
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
                    db, trip_id=__import__("uuid").UUID(trip_id),
                    contact_name=f"Synthetic Passenger {index}",
                    contact_phone=f"+25190000000{index}",
                    passengers=[{"name": f"Passenger {index}"}],
                    seat_ids=[__import__("uuid").UUID(seat_id)],
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
