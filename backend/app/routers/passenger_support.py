"""Passenger help content and authenticated support-case endpoints."""
# FastAPI dependency injection requires Depends instances in endpoint defaults.
# ruff: noqa: B008
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.domains.audit.service import record_event
from app.domains.identity.passenger_service import (
    PassengerContext,
    verify_passenger_csrf,
)
from app.domains.support.passenger_models import PassengerSupportCase
from app.routers.passenger_auth import current_passenger_context

router = APIRouter(prefix="/passenger/support", tags=["passenger-support"])

SupportCategory = Literal[
    "account", "booking", "journey", "wallet", "safety", "accessibility", "technical", "general"
]

_FAQS = {
    "en": [
        {"id": "account-login", "category": "account", "question": "How do I create or access my account?", "answer": "Create an account with an email address or international phone number and a password. Use the same identifier when you sign in."},
        {"id": "booking-status", "category": "booking", "question": "Where can I find my reservation?", "answer": "Open the booking flow and complete the booking-contact verification. A reservation reference is not a travel ticket or boarding authorization."},
        {"id": "journey-search", "category": "journey", "question": "Why can’t I find a journey?", "answer": "Only operator-published trips and locations appear. If no trip is listed, the route or schedule may not yet be published."},
        {"id": "wallet-safety", "category": "wallet", "question": "Can I deposit or withdraw money?", "answer": "Real-money wallet transactions are not enabled. Do not send money to anyone claiming to activate your MaaleNex wallet."},
        {"id": "privacy", "category": "safety", "question": "How is my account protected?", "answer": "Keep your password private, sign out on shared devices, and contact support if you notice activity you do not recognize."},
        {"id": "offline", "category": "technical", "question": "What happens when I lose internet access?", "answer": "Some locally available screens may remain visible. Requests that need the server cannot be submitted until the connection returns."},
    ],
    "am": [
        {"id": "account-login", "category": "account", "question": "መለያዬን እንዴት እፈጥራለሁ ወይም እገባለሁ?", "answer": "በኢሜይል ወይም በዓለም አቀፍ የስልክ ቁጥር እና በይለፍ ቃል መለያ ይፍጠሩ። ሲገቡ ያንኑ መለያ ይጠቀሙ።"},
        {"id": "booking-status", "category": "booking", "question": "የቦታ ማስያዣዬን የት አገኛለሁ?", "answer": "የቦታ ማስያዣ ሂደቱን ከፍተው የተሳፋሪ መረጃ ማረጋገጫን ያጠናቅቁ። የማስያዣ ማጣቀሻ የጉዞ ትኬት ወይም የመሳፈሪያ ፈቃድ አይደለም።"},
        {"id": "journey-search", "category": "journey", "question": "ለምን የጉዞ መረጃ አላገኘሁም?", "answer": "በኦፕሬተር የታተሙ መስመሮችና ጉዞዎች ብቻ ይታያሉ። መረጃ ካልታየ መስመሩ ወይም ሰዓቱ ገና ላይታተም ይችላል።"},
        {"id": "wallet-safety", "category": "wallet", "question": "ገንዘብ ማስገባት ወይም ማውጣት እችላለሁ?", "answer": "የእውነተኛ ገንዘብ ግብይት ገና አልነቃም። የቦርሳ አገልግሎትን ለማንቃት ነው ብሎ ለሚጠይቅ ሰው ገንዘብ አይላኩ።"},
        {"id": "privacy", "category": "safety", "question": "መለያዬ እንዴት ይጠበቃል?", "answer": "የይለፍ ቃልዎን በሚስጥር ይያዙ፣ በጋራ በሚጠቀሙበት መሣሪያ ላይ ይውጡ፣ ያልተለመደ እንቅስቃሴ ካዩ ድጋፍን ያግኙ።"},
        {"id": "offline", "category": "technical", "question": "የኢንተርኔት ግንኙነት ሲቋረጥ ምን ይሆናል?", "answer": "በመሣሪያው ያሉ አንዳንድ ማያዎች ሊታዩ ይችላሉ። ሰርቨር የሚፈልጉ ጥያቄዎች ግንኙነት እስኪመለስ ድረስ መላክ አይቻልም።"},
    ],
}


class SupportCaseCreate(BaseModel):
    category: SupportCategory = "general"
    subject: str = Field(min_length=3, max_length=160)
    message: str = Field(min_length=10, max_length=4000)


def _require_mutation_access(request: Request, context: PassengerContext) -> None:
    origin = request.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail="Request origin is not allowed.")
    if not verify_passenger_csrf(
        context,
        cookie_token=request.cookies.get("mnm_passenger_csrf"),
        header_token=request.headers.get("X-CSRF-Token"),
    ):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")


def _case_payload(case: PassengerSupportCase) -> dict:
    return {
        "case_reference": case.case_reference,
        "category": case.category,
        "subject": case.subject,
        "message": case.message,
        "status": case.status,
        "resolution_note": case.resolution_note,
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
        "resolved_at": case.resolved_at.isoformat() if case.resolved_at else None,
    }


@router.get("/faqs")
def list_support_faqs(language: Literal["am", "en"] = "am") -> dict:
    return {"language": language, "items": _FAQS[language]}


@router.post("/cases", status_code=status.HTTP_201_CREATED)
def create_support_case(
    payload: SupportCaseCreate,
    request: Request,
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    _require_mutation_access(request, context)
    subject, message = payload.subject.strip(), payload.message.strip()
    if len(subject) < 3 or len(message) < 10:
        raise HTTPException(status_code=422, detail="A subject and message are required.")
    cutoff = datetime.now(UTC) - timedelta(hours=1)
    recent_count = db.scalar(
        select(func.count()).select_from(PassengerSupportCase).where(
            PassengerSupportCase.passenger_id == context.passenger.id,
            PassengerSupportCase.created_at >= cutoff,
        )
    ) or 0
    if recent_count >= 5:
        raise HTTPException(status_code=429, detail="Support request limit reached. Try again later.")
    case = PassengerSupportCase(
        case_reference="MN-SUP-" + token_urlsafe(9).replace("-", "").replace("_", "").upper(),
        passenger_id=context.passenger.id,
        category=payload.category,
        subject=subject,
        message=message,
        status="open",
    )
    db.add(case)
    db.flush()
    record_event(
        db,
        event_type="passenger.support.case.created",
        actor_type="passenger",
        actor_id=str(context.passenger.id),
        resource_type="passenger_support_case",
        resource_id=str(case.id),
        action="create",
        outcome="success",
        metadata={"category": case.category, "case_reference": case.case_reference},
    )
    db.commit()
    db.refresh(case)
    return _case_payload(case)


@router.get("/cases")
def list_support_cases(
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    cases = db.scalars(
        select(PassengerSupportCase)
        .where(PassengerSupportCase.passenger_id == context.passenger.id)
        .order_by(PassengerSupportCase.created_at.desc())
        .limit(50)
    ).all()
    return {"items": [_case_payload(case) for case in cases]}


@router.get("/cases/{case_reference}")
def read_support_case(
    case_reference: str,
    context: PassengerContext = Depends(current_passenger_context),
    db: Session = Depends(get_db),
) -> dict:
    case = db.scalar(
        select(PassengerSupportCase).where(
            PassengerSupportCase.case_reference == case_reference,
            PassengerSupportCase.passenger_id == context.passenger.id,
        )
    )
    if case is None:
        raise HTTPException(status_code=404, detail="Support request not found.")
    return _case_payload(case)
