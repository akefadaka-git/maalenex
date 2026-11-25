"""Authenticated, tenant-scoped internal vehicle-position API."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.geo.security import (
    GeoAuthorizationError,
    authorize_geo_tenant_context,
)
from app.domains.identity.service import StaffContext
from app.routers.auth import current_staff_context

router = APIRouter(prefix="/geo/internal", tags=["internal-geography"])


@router.get("/vehicles/positions")
def read_internal_vehicle_positions(
    response: Response,
    organization_id: Annotated[UUID, Query(description="Organization whose positions the caller is authorized to read")],
    context: Annotated[StaffContext, Depends(current_staff_context)],
    db: Annotated[Session, Depends(get_db)],
    vehicle_id: Annotated[UUID | None, Query(description="Optional vehicle filter within the selected organization")] = None,
    max_age_minutes: Annotated[int, Query(ge=1, le=1440)] = 30,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
) -> dict:
    """Return only the latest recent position per vehicle in one authorized tenant."""
    try:
        authorize_geo_tenant_context(
            db,
            user_id=context.user.id,
            organization_id=organization_id,
            permission_code="platform.tracking.read",
        )
        rows = db.execute(text("""
            SELECT vehicle_id, longitude, latitude, recorded_at, received_at,
                   speed_kph, heading_degrees, accuracy_meters, is_synthetic
            FROM (
                SELECT DISTINCT ON (vp.vehicle_id)
                       vp.vehicle_id,
                       ST_X(vp.geom)::double precision AS longitude,
                       ST_Y(vp.geom)::double precision AS latitude,
                       vp.recorded_at,
                       vp.received_at,
                       vp.speed_kph,
                       vp.heading_degrees,
                       vp.accuracy_meters,
                       vp.is_synthetic
                FROM geo.vehicle_positions AS vp
                WHERE vp.organization_id = :organization_id
                  AND vp.recorded_at >= now() - make_interval(mins => :max_age_minutes)
                  AND (:vehicle_id IS NULL OR vp.vehicle_id = :vehicle_id)
                ORDER BY vp.vehicle_id, vp.recorded_at DESC,
                         vp.received_at DESC, vp.id DESC
            ) AS latest
            ORDER BY recorded_at DESC, vehicle_id
            LIMIT :limit
        """), {
            "organization_id": organization_id,
            "vehicle_id": vehicle_id,
            "max_age_minutes": max_age_minutes,
            "limit": limit,
        }).mappings().all()
    except GeoAuthorizationError:
        db.rollback()
        raise HTTPException(status_code=403, detail="Tracking permission for this organization is required.")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=503, detail="Tenant-scoped tracking storage is unavailable.")

    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Vary"] = "Cookie"
    return {
        "organization_id": str(organization_id),
        "generated_at": rows[0]["received_at"].isoformat() if rows else None,
        "positions": [
            {
                "vehicle_id": str(row["vehicle_id"]),
                "longitude": row["longitude"],
                "latitude": row["latitude"],
                "recorded_at": row["recorded_at"].isoformat(),
                "received_at": row["received_at"].isoformat(),
                "speed_kph": float(row["speed_kph"]),
                "heading_degrees": float(row["heading_degrees"]),
                "accuracy_meters": float(row["accuracy_meters"]),
                "is_synthetic": row["is_synthetic"],
            }
            for row in rows
        ],
    }
