"""Idempotently grant the dedicated Move dispatch permission to the synthetic platform admin.

Run from backend/ after provisioning the synthetic platform administrator:
    python -m scripts.seed_move_dispatch_permission

This is restricted to synthetic development/test environments and never activates Move.
"""
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.domains.identity.models import Permission, Role, RolePermission


def seed() -> None:
    if settings.app_env not in {"development", "test"} or not settings.synthetic_data_only:
        raise RuntimeError("Move dispatch permission seeding requires synthetic development/test mode.")

    with SessionLocal.begin() as db:
        role = db.scalar(select(Role).where(Role.code == "synthetic_platform_admin"))
        if role is None:
            raise RuntimeError("Synthetic platform administrator role is not provisioned.")

        permission = db.scalar(select(Permission).where(Permission.code == "platform.move.dispatch"))
        if permission is None:
            permission = Permission(
                code="platform.move.dispatch",
                description="Platform Move dispatch and driver assignment",
            )
            db.add(permission)
            db.flush()

        assignment = db.scalar(select(RolePermission.id).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        ))
        if assignment is None:
            db.add(RolePermission(role_id=role.id, permission_id=permission.id))


def main() -> None:
    seed()
    print("PASS: dedicated Move dispatch permission granted to synthetic platform admin.")


if __name__ == "__main__":
    main()
