# ruff: noqa: I001
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import model_registry  # noqa: F401
from app.db.session import SessionLocal
from app.jobs.booking_hold_expiry import expire_due_booking_holds
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.bookings import router as bookings_router
from app.routers.health import router as health_router
from app.routers.passenger_auth import router as passenger_auth_router
from app.routers.passenger_catalog import router as passenger_catalog_router
from app.routers.passenger_notifications import router as passenger_notifications_router
from app.routers.passenger_bookings import router as passenger_bookings_router
from app.routers.passenger_reports import router as passenger_reports_router
from app.routers.passenger_support import router as passenger_support_router
from app.routers.passenger_wallet import router as passenger_wallet_router

logger = logging.getLogger(__name__)

async def _hold_expiry_loop() -> None:
    """Development worker; row locks make concurrent API workers safe."""
    while True:
        try:
            def run_batch() -> None:
                with SessionLocal() as db:
                    try:
                        expire_due_booking_holds(db, batch_size=100)
                        db.commit()
                    except Exception:
                        db.rollback()
                        raise
            await asyncio.to_thread(run_batch)
        except Exception:
            logger.exception("Scheduled booking hold expiry batch failed")
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_hold_expiry_loop()) if settings.app_env == "development" else None
    try:
        yield
    finally:
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    version="0.1.0",
    description="Passenger MVP development API. Synthetic data only; payment, ticketing, boarding and production use are disabled.",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
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
app.include_router(bookings_router, prefix=settings.api_prefix)
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
        "status": "development",
        "synthetic_data_only": settings.synthetic_data_only,
    }
