from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SupportCase(Base):
    __tablename__ = "support_cases"
    __table_args__ = (
        Index("ix_support_cases_status_created", "status", "created_at"),
        Index("ix_support_cases_booking_id", "booking_id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    case_reference: Mapped[str] = mapped_column(String(32), unique=True)
    booking_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="RESTRICT")
    )
    category: Mapped[str] = mapped_column(String(32))
    subject: Mapped[str] = mapped_column(String(160))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="open")
    assigned_to: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    resolution_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
