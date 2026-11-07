from datetime import date, datetime, time, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.db.session import get_db
from app.domains.bookings.models import Booking, SeatAllocation, SeatHold
from app.domains.catalog.models import Location, Route
from app.domains.fares.models import Fare, FareVersion
from app.domains.trips.models import Trip, TripSeat

router = APIRouter(tags=["passenger-catalog"])


@router.get("/catalog/locations")
def list_public_locations(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(Location).where(Location.status == "published").order_by(Location.name))
    return [{"id": str(row.id), "name": row.name, "type": row.location_type} for row in rows]


@router.get("/catalog/routes")
def list_public_routes(db: Session = Depends(get_db)) -> list[dict]:
    origin = aliased(Location)
    destination = aliased(Location)
    rows = db.execute(
        select(Route, origin, destination)
        .join(origin, Route.origin_location_id == origin.id)
        .join(destination, Route.destination_location_id == destination.id)
        .where(Route.status == "published")
        .order_by(Route.code)
    ).all()
    return [
        {"id": str(route.id), "code": route.code,
         "origin": {"id": str(origin.id), "name": origin.name},
         "destination": {"id": str(destination.id), "name": destination.name}}
        for route, origin, destination in rows
    ]


@router.get("/trips/search")
def search_published_trips(
    origin_id: UUID, destination_id: UUID, travel_date: date,
    passenger_count: int = Query(default=1, ge=1, le=10),
    db: Session = Depends(get_db),
) -> list[dict]:
    local_start = datetime.combine(travel_date, time.min, ZoneInfo("Africa/Addis_Ababa"))
    local_end = datetime.combine(travel_date, time.max, ZoneInfo("Africa/Addis_Ababa"))
    start_utc = local_start.astimezone(timezone.utc)
    end_utc = local_end.astimezone(timezone.utc)
    now = db.scalar(select(func.now()))
    trips = db.scalars(
        select(Trip).join(Route, Route.id == Trip.route_id).where(
            Trip.status == "published",
            Route.status == "published",
            Route.origin_location_id == origin_id,
            Route.destination_location_id == destination_id,
            Trip.departure_at >= start_utc,
            Trip.departure_at <= end_utc,
        ).order_by(Trip.departure_at)
    ).all()
    results = []
    for trip in trips:
        fare = db.scalar(
            select(FareVersion).join(Fare, Fare.id == FareVersion.fare_id).where(
                Fare.organization_id == trip.organization_id,
                Fare.route_id == trip.route_id,
                or_(Fare.trip_id == trip.id, Fare.trip_id.is_(None)),
                FareVersion.status == "published",
                FareVersion.currency_code == "ETB",
                FareVersion.effective_from <= now,
                or_(FareVersion.effective_to.is_(None), FareVersion.effective_to > now),
            ).order_by(Fare.trip_id.is_not(None).desc(), FareVersion.effective_from.desc())
        )
        if fare is None:
            continue
        total_seats = db.scalar(select(func.count(TripSeat.id)).where(
            TripSeat.trip_id == trip.id, TripSeat.sellable_status == "sellable"
        )) or 0
        occupied = db.scalar(
            select(func.count(SeatAllocation.id))
            .join(Booking, Booking.id == SeatAllocation.booking_id)
            .where(
                SeatAllocation.trip_id == trip.id,
                SeatAllocation.status == "active",
                or_(
                    Booking.status == "reserved",
                    and_(
                        Booking.status == "held",
                        exists(select(1).where(
                            SeatHold.booking_id == SeatAllocation.booking_id,
                            SeatHold.trip_seat_id == SeatAllocation.trip_seat_id,
                            SeatHold.status == "active",
                            SeatHold.expires_at > now,
                        )),
                    ),
                ),
            )
        ) or 0
        available = max(0, total_seats - occupied)
        if available < passenger_count:
            continue
        results.append({
            "id": str(trip.id),
            "departure_at": trip.departure_at.isoformat(),
            "arrival_estimate_at": trip.arrival_estimate_at.isoformat() if trip.arrival_estimate_at else None,
            "boarding_model": "Jinka Bus Terminal",
            "available_seats": available,
            "availability_as_of": now.isoformat(),
            "fare": {"amount_minor_units": fare.amount_minor_units, "currency_code": "ETB"},
            "reservation_only": True,
            "ticketing_enabled": False,
            "payment_enabled": False,
        })
    return results
