"""Public general-account registration, authentication and recovery endpoints.

These routes are intentionally separate from /auth staff/operator authentication.
"""
import logging
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.request_security import require_allowed_origin
from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.identity.accounts import AccountIdentifier, AccountSession
from app.domains.identity.account_service import (
    AccountAuthenticationError, AccountRateLimited, authenticate_account,
    complete_password_recovery, enroll_password, register_account,
    request_password_recovery, resend_account_challenge, resolve_account_session, revoke_account_sessions,
    verify_identifier, decrypt_identifier, normalize_identifier,
)
from app.domains.identity.email_delivery import deliver_account_challenge

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/identity", tags=["account-identity"])
SESSION_COOKIE = "mnm_account_session"
CSRF_COOKIE = "mnm_account_csrf"


class RegistrationRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=160)
    identifier_type: Literal["email", "phone"]
    identifier_value: str = Field(min_length=3, max_length=254)
    preferred_locale: str = Field(default="am-ET", min_length=2, max_length=16)


class ResendChallengeRequest(BaseModel):
    identifier_type: Literal["email", "phone"]
    identifier_value: str = Field(min_length=3, max_length=254)
    purpose: Literal["identifier_verification", "credential_enrollment", "password_recovery"]


class ChallengeRequest(BaseModel):
    token: str = Field(min_length=32, max_length=128)


class PasswordEnrollmentRequest(ChallengeRequest):
    password: SecretStr


class LoginRequest(BaseModel):
    identifier_type: Literal["email", "phone"]
    identifier_value: str = Field(min_length=3, max_length=254)
    password: SecretStr


class RecoveryRequest(BaseModel):
    identifier_type: Literal["email", "phone"]
    identifier_value: str = Field(min_length=3, max_length=254)


class RecoveryCompleteRequest(ChallengeRequest):
    new_password: SecretStr


def _test_token(token: str) -> str | None:
    if settings.app_env in {"development", "test"} and settings.identity_expose_test_tokens:
        return token
    return None


def _audit_challenge_delivery(
    db: Session, *, account_id: UUID, purpose: str, delivery_status: str
) -> None:
    """Record the SMTP adapter result without storing recipient, token or credentials."""
    success = delivery_status == "sent"
    record_event(
        db,
        event_type="account.challenge.delivery",
        actor_type="system",
        actor_id=None,
        resource_type="platform_account",
        resource_id=str(account_id),
        action="send_verification_email",
        outcome="success" if success else "failure",
        reason_code=None if success else delivery_status,
        correlation_id=str(account_id),
        metadata={
            "channel": "email",
            "provider": "smtp",
            "purpose": purpose,
            "delivery_status": delivery_status,
        },
    )
    db.commit()


def _current_account(request: Request, db: Session = Depends(get_db)):
    try:
        context = resolve_account_session(db, request.cookies.get(SESSION_COOKIE))
        db.commit()
        return context
    except AccountAuthenticationError:
        raise HTTPException(status_code=401, detail="Authentication required.")


def _require_csrf(request: Request, session: AccountSession) -> None:
    require_allowed_origin(request)
    from app.domains.identity.security import token_digest
    import hmac

    cookie_token = request.cookies.get(CSRF_COOKIE)
    header_token = request.headers.get("X-CSRF-Token")
    if (not cookie_token or not header_token
            or not hmac.compare_digest(cookie_token, header_token)
            or not hmac.compare_digest(token_digest(cookie_token), session.csrf_digest)):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")


@router.post("/registrations", status_code=status.HTTP_202_ACCEPTED)
def create_account_registration(payload: RegistrationRequest, db: Session = Depends(get_db)) -> dict:
    try:
        account, token = register_account(
            db, display_name=payload.display_name,
            identifier_type=payload.identifier_type,
            identifier_value=payload.identifier_value,
            preferred_locale=payload.preferred_locale,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))
    except RuntimeError:
        db.rollback()
        raise HTTPException(status_code=503, detail="Identity encryption is not configured.")
    delivery_status = deliver_account_challenge(
        identifier_type=payload.identifier_type,
        destination=normalize_identifier(payload.identifier_type, payload.identifier_value),
        purpose="identifier_verification",
        token=token,
    )
    _audit_challenge_delivery(
        db, account_id=account.id, purpose="identifier_verification",
        delivery_status=delivery_status,
    )
    return {
        "account_id": str(account.id),
        "status": account.status,
        "delivery_status": delivery_status,
        "development_challenge_token": _test_token(token),
        "message": "Complete identifier verification before enrolling a password.",
    }


@router.post("/identifiers/verify")
def confirm_identifier(payload: ChallengeRequest, db: Session = Depends(get_db)) -> dict:
    try:
        account, enrollment_token = verify_identifier(db, raw_token=payload.token)
        identifier = db.scalar(select(AccountIdentifier).where(
            AccountIdentifier.account_id == account.id,
            AccountIdentifier.verified_at.is_not(None),
            AccountIdentifier.revoked_at.is_(None),
        ).order_by(AccountIdentifier.created_at.desc()).limit(1))
        if identifier is None:
            raise ValueError("Verified identifier is unavailable.")
        destination = decrypt_identifier(identifier.identifier_type, identifier.encrypted_value)
        identifier_type = identifier.identifier_type
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Identity delivery is not configured.") from exc
    delivery_status = deliver_account_challenge(
        identifier_type=identifier_type, destination=destination,
        purpose="credential_enrollment", token=enrollment_token,
    )
    return {
        "account_id": str(account.id),
        "status": account.status,
        "credential_enrollment_token": _test_token(enrollment_token),
        "delivery_status": delivery_status,
        "next_step": "enroll_password",
    }


@router.post("/credentials/password", status_code=status.HTTP_201_CREATED)
def create_password_credential(
    payload: PasswordEnrollmentRequest, db: Session = Depends(get_db)
) -> dict:
    try:
        account_id = enroll_password(
            db, raw_token=payload.token, password=payload.password.get_secret_value()
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    return {"account_id": str(account_id), "credential": "password", "status": "active"}


@router.post("/sessions")
def create_account_session(
    payload: LoginRequest, request: Request, response: Response,
    db: Session = Depends(get_db),
) -> dict:
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed.")
    client_ip = request.client.host if request.client else "unknown"
    try:
        account, session, raw_session, csrf = authenticate_account(
            db, identifier_type=payload.identifier_type,
            identifier_value=payload.identifier_value,
            password=payload.password.get_secret_value(), client_ip=client_ip,
        )
        db.commit()
    except AccountRateLimited:
        db.commit()
        raise HTTPException(status_code=429, detail="Too many login attempts.")
    except AccountAuthenticationError:
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Identity lookup is not configured.") from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=401, detail="Invalid credentials.") from exc
    secure = settings.should_use_secure_cookies(request.url.scheme)
    response.set_cookie(
        SESSION_COOKIE, raw_session, max_age=12 * 60 * 60,
        httponly=True, secure=secure, samesite="lax", path="/",
    )
    response.set_cookie(
        CSRF_COOKIE, csrf, max_age=12 * 60 * 60,
        httponly=False, secure=secure, samesite="lax", path="/",
    )
    return {
        "account_id": str(account.id),
        "display_name": account.display_name,
        "preferred_locale": account.preferred_locale,
        "expires_at": session.expires_at.isoformat(),
    }


@router.get("/sessions/current")
def read_current_account_session(context=Depends(_current_account)) -> dict:
    account, session = context
    return {
        "account_id": str(account.id),
        "display_name": account.display_name,
        "preferred_locale": account.preferred_locale,
        "session_id": str(session.id),
        "expires_at": session.expires_at.isoformat(),
    }


@router.get("/sessions")
def list_account_sessions(context=Depends(_current_account), db: Session = Depends(get_db)) -> list[dict]:
    account, current = context
    rows = db.scalars(select(AccountSession).where(
        AccountSession.account_id == account.id,
        AccountSession.revoked_at.is_(None),
        AccountSession.expires_at > func.now(),
    ).order_by(AccountSession.created_at.desc())).all()
    return [{
        "session_id": str(row.id), "created_at": row.created_at.isoformat(),
        "last_seen_at": row.last_seen_at.isoformat(), "expires_at": row.expires_at.isoformat(),
        "is_current": row.id == current.id,
    } for row in rows]


@router.delete("/sessions/current", status_code=status.HTTP_204_NO_CONTENT)
def revoke_current_account_session(
    request: Request, response: Response,
    context=Depends(_current_account), db: Session = Depends(get_db),
) -> Response:
    account, session = context
    _require_csrf(request, session)
    revoke_account_sessions(db, account_id=account.id, session_id=session.id)
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/", samesite="lax", secure=settings.should_use_secure_cookies(request.url.scheme))
    response.delete_cookie(CSRF_COOKIE, path="/", samesite="lax", secure=settings.should_use_secure_cookies(request.url.scheme))
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_one_account_session(
    session_id: UUID, request: Request, context=Depends(_current_account),
    db: Session = Depends(get_db),
) -> Response:
    account, current = context
    _require_csrf(request, current)
    target = db.scalar(select(AccountSession).where(
        AccountSession.id == session_id, AccountSession.account_id == account.id,
        AccountSession.revoked_at.is_(None),
    ).with_for_update())
    if target is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    revoke_account_sessions(db, account_id=account.id, session_id=target.id)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
def revoke_all_account_sessions(
    request: Request, response: Response, context=Depends(_current_account),
    db: Session = Depends(get_db),
) -> Response:
    account, current = context
    _require_csrf(request, current)
    revoke_account_sessions(db, account_id=account.id)
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/", samesite="lax")
    response.delete_cookie(CSRF_COOKIE, path="/", samesite="lax")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/recovery", status_code=status.HTTP_202_ACCEPTED)
def start_password_recovery(payload: RecoveryRequest, db: Session = Depends(get_db)) -> dict:
    try:
        token = request_password_recovery(
            db, identifier_type=payload.identifier_type,
            identifier_value=payload.identifier_value,
        )
        db.commit()
    except (ValueError, RuntimeError):
        db.rollback()
        token = None
    if token:
        try:
            delivery_status = deliver_account_challenge(
                identifier_type=payload.identifier_type,
                destination=normalize_identifier(payload.identifier_type, payload.identifier_value),
                purpose="password_recovery",
                token=token,
            )
            if delivery_status != "sent":
                logger.warning(
                    "account_challenge_delivery_not_sent purpose=password_recovery result=%s",
                    delivery_status,
                )
        except (ValueError, RuntimeError):
            logger.warning("account_challenge_delivery_not_sent purpose=password_recovery result=error")
    return {
        "message": "If the verified identifier matches an active account, recovery instructions will be sent.",
        "delivery_status": "accepted",
        "development_challenge_token": _test_token(token) if token else None,
    }


@router.post("/recovery/complete")
def finish_password_recovery(
    payload: RecoveryCompleteRequest, db: Session = Depends(get_db)
) -> dict:
    try:
        account_id = complete_password_recovery(
            db, raw_token=payload.token, new_password=payload.new_password.get_secret_value()
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "account_id": str(account_id),
        "recovery": "completed",
        "sessions_revoked": True,
    }


@router.post("/challenges/resend", status_code=status.HTTP_202_ACCEPTED)
def resend_identity_challenge(
    payload: ResendChallengeRequest, request: Request, db: Session = Depends(get_db)
) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    try:
        result = resend_account_challenge(
            db, identifier_type=payload.identifier_type,
            identifier_value=payload.identifier_value, purpose=payload.purpose,
            client_ip=client_ip,
        )
        db.commit()
    except (ValueError, RuntimeError):
        db.rollback()
        result = None
    if result is not None:
        _account, token = result
        try:
            delivery = deliver_account_challenge(
                identifier_type=payload.identifier_type,
                destination=normalize_identifier(payload.identifier_type, payload.identifier_value),
                purpose=payload.purpose, token=token,
            )
            if delivery != "sent":
                logger.warning(
                    "account_challenge_delivery_not_sent purpose=%s result=%s",
                    payload.purpose, delivery,
                )
        except (ValueError, RuntimeError):
            logger.warning(
                "account_challenge_delivery_not_sent purpose=%s result=error",
                payload.purpose,
            )
        return {
            "message": "If the account is eligible, a fresh challenge will be sent.",
            "status": "accepted",
            "development_challenge_token": _test_token(token),
        }
    return {
        "message": "If the account is eligible, a fresh challenge will be sent.",
        "status": "accepted",
        "development_challenge_token": None,
    }
