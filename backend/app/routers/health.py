# FastAPI dependency injection requires Depends instances in endpoint defaults.
# ruff: noqa: B008
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


def _runtime_mode() -> str:
    return "synthetic-development" if settings.synthetic_data_only else settings.app_env


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness endpoint: process is running; it does not depend on database availability."""
    return HealthResponse(status="ok", mode=_runtime_mode())


@router.get("/ready", response_model=HealthResponse)
def readiness(db: Session = Depends(get_db)) -> HealthResponse:
    """Readiness endpoint: only report ready when the configured database responds."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database readiness check failed.") from exc
    return HealthResponse(status="ready", mode=_runtime_mode())
