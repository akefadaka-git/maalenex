"""Request-level browser origin checks for cookie-authenticated mutations."""
from fastapi import HTTPException, Request, status

from app.core.config import settings


def require_allowed_origin(request: Request) -> None:
    # Inspect raw ASGI headers so duplicate Origin fields cannot be hidden by
    # Starlette's convenience accessor selecting only one value.
    values = [
        value for key, value in request.scope.get("headers", [])
        if key.lower() == b"origin"
    ]
    if len(values) != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )
    try:
        origin = values[0].decode("ascii")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )
    if not origin or "," in origin or origin not in settings.allowed_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )
