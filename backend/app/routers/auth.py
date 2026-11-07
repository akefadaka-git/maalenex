from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.identity.models import Credential, RoleAssignment, User
from app.domains.identity.security import hash_secret, token_digest
from app.domains.organizations.models import Organization, OrganizationInvitation, OrganizationMembership
from app.domains.audit.service import record_event
from app.domains.identity.service import (
    AuthenticationError, AuthenticationRateLimited, StaffContext,
    authenticate_staff, resolve_staff_session, verify_csrf,
)

router = APIRouter(prefix="/auth", tags=["staff-auth"])
SESSION_COOKIE = "mnm_staff_session"
CSRF_COOKIE = "mnm_csrf"


class LoginRequest(BaseModel):
    login_identifier: str = Field(min_length=1, max_length=254)
    password: SecretStr


class AcceptOperatorInvitation(BaseModel):
    token: str = Field(min_length=32, max_length=128)
    password: SecretStr


def current_staff_context(request: Request, db: Session = Depends(get_db)) -> StaffContext:
    try:
        context = resolve_staff_session(db, raw_token=request.cookies.get(SESSION_COOKIE))
        db.commit()
        return context
    except AuthenticationError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")


def require_csrf(request: Request, context: StaffContext) -> None:
    if not verify_csrf(
        context, cookie_token=request.cookies.get(CSRF_COOKIE),
        header_token=request.headers.get("X-CSRF-Token"),
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed.")


@router.post("/operator-invitations/accept", status_code=status.HTTP_201_CREATED)
def accept_operator_invitation(
    payload: AcceptOperatorInvitation, db: Session = Depends(get_db),
) -> dict:
    password = payload.password.get_secret_value()
    if len(password) < 14 or len(password) > 256:
        raise HTTPException(status_code=422, detail="Password must contain 14 to 256 characters.")
    now = db.scalar(select(func.now()))
    invitation = db.scalar(select(OrganizationInvitation).where(
        OrganizationInvitation.token_hash == token_digest(payload.token),
        OrganizationInvitation.accepted_at.is_(None),
        OrganizationInvitation.revoked_at.is_(None),
        OrganizationInvitation.expires_at > now,
    ).with_for_update())
    if invitation is None:
        raise HTTPException(status_code=404, detail="Invitation is invalid or expired.")
    operator = db.get(Organization, invitation.organization_id)
    if operator is None or operator.organization_type != "operator" or operator.status != "approved":
        raise HTTPException(status_code=409, detail="Operator organization is not approved for account activation.")
    if db.scalar(select(User.id).where(
        User.login_identifier == invitation.login_identifier
    )) is not None:
        raise HTTPException(status_code=409, detail="A staff account already exists for this login.")
    user = User(
        login_identifier=invitation.login_identifier,
        display_name=invitation.display_name,
        status="active",
    )
    db.add(user)
    db.flush()
    db.add(Credential(
        user_id=user.id, credential_type="password",
        secret_hash=hash_secret(password), status="active",
    ))
    db.add(OrganizationMembership(
        organization_id=operator.id, user_id=user.id, membership_status="active",
    ))
    db.add(RoleAssignment(
        user_id=user.id, role_id=invitation.role_id,
        organization_id=operator.id, assigned_by=invitation.created_by,
    ))
    invitation.accepted_at = now
    record_event(
        db, event_type="organization.invitation.accepted", actor_type="guest",
        actor_id=str(user.id), resource_type="organization_invitation",
        resource_id=str(invitation.id), action="accept", outcome="success",
        organization_id=operator.id, metadata={"role": "synthetic_operator_manager"},
    )
    db.commit()
    return {
        "user_id": str(user.id),
        "login_identifier": user.login_identifier,
        "organization_id": str(operator.id),
        "membership_status": "active",
        "next_step": "sign_in",
    }


@router.post("/sessions")
def create_staff_session(
    payload: LoginRequest, request: Request, response: Response,
    db: Session = Depends(get_db),
) -> dict:
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Request origin is not allowed.")
    client_ip = request.client.host if request.client else "unknown"
    try:
        issued = authenticate_staff(
            db, login_identifier=payload.login_identifier,
            password=payload.password.get_secret_value(), client_ip=client_ip,
        )
        db.commit()
    except AuthenticationRateLimited:
        db.commit()
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts.")
    except AuthenticationError:
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    secure_cookie = request.url.scheme == "https"
    response.set_cookie(
        SESSION_COOKIE, issued.session_token, max_age=8 * 60 * 60,
        httponly=True, secure=secure_cookie, samesite="lax", path="/",
    )
    response.set_cookie(
        CSRF_COOKIE, issued.csrf_token, max_age=8 * 60 * 60,
        httponly=False, secure=secure_cookie, samesite="lax", path="/",
    )
    return {
        "id": str(issued.user.id),
        "display_name": issued.user.display_name,
        "login_identifier": issued.user.login_identifier,
        "expires_at": issued.session.expires_at.isoformat(),
    }


@router.get("/sessions/current")
def read_current_staff_session(
    context: StaffContext = Depends(current_staff_context),
) -> dict:
    return {
        "id": str(context.user.id),
        "display_name": context.user.display_name,
        "login_identifier": context.user.login_identifier,
        "expires_at": context.session.expires_at.isoformat(),
    }


@router.delete("/sessions/current", status_code=status.HTTP_204_NO_CONTENT)
def revoke_current_staff_session(
    request: Request, response: Response,
    context: StaffContext = Depends(current_staff_context),
    db: Session = Depends(get_db),
) -> Response:
    require_csrf(request, context)
    from sqlalchemy import func, select
    from app.domains.identity.models import StaffSession
    context.session.revoked_at = db.scalar(select(func.now()))
    record_event(
        db, event_type="staff.session.revoked", actor_type="staff",
        actor_id=str(context.user.id), resource_type="staff_session",
        resource_id=str(context.session.id), action="logout", outcome="success",
    )
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/", samesite="lax")
    response.delete_cookie(CSRF_COOKIE, path="/", samesite="lax")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
