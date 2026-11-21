"""Passenger in-app notification inbox and delivery preferences."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PassengerNotification(Base):
    __tablename__ = "passenger_notifications"
    __table_args__ = (
        Index("ix_passenger_notifications_owner_created", "passenger_id", "created_at"),
        Index("ix_passenger_notifications_owner_read", "passenger_id", "read_at"),
        UniqueConstraint("dedupe_key", name="uq_passenger_notifications_dedupe_key"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE"), nullable=False
    )
    notification_type: Mapped[str] = mapped_column(String(48), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(48), nullable=True)
    resource_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dedupe_key: Mapped[str] = mapped_column(String(128), nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PassengerNotificationPreference(Base):
    __tablename__ = "passenger_notification_preferences"
    __table_args__ = (
        UniqueConstraint("passenger_id", name="uq_passenger_notification_preferences_owner"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    passenger_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("passenger_accounts.id", ondelete="CASCADE"), nullable=False
    )
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    sms_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
