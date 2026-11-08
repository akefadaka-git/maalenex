from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from app.domains.organizations.models import Organization, OrganizationMembership
from app.domains.audit.service import record_event

def create_candidate_operator(db: Session, *, display_name: str, actor_id: UUID) -> Organization:
    name = " ".join(display_name.split())
    if not name or len(name) > 200:
        raise ValueError("display_name must contain 1 to 200 characters")
    organization = Organization(id=uuid4(), organization_type="operator",
                                display_name=name, status="candidate")
    db.add(organization)
    record_event(db, event_type="operator.candidate.created", actor_type="staff",
                 actor_id=str(actor_id), resource_type="organization",
                 resource_id=str(organization.id), action="create",
                 outcome="success", organization_id=organization.id)
    return organization

def add_membership(db: Session, *, organization_id: UUID, user_id: UUID,
                   actor_id: UUID) -> OrganizationMembership:
    membership = OrganizationMembership(organization_id=organization_id, user_id=user_id,
                                         membership_status="active")
    db.add(membership)
    record_event(db, event_type="organization.membership.created", actor_type="staff",
                 actor_id=str(actor_id), resource_type="organization_membership",
                 resource_id=str(membership.id), action="create", outcome="success",
                 organization_id=organization_id)
    return membership
