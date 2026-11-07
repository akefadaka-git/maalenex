from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class User(Base):
    __tablename__ = "staff_users"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    login_identifier: Mapped[str] = mapped_column(String(254), unique=True)
    display_name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
class Credential(Base):
    __tablename__ = "staff_credentials"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="CASCADE"), index=True)
    credential_type: Mapped[str] = mapped_column(String(32))
    secret_hash: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
class StaffSession(Base):
    __tablename__ = "staff_sessions"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="CASCADE"), index=True)
    secret_hash: Mapped[str] = mapped_column(String(128), unique=True)
    csrf_token_hash: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
class Role(Base):
    __tablename__ = "access_roles"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(String(240))
class Permission(Base):
    __tablename__ = "access_permissions"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(String(240))
class RolePermission(Base):
    __tablename__ = "access_role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    role_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("access_roles.id", ondelete="CASCADE"))
    permission_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("access_permissions.id", ondelete="CASCADE"))
class RoleAssignment(Base):
    __tablename__ = "access_role_assignments"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("access_roles.id", ondelete="RESTRICT"))
    organization_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    assigned_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class AuthLoginAttempt(Base):
    __tablename__ = "auth_login_attempts"
    key_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
