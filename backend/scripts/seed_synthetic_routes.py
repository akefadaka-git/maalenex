"""Seed a deterministic, synthetic-only location and route catalog.

Run from backend/ after applying migrations:
    python -m scripts.seed_synthetic_routes

Creates locations, terminals, routes and route stops only. It does not create
operators, vehicles, trips, fares, passengers, bookings or payments.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.core.config import settings
from app.db import model_registry  # noqa: F401
from app.db.session import SessionLocal
from app.domains.catalog.models import Location, Route, RouteStop, Terminal

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
    "SYNTH-KOYBE-JINKA": ("koybe", "jinka", ["koybe", "jinka"]),
    "SYNTH-JINKA-WOLaita": ("jinka", "wolaita_sodo", ["jinka", "wolaita_sodo"]),
    "SYNTH-WOLaita-ADDIS": ("wolaita_sodo", "addis_ababa", ["wolaita_sodo", "addis_ababa"]),
    "SYNTH-JINKA-ADDIS": ("jinka", "addis_ababa", ["jinka", "wolaita_sodo", "addis_ababa"]),
    "SYNTH-ADDIS-WOLaita": ("addis_ababa", "wolaita_sodo", ["addis_ababa", "wolaita_sodo"]),
    "SYNTH-WOLaita-JINKA": ("wolaita_sodo", "jinka", ["wolaita_sodo", "jinka"]),
    "SYNTH-JINKA-KOYBE": ("jinka", "koybe", ["jinka", "koybe"]),
}


def seed() -> None:
    if settings.app_env != "test" or not settings.synthetic_data_only:
        raise RuntimeError("Seeding requires APP_ENV=test and synthetic data mode.")

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
        for index, key in enumerate(LOCATION_DATA, start=1):
            terminal_id = UUID(f"20000000-0000-4000-8000-{index:012d}")
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

        session.flush()
        for index, (code, (origin_key, destination_key, stop_keys)) in enumerate(
            ROUTE_DATA.items(), start=1
        ):
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

            existing = session.scalars(
                select(RouteStop)
                .where(RouteStop.route_id == route.id)
                .order_by(RouteStop.sequence_number)
            ).all()
            expected = [
                (LOCATION_IDS[key], sequence)
                for sequence, key in enumerate(stop_keys, start=1)
            ]
            actual = [(stop.location_id, stop.sequence_number) for stop in existing]
            if not existing:
                for sequence, key in enumerate(stop_keys, start=1):
                    stop_number = index * 10 + sequence
                    session.add(RouteStop(
                        id=UUID(f"40000000-0000-4000-8000-{stop_number:012d}"),
                        route_id=route.id, location_id=LOCATION_IDS[key],
                        sequence_number=sequence, boarding_allowed=True,
                        alighting_allowed=True, status="published",
                    ))
            elif actual != expected:
                raise RuntimeError(f"Synthetic route-stop mismatch for {code}; refusing rewrite.")
            else:
                for stop in existing:
                    stop.status = "published"

    print(
        f"Seeded {len(LOCATION_DATA)} synthetic locations, "
        f"{len(LOCATION_DATA)} terminals, and {len(ROUTE_DATA)} routes."
    )


if __name__ == "__main__":
    seed()
