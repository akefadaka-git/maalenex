from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.health import router as health_router

app = FastAPI(title=settings.app_name, version="0.1.0", description="Synthetic-only development API.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)
app.include_router(health_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"name": settings.app_name, "environment": settings.app_env, "status": "development"}
