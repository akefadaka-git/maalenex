from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domains.identity.models import Permission, RoleAssignment, RolePermission

def has_permission(db: Session, *, user_id: UUID, permission_code: str,
                   organization_id: UUID | None) -> bool:
    statement = (
        select(Permission.id)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(RoleAssignment, RoleAssignment.role_id == RolePermission.role_id)
        .where(
            RoleAssignment.user_id == user_id,
            RoleAssignment.revoked_at.is_(None),
            Permission.code == permission_code,
        )
    )
    if organization_id is None:
        # Platform-wide grants are explicit and cannot be inferred from a null tenant.
        statement = statement.where(RoleAssignment.organization_id.is_(None), Permission.code.like("platform.%"))
    else:
        statement = statement.where(RoleAssignment.organization_id == organization_id)
    return db.scalar(statement.limit(1)) is not None
