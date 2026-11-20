"""Support cases opened by authenticated passengers, independent of bookings."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PassengerSupportCase(Base):
    __tablename__ = "passenger_support_cases"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved', 'closed')",
            name="ck_passenger_support_cases_status",
        ),
        Index("ix_passenger_support_owner_created", "passenger_id", "created_at"),
        Index("ix_passenger_support_status_created", "status", "created_at"),
        UniqueConstraint("case_reference", name="uq_passenger_support_cases_reference"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    case_reference: Mapped[str] = mapped_column(String(32), nullable=False)
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("passenger_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="open", server_default="open")
    resolution_note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
