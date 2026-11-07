from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import model_registry  # noqa: F401
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.passenger_catalog import router as passenger_catalog_router

app = FastAPI(
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
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(passenger_catalog_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str | bool]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "status": "development",
        "synthetic_data_only": settings.synthetic_data_only,
    }
