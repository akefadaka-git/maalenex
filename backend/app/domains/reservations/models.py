from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class ReservationReference(Base):
    __tablename__ = "reservation_references"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    booking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    public_reference: Mapped[str] = mapped_column(String(64), unique=True)
    qr_payload_version: Mapped[int] = mapped_column(default=1)
    qr_payload_reference: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
class BookingAccessGrant(Base):
    __tablename__ = "booking_access_grants"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    booking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    credential_hash: Mapped[str] = mapped_column(String(128), unique=True)
    csrf_token_hash: Mapped[str] = mapped_column(String(128))
    scope: Mapped[str] = mapped_column(String(32), default="read")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
