"""Provision a synthetic local platform administrator.

Run from backend/: python scripts/seed_synthetic_admin.py
The password is entered interactively and is never printed or committed.
"""
from getpass import getpass

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.domains.audit.service import record_event
from app.domains.identity.models import (
    Credential, Permission, Role, RoleAssignment, RolePermission, User,
)
from app.domains.identity.security import hash_secret

PLATFORM_PERMISSIONS = (
    "platform.access.manage",
    "platform.audit.read",
    "platform.operator.create",
    "platform.operator.review",
    "platform.catalog.manage",
    "platform.catalog.publish",
    "platform.trip.approve",
    "platform.trip.publish",
    "platform.fare.approve",
    "platform.fare.publish",
    "platform.fleet.review",
    "operator.fleet.manage",
    "operator.trip.manage",
    "operator.fare.propose",
    "organization.members.manage",
)

OPERATOR_PERMISSIONS = {
    "operator.fleet.manage",
    "operator.trip.manage",
    "operator.fare.propose",
    "organization.members.manage",
}


def main() -> None:
    if settings.app_env not in {"development", "test"} or not settings.synthetic_data_only:
        raise SystemExit("Refusing to provision outside synthetic development/test mode.")

    login = input("Synthetic administrator login identifier: ").strip().lower()
    display_name = input("Display name: ").strip()
    password = getpass("Password (minimum 14 characters): ")
    confirmation = getpass("Confirm password: ")
    if not login or not display_name or len(password) < 14 or password != confirmation:
        raise SystemExit("Invalid login/display name or password confirmation.")

    with SessionLocal() as db:
        if db.scalar(select(User.id).where(User.login_identifier == login)) is not None:
            raise SystemExit("That login identifier already exists.")
        user = User(login_identifier=login, display_name=display_name, status="active")
        role = db.scalar(select(Role).where(Role.code == "synthetic_platform_admin"))
        if role is None:
            role = Role(code="synthetic_platform_admin", description="Synthetic local platform administrator")
            db.add(role)
            db.flush()

        operator_role = db.scalar(select(Role).where(Role.code == "synthetic_operator_manager"))
        if operator_role is None:
            operator_role = Role(code="synthetic_operator_manager", description="Synthetic operator manager, organization-scoped")
            db.add(operator_role)
            db.flush()

        for code in PLATFORM_PERMISSIONS:
            permission = db.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code, description=code.replace(".", " ").title())
                db.add(permission)
                db.flush()
            target_roles = [role] if code.startswith("platform.") else [operator_role]
            for target_role in target_roles:
                assigned = db.scalar(select(RolePermission.id).where(
                    RolePermission.role_id == target_role.id,
                    RolePermission.permission_id == permission.id,
                ))
                if assigned is None:
                    db.add(RolePermission(role_id=target_role.id, permission_id=permission.id))

        db.add(user)
        db.flush()
        db.add(Credential(
            user_id=user.id, credential_type="password",
            secret_hash=hash_secret(password), status="active",
        ))
        db.add(RoleAssignment(
            user_id=user.id, role_id=role.id, organization_id=None,
            assigned_by=user.id,
        ))
        record_event(
            db, event_type="staff.synthetic_admin.provisioned", actor_type="system",
            actor_id=None, resource_type="staff_user", resource_id=str(user.id),
            action="provision", outcome="success",
            metadata={"role": role.code},
        )
        db.commit()
        print("Synthetic platform administrator provisioned.")
        print("Use the login identifier entered above; the password is not displayed.")


if __name__ == "__main__":
    main()
