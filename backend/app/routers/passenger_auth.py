"""Passenger registration, login, profile and logout endpoints."""
# FastAPI dependency injection requires Depends instances in endpoint defaults.
# ruff: noqa: B008
import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.identity.passenger_service import (
    PassengerAuthenticationError,
    PassengerContext,
    PassengerRateLimited,
    create_passenger_session,
    register_passenger,
    resolve_passenger_session,
    verify_passenger_csrf,
)

router = APIRouter(prefix="/passenger/auth", tags=["passenger-auth"])
SESSION_COOKIE = "mnm_passenger_session"
CSRF_COOKIE = "mnm_passenger_csrf"

class PassengerRegistration(BaseModel):
    login_identifier: str = Field(min_length=5, max_length=254)
    display_name: str = Field(min_length=2, max_length=120)
    password: SecretStr

class PassengerLogin(BaseModel):
    login_identifier: str = Field(min_length=5, max_length=254)
    password: SecretStr

class PassengerProfileUpdate(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)

def _identifier(value: str) -> str:
    value = value.strip().lower()
    email = re.fullmatch(r"[^\s@]{1,64}@[^\s@.]+(?:\.[^\s@.]+)+", value)
    phone = re.fullmatch(r"\+[1-9][0-9]{7,14}", value)
    if not (email or phone):
        raise HTTPException(status_code=422, detail="Use a valid email or international phone number.")
    return value

def _cookies(request: Request, response: Response, issued) -> None:
    secure = settings.should_use_secure_cookies(request.url.scheme)
    response.set_cookie(SESSION_COOKIE, issued.session_token, max_age=43200, httponly=True, secure=secure, samesite="lax", path="/")
    response.set_cookie(CSRF_COOKIE, issued.csrf_token, max_age=43200, httponly=False, secure=secure, samesite="lax", path="/")

def current_passenger_context(request: Request, db: Session = Depends(get_db)) -> PassengerContext:
    try:
        context = resolve_passenger_session(db, raw_token=request.cookies.get(SESSION_COOKIE))
        db.commit()
        return context
    except PassengerAuthenticationError:
        raise HTTPException(status_code=401, detail="Passenger authentication required.")

def _csrf(request: Request, context: PassengerContext) -> None:
    if not verify_passenger_csrf(context, cookie_token=request.cookies.get(CSRF_COOKIE), header_token=request.headers.get("X-CSRF-Token")):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")

def _origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed.")

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: PassengerRegistration, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    _origin(request)
    identifier = _identifier(payload.login_identifier)
    password = payload.password.get_secret_value()
    if len(password) < 12 or len(password) > 128:
        raise HTTPException(status_code=422, detail="Password must contain 12 to 128 characters.")
    try:
        passenger = register_passenger(db, login_identifier=identifier, display_name=payload.display_name, password=password)
        issued = create_passenger_session(db, login_identifier=identifier, password=password, client_ip=request.client.host if request.client else "unknown")
        db.commit()
    except PassengerAuthenticationError as exc:
        db.rollback()
        if str(exc) == "account_exists":
            raise HTTPException(status_code=409, detail="An account already exists for this contact.")
        raise HTTPException(status_code=401, detail="Unable to create passenger session.")
    _cookies(request, response, issued)
    return {"id": str(passenger.id), "display_name": passenger.display_name, "login_identifier": passenger.login_identifier, "contact_verified": False, "expires_at": issued.session.expires_at.isoformat()}

@router.post("/sessions")
def login(payload: PassengerLogin, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    _origin(request)
    identifier = _identifier(payload.login_identifier)
    try:
        issued = create_passenger_session(db, login_identifier=identifier, password=payload.password.get_secret_value(), client_ip=request.client.host if request.client else "unknown")
        db.commit()
    except PassengerRateLimited:
        db.commit()
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")
    except PassengerAuthenticationError:
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    _cookies(request, response, issued)
    return {"id": str(issued.passenger.id), "display_name": issued.passenger.display_name, "login_identifier": issued.passenger.login_identifier, "expires_at": issued.session.expires_at.isoformat()}

@router.get("/sessions/current")
def current(context: PassengerContext = Depends(current_passenger_context)) -> dict:
    return {"id": str(context.passenger.id), "display_name": context.passenger.display_name, "login_identifier": context.passenger.login_identifier, "contact_verified": context.passenger.contact_verified_at is not None, "expires_at": context.session.expires_at.isoformat()}

@router.patch("/profile")
def update_profile(payload: PassengerProfileUpdate, request: Request, context: PassengerContext = Depends(current_passenger_context), db: Session = Depends(get_db)) -> dict:
    _csrf(request, context)
    context.passenger.display_name = payload.display_name.strip()
    record_event(db, event_type="passenger.profile.updated", actor_type="passenger", actor_id=str(context.passenger.id), resource_type="passenger_account", resource_id=str(context.passenger.id), action="update_profile", outcome="success")
    db.commit()
    return {"id": str(context.passenger.id), "display_name": context.passenger.display_name, "login_identifier": context.passenger.login_identifier, "contact_verified": context.passenger.contact_verified_at is not None, "expires_at": context.session.expires_at.isoformat()}

@router.delete("/sessions/current", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, context: PassengerContext = Depends(current_passenger_context), db: Session = Depends(get_db)) -> Response:
    _csrf(request, context)
    context.session.revoked_at = db.scalar(select(func.now()))
    record_event(db, event_type="passenger.session.revoked", actor_type="passenger", actor_id=str(context.passenger.id), resource_type="passenger_session", resource_id=str(context.session.id), action="logout", outcome="success")
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/", samesite="lax")
    response.delete_cookie(CSRF_COOKIE, path="/", samesite="lax")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
