"""Seed deterministic synthetic catalog and passenger-search fixtures.

Run from backend/ after applying migrations:
    python -m scripts.seed_synthetic_routes

All records are synthetic and restricted to APP_ENV=test. No real operators,
vehicles, passengers, payments, bookings or GPS traces are created.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from uuid import NAMESPACE_URL, UUID, uuid5
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.core.config import settings
from app.db import model_registry  # noqa: F401
from app.db.session import SessionLocal
from app.domains.catalog.models import Location, Route, RouteStop, Terminal
from app.domains.fares.models import Fare, FareVersion
from app.domains.fleet.models import SeatLayoutVersion, Vehicle, VehicleSeat
from app.domains.identity.models import User
from app.domains.organizations.models import Organization
from app.domains.trips.models import Trip, TripSeat

LOCATION_IDS = {
    "koybe": UUID("10000000-0000-4000-8000-000000000001"),
    "jinka": UUID("10000000-0000-4000-8000-000000000002"),
    "wolaita_sodo": UUID("10000000-0000-4000-8000-000000000003"),
    "addis_ababa": UUID("10000000-0000-4000-8000-000000000004"),
}
LOCATION_DATA = {
    "koybe": ("Koybe", "town"),
    "jinka": ("Jinka", "town"),
    "wolaita_sodo": ("Wolaita Sodo", "city"),
    "addis_ababa": ("Addis Ababa", "city"),
}
ROUTE_DATA = {
    "SYNTH-KOYBE-JINKA": ("koybe", "jinka", ["koybe", "jinka"], 10000, 2),
    "SYNTH-JINKA-WOLaita": ("jinka", "wolaita_sodo", ["jinka", "wolaita_sodo"], 35000, 5),
    "SYNTH-WOLaita-ADDIS": ("wolaita_sodo", "addis_ababa", ["wolaita_sodo", "addis_ababa"], 60000, 6),
    "SYNTH-JINKA-ADDIS": ("jinka", "addis_ababa", ["jinka", "wolaita_sodo", "addis_ababa"], 95000, 11),
    "SYNTH-ADDIS-WOLaita": ("addis_ababa", "wolaita_sodo", ["addis_ababa", "wolaita_sodo"], 60000, 6),
    "SYNTH-WOLaita-JINKA": ("wolaita_sodo", "jinka", ["wolaita_sodo", "jinka"], 35000, 5),
    "SYNTH-JINKA-KOYBE": ("jinka", "koybe", ["jinka", "koybe"], 10000, 2),
}
TEST_ORGANIZATION_ID = UUID("50000000-0000-4000-8000-000000000001")
TEST_USER_ID = UUID("50000000-0000-4000-8000-000000000002")
TEST_VEHICLE_ID = UUID("50000000-0000-4000-8000-000000000003")
TEST_LAYOUT_ID = UUID("50000000-0000-4000-8000-000000000004")
SEAT_COUNT = 12
SERVICE_DAYS = 7
EAT = ZoneInfo("Africa/Addis_Ababa")


def stable_id(value: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"maalenex-moto-synthetic:{value}")


def seed() -> None:
    if settings.app_env != "test" or not settings.synthetic_data_only:
        raise RuntimeError("Seeding requires APP_ENV=test and synthetic data mode.")

    now = datetime.now(timezone.utc)
    with SessionLocal.begin() as session:
        for key, (name, location_type) in LOCATION_DATA.items():
            location = session.get(Location, LOCATION_IDS[key])
            if location is None:
                session.add(Location(
                    id=LOCATION_IDS[key], name=name,
                    location_type=location_type, status="published",
                ))
            elif (location.name, location.location_type) != (name, location_type):
                raise RuntimeError(f"Synthetic location ID collision for {key}; refusing overwrite.")
            else:
                location.status = "published"

        session.flush()
        terminal_ids: dict[str, UUID] = {}
        for index, key in enumerate(LOCATION_DATA, start=1):
            terminal_id = UUID(f"20000000-0000-4000-8000-{index:012d}")
            terminal_ids[key] = terminal_id
            terminal_name = f"{LOCATION_DATA[key][0]} Synthetic Test Terminal"
            terminal = session.get(Terminal, terminal_id)
            if terminal is None:
                session.add(Terminal(
                    id=terminal_id, location_id=LOCATION_IDS[key],
                    name=terminal_name, status="published",
                ))
            elif terminal.location_id != LOCATION_IDS[key] or terminal.name != terminal_name:
                raise RuntimeError(f"Synthetic terminal ID collision for {key}; refusing overwrite.")
            else:
                terminal.status = "published"

        organization = session.get(Organization, TEST_ORGANIZATION_ID)
        if organization is None:
            organization = Organization(
                id=TEST_ORGANIZATION_ID,
                organization_type="operator",
                display_name="MaaleNex Synthetic Test Operator",
                status="approved",
            )
            session.add(organization)
        elif organization.display_name != "MaaleNex Synthetic Test Operator":
            raise RuntimeError("Synthetic organization ID collision; refusing overwrite.")
        else:
            organization.status = "approved"

        test_user = session.get(User, TEST_USER_ID)
        if test_user is None:
            test_user = User(
                id=TEST_USER_ID,
                login_identifier="synthetic-fixture@maalenex.invalid",
                display_name="Synthetic Test Fixture",
                status="active",
            )
            session.add(test_user)
        elif test_user.login_identifier != "synthetic-fixture@maalenex.invalid":
            raise RuntimeError("Synthetic staff-user ID collision; refusing overwrite.")
        else:
            test_user.status = "active"

        # Flush the organization/user parents before their FK-dependent vehicle.
        session.flush()
        vehicle = session.get(Vehicle, TEST_VEHICLE_ID)
        if vehicle is None:
            vehicle = Vehicle(
                id=TEST_VEHICLE_ID,
                organization_id=TEST_ORGANIZATION_ID,
                vehicle_reference="SYNTHETIC-COACH-001",
                status="published",
                review_status="approved",
            )
            session.add(vehicle)
        elif vehicle.organization_id != TEST_ORGANIZATION_ID:
            raise RuntimeError("Synthetic vehicle ID collision; refusing overwrite.")
        else:
            vehicle.status = "published"
            vehicle.review_status = "approved"

        # Flush parent rows before inserting the seat-layout FK dependent.
        session.flush()
        layout = session.get(SeatLayoutVersion, TEST_LAYOUT_ID)
        if layout is None:
            layout = SeatLayoutVersion(
                id=TEST_LAYOUT_ID, vehicle_id=TEST_VEHICLE_ID,
                version_number=1, status="published", effective_from=now - timedelta(days=1),
            )
            session.add(layout)
        elif layout.vehicle_id != TEST_VEHICLE_ID:
            raise RuntimeError("Synthetic seat-layout ID collision; refusing overwrite.")
        else:
            layout.status = "published"

        session.flush()
        seat_ids: list[UUID] = []
        for seat_number in range(1, SEAT_COUNT + 1):
            seat_code = f"{seat_number:02d}"
            seat_id = stable_id(f"vehicle-seat:{seat_code}")
            seat_ids.append(seat_id)
            seat = session.get(VehicleSeat, seat_id)
            if seat is None:
                session.add(VehicleSeat(
                    id=seat_id, seat_layout_version_id=TEST_LAYOUT_ID,
                    seat_code=seat_code, row_label=str((seat_number - 1) // 4 + 1),
                    position_metadata={"synthetic": True}, seat_type="standard",
                    is_sellable=True,
                ))
            elif seat.seat_layout_version_id != TEST_LAYOUT_ID or seat.seat_code != seat_code:
                raise RuntimeError(f"Synthetic vehicle-seat collision for {seat_code}; refusing overwrite.")

        session.flush()
        seeded_routes: dict[str, Route] = {}
        for index, (code, route_data) in enumerate(ROUTE_DATA.items(), start=1):
            origin_key, destination_key, stop_keys, fare_minor, duration_hours = route_data
            route_id = UUID(f"30000000-0000-4000-8000-{index:012d}")
            route = session.scalar(select(Route).where(Route.code == code))
            if route is None:
                route = Route(
                    id=route_id, code=code,
                    origin_location_id=LOCATION_IDS[origin_key],
                    destination_location_id=LOCATION_IDS[destination_key],
                    status="published",
                )
                session.add(route)
                session.flush()
            elif (
                route.id != route_id
                or route.origin_location_id != LOCATION_IDS[origin_key]
                or route.destination_location_id != LOCATION_IDS[destination_key]
            ):
                raise RuntimeError(f"Synthetic route code collision for {code}; refusing overwrite.")
            else:
                route.status = "published"
            seeded_routes[code] = route

            existing_stops = session.scalars(
                select(RouteStop).where(RouteStop.route_id == route.id)
                .order_by(RouteStop.sequence_number)
            ).all()
            expected_stops = [
                (LOCATION_IDS[key], sequence)
                for sequence, key in enumerate(stop_keys, start=1)
            ]
            actual_stops = [(stop.location_id, stop.sequence_number) for stop in existing_stops]
            if not existing_stops:
                for sequence, key in enumerate(stop_keys, start=1):
                    stop_number = index * 10 + sequence
                    session.add(RouteStop(
                        id=UUID(f"40000000-0000-4000-8000-{stop_number:012d}"),
                        route_id=route.id, location_id=LOCATION_IDS[key],
                        sequence_number=sequence, boarding_allowed=True,
                        alighting_allowed=True, status="published",
                    ))
            elif actual_stops != expected_stops:
                raise RuntimeError(f"Synthetic route-stop mismatch for {code}; refusing rewrite.")
            else:
                for stop in existing_stops:
                    stop.status = "published"

            fare = session.scalar(select(Fare).where(
                Fare.organization_id == TEST_ORGANIZATION_ID,
                Fare.route_id == route.id,
                Fare.trip_id.is_(None),
            ))
            if fare is None:
                fare = Fare(
                    id=stable_id(f"fare:{code}"),
                    organization_id=TEST_ORGANIZATION_ID,
                    route_id=route.id,
                    trip_id=None,
                    status="published",
                )
                session.add(fare)
                session.flush()
            fare_version = session.scalar(select(FareVersion).where(
                FareVersion.fare_id == fare.id, FareVersion.version_number == 1,
            ))
            if fare_version is None:
                fare_version = FareVersion(
                    id=stable_id(f"fare-version:{code}:1"),
                    fare_id=fare.id, version_number=1,
                    amount_minor_units=fare_minor, currency_code="ETB",
                    effective_from=now - timedelta(days=1), effective_to=None,
                    status="published", proposed_by=TEST_USER_ID,
                    approved_by=TEST_USER_ID, published_by=TEST_USER_ID,
                    approved_at=now - timedelta(days=1), published_at=now - timedelta(days=1),
                )
                session.add(fare_version)
            elif fare_version.amount_minor_units != fare_minor or fare_version.currency_code != "ETB":
                raise RuntimeError(f"Synthetic fare mismatch for {code}; refusing overwrite.")
            else:
                fare_version.status = "published"

            for day_offset in range(1, SERVICE_DAYS + 1):
                service_date = datetime.now(EAT).date() + timedelta(days=day_offset)
                departure = datetime.combine(
                    service_date, time(hour=8), tzinfo=EAT,
                ).astimezone(timezone.utc)
                trip_id = stable_id(f"trip:{code}:{service_date.isoformat()}")
                trip = session.get(Trip, trip_id)
                if trip is None:
                    trip = Trip(
                        id=trip_id, organization_id=TEST_ORGANIZATION_ID,
                        route_id=route.id, boarding_terminal_id=terminal_ids[origin_key],
                        schedule_id=None, vehicle_id=TEST_VEHICLE_ID,
                        seat_layout_version_id=TEST_LAYOUT_ID,
                        departure_at=departure,
                        arrival_estimate_at=departure + timedelta(hours=duration_hours),
                        status="published", published_at=now,
                    )
                    session.add(trip)
                    session.flush()
                elif trip.route_id != route.id or trip.vehicle_id != TEST_VEHICLE_ID:
                    raise RuntimeError(f"Synthetic trip ID collision for {code}; refusing overwrite.")
                else:
                    trip.status = "published"

                for seat_number, vehicle_seat_id in enumerate(seat_ids, start=1):
                    trip_seat_id = stable_id(
                        f"trip-seat:{code}:{service_date.isoformat()}:{seat_number}"
                    )
                    trip_seat = session.get(TripSeat, trip_seat_id)
                    if trip_seat is None:
                        session.add(TripSeat(
                            id=trip_seat_id, trip_id=trip.id,
                            vehicle_seat_id=vehicle_seat_id,
                            seat_code_snapshot=f"{seat_number:02d}",
                            sellable_status="sellable",
                        ))
                    elif trip_seat.trip_id != trip.id or trip_seat.vehicle_seat_id != vehicle_seat_id:
                        raise RuntimeError("Synthetic trip-seat ID collision; refusing overwrite.")

    print(
        f"Seeded {len(LOCATION_DATA)} locations, {len(LOCATION_DATA)} terminals, "
        f"{len(ROUTE_DATA)} routes and {len(ROUTE_DATA) * SERVICE_DAYS} synthetic trips "
        f"with {SEAT_COUNT} seats each. Synthetic ETB fares only."
    )


if __name__ == "__main__":
    seed()
