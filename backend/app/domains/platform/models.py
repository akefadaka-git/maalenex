from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String,
    UniqueConstraint, Uuid, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlatformService(Base):
    __tablename__ = "platform_services"
    __table_args__ = (
        CheckConstraint(
            "rollout_status IN ('planned', 'synthetic_test', 'pilot', 'active', 'suspended')",
            name="ck_platform_services_rollout_status",
        ),
    )

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    rollout_status: Mapped[str] = mapped_column(String(24), nullable=False, default="planned")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ServiceArea(Base):
    __tablename__ = "service_areas"

    code: Mapped[str] = mapped_column(String(48), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="ET")
    administrative_area: Mapped[str] = mapped_column(String(120), nullable=False)
    area_type: Mapped[str] = mapped_column(String(24), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ServiceAreaAvailability(Base):
    __tablename__ = "service_area_availability"
    __table_args__ = (
        UniqueConstraint("service_code", "area_code", name="uq_service_area_availability"),
        CheckConstraint(
            "availability_status IN ('planned', 'synthetic_test', 'pilot', 'active', 'suspended')",
            name="ck_service_area_availability_status",
        ),
        CheckConstraint(
            "valid_until IS NULL OR valid_from IS NULL OR valid_until > valid_from",
            name="ck_service_area_validity_window",
        ),
        Index("ix_service_area_availability_area_code", "area_code"),
        Index("ix_service_area_availability_service_code", "service_code"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    service_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("platform_services.code", ondelete="CASCADE"), nullable=False
    )
    area_code: Mapped[str] = mapped_column(
        String(48), ForeignKey("service_areas.code", ondelete="RESTRICT"), nullable=False
    )
    availability_status: Mapped[str] = mapped_column(String(24), nullable=False, default="planned")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
