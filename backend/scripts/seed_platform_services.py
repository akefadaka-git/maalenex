"""Seed the synthetic MaaleNex service registry and pilot-area policies.

Run from backend/ after applying migrations:
    python -m scripts.seed_platform_services

This fixture is restricted to APP_ENV=test and synthetic-data-only mode.
It does not activate any live service or create real provider/customer data.
"""
from app.core.config import settings
from app.db.session import SessionLocal
from app.domains.platform.models import PlatformService, ServiceArea, ServiceAreaAvailability

SERVICES = [
    ("move", "MaaleNex Move", "Local passenger rides and dispatch", "planned", False, 1),
    ("transit", "MaaleNex Transit", "Intercity routes, schedules and reservations", "synthetic_test", True, 2),
    ("delivery", "MaaleNex Delivery", "Local parcels and last-mile delivery", "planned", False, 3),
    ("cargo", "MaaleNex Cargo", "Freight requests, carrier capacity and delivery", "planned", False, 4),
    ("market", "MaaleNex Market", "Merchant discovery, catalog and orders", "planned", False, 5),
    ("fleet", "MaaleNex Fleet", "Vehicles, drivers and fleet compliance", "planned", False, 6),
    ("business", "MaaleNex Business", "SME and enterprise service accounts", "planned", False, 7),
    ("pay", "MaaleNex Pay", "Payment adapters and ETB financial ledger", "planned", False, 8),
]
AREAS = [
    ("ET-SO-KOYBE", "Koybe", "South Omo", "town"),
    ("ET-SO-JINKA", "Jinka", "South Omo", "town"),
    ("ET-WOL-WOL-SODO", "Wolaita Sodo", "Wolaita", "city"),
    ("ET-AA-ADDIS", "Addis Ababa", "Addis Ababa", "city"),
]


def seed() -> None:
    if settings.app_env != "test" or not settings.synthetic_data_only:
        raise RuntimeError("Platform service seeding requires APP_ENV=test and synthetic data mode.")

    with SessionLocal.begin() as session:
        for code, name, description, status, enabled, order in SERVICES:
            row = session.get(PlatformService, code)
            if row is None:
                row = PlatformService(
                    code=code, name=name, description=description,
                    rollout_status=status, is_enabled=enabled, sort_order=order,
                )
                session.add(row)
            elif row.name != name:
                raise RuntimeError(f"Platform service code collision for {code}; refusing overwrite.")
            else:
                row.description = description
                row.rollout_status = status
                row.is_enabled = enabled
                row.sort_order = order

        for code, name, administrative_area, area_type in AREAS:
            row = session.get(ServiceArea, code)
            if row is None:
                session.add(ServiceArea(
                    code=code, name=name, country_code="ET",
                    administrative_area=administrative_area, area_type=area_type,
                ))
            elif row.name != name:
                raise RuntimeError(f"Service-area code collision for {code}; refusing overwrite.")

        session.flush()
        for service_code, *_ in SERVICES:
            for area_code, *_ in AREAS:
                row = session.query(ServiceAreaAvailability).filter_by(
                    service_code=service_code, area_code=area_code
                ).one_or_none()
                status = "synthetic_test" if service_code in {"transit", "move"} else "planned"
                enabled = service_code in {"transit", "move"}
                if row is None:
                    session.add(ServiceAreaAvailability(
                        service_code=service_code, area_code=area_code,
                        availability_status=status, is_enabled=enabled,
                    ))
                else:
                    row.availability_status = status
                    row.is_enabled = enabled


def main() -> None:
    seed()
    print("PASS: seeded 8 synthetic MaaleNex services across 4 areas; no live service activated.")


if __name__ == "__main__":
    main()
