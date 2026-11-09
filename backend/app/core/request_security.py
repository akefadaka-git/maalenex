"""Request-level browser origin checks for cookie-authenticated mutations."""
from fastapi import HTTPException, Request, status

from app.core.config import settings


def require_allowed_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is None or origin not in settings.allowed_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )
