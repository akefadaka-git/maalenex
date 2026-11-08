from uuid import UUID
from sqlalchemy.orm import Session
from app.domains.audit.models import AuditEvent

_SENSITIVE_KEYS = {"password", "secret", "token", "authorization", "phone", "email", "qr", "credential"}

def redact_metadata(value: dict | None) -> dict:
    safe = {}
    for key, item in (value or {}).items():
        normalized_key = key.lower().replace("-", "_")
        if any(marker in normalized_key for marker in _SENSITIVE_KEYS):
            safe[key] = "[REDACTED]"
        elif isinstance(item, dict):
            safe[key] = redact_metadata(item)
        elif isinstance(item, (str, int, float, bool)) or item is None:
            safe[key] = item
        else:
            safe[key] = str(item)[:160]
    return safe

def record_event(
    db: Session, *, event_type: str, actor_type: str, actor_id: str | None,
    resource_type: str, resource_id: str | None, action: str, outcome: str,
    organization_id: UUID | None = None, actor_role_snapshot: str | None = None,
    reason_code: str | None = None, request_id: str | None = None,
    correlation_id: str | None = None, metadata: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        event_type=event_type, actor_type=actor_type, actor_id=actor_id,
        actor_role_snapshot=actor_role_snapshot, organization_id=organization_id,
        resource_type=resource_type, resource_id=resource_id, action=action,
        outcome=outcome, reason_code=reason_code, request_id=request_id,
        correlation_id=correlation_id, metadata_redacted=redact_metadata(metadata),
    )
    db.add(event)
    return event
