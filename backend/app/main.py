# ruff: noqa: I001
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import model_registry  # noqa: F401
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.bookings import router as bookings_router
from app.routers.cargo import router as cargo_router
from app.routers.cargo_dispatch import router as cargo_dispatch_router
from app.routers.health import router as health_router
from app.routers.passenger_auth import router as passenger_auth_router
from app.routers.passenger_catalog import router as passenger_catalog_router
from app.routers.passenger_notifications import router as passenger_notifications_router
from app.routers.passenger_bookings import router as passenger_bookings_router
from app.routers.passenger_reports import router as passenger_reports_router
from app.routers.passenger_support import router as passenger_support_router
from app.routers.passenger_wallet import router as passenger_wallet_router
from app.routers.staff_admin import router as staff_admin_router

production = settings.app_env == "production"

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="MaaleNex shared mobility platform API.",
    openapi_url=None if production else f"{settings.api_prefix}/openapi.json",
    docs_url=None if production else f"{settings.api_prefix}/docs",
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "X-CSRF-Token", "Idempotency-Key"],
)
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)
app.include_router(staff_admin_router, prefix=settings.api_prefix)
app.include_router(bookings_router, prefix=settings.api_prefix)
app.include_router(cargo_router, prefix=settings.api_prefix)
app.include_router(cargo_dispatch_router, prefix=settings.api_prefix)
app.include_router(passenger_catalog_router, prefix=settings.api_prefix)
app.include_router(passenger_auth_router, prefix=settings.api_prefix)
app.include_router(passenger_support_router, prefix=settings.api_prefix)
app.include_router(passenger_reports_router, prefix=settings.api_prefix)
app.include_router(passenger_wallet_router, prefix=settings.api_prefix)
app.include_router(passenger_notifications_router, prefix=settings.api_prefix)
app.include_router(passenger_bookings_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str | bool]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "status": "running" if production else "development",
        "synthetic_data_only": settings.synthetic_data_only,
    }
