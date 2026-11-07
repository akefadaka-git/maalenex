from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_type: Mapped[str] = mapped_column(String(32), default="operator")
    display_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(24), default="candidate", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    __table_args__ = (Index("uq_active_organization_membership", "organization_id", "user_id", unique=True, postgresql_where=text("revoked_at IS NULL")),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="CASCADE"), index=True)
    membership_status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
