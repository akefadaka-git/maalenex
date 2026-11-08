from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domains.platform.models import PlatformService, ServiceArea, ServiceAreaAvailability
from app.schemas.platform import PlatformServiceResponse

router = APIRouter(prefix="/platform", tags=["platform-services"])


@router.get("/services", response_model=list[PlatformServiceResponse])
def list_platform_services(
    area_code: str | None = Query(default=None, min_length=2, max_length=48),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List service lines and their explicitly configured geographic rollout state.

    A synthetic-test state is never reported as live availability. No service is
    considered available unless both the service and its area policy are enabled.
    """
    services = db.scalars(
        select(PlatformService).order_by(PlatformService.sort_order, PlatformService.code)
    ).all()
    availability_query = (
        select(ServiceAreaAvailability, ServiceArea)
        .join(ServiceArea, ServiceArea.code == ServiceAreaAvailability.area_code)
        .order_by(ServiceArea.name)
    )
    if area_code is not None:
        availability_query = availability_query.where(ServiceAreaAvailability.area_code == area_code)
    rows = db.execute(availability_query).all()
    by_service: dict[str, list[dict]] = {}
    now = datetime.now(timezone.utc)
    for policy, area in rows:
        in_window = (policy.valid_from is None or policy.valid_from <= now) and (
            policy.valid_until is None or policy.valid_until > now
        )
        enabled = policy.is_enabled and in_window
        service_is_enabled = next((item.is_enabled for item in services if item.code == policy.service_code), False)
        by_service.setdefault(policy.service_code, []).append({
            "area_code": area.code,
            "area_name": area.name,
            "availability_status": policy.availability_status,
            "is_enabled": enabled and service_is_enabled,
            "is_available": (
                enabled and service_is_enabled
                and policy.availability_status in {"pilot", "active"}
            ),
            "synthetic_test_available": (
                enabled and service_is_enabled
                and policy.availability_status == "synthetic_test"
            ),
        })
    return [
        {
            "code": service.code,
            "name": service.name,
            "description": service.description,
            "rollout_status": service.rollout_status,
            "is_enabled": service.is_enabled,
            "availability": by_service.get(service.code, []),
        }
        for service in services
    ]
