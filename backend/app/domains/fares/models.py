from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class Fare(Base):
    __tablename__ = "fares"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    route_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("routes.id", ondelete="RESTRICT"))
    trip_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("trips.id", ondelete="RESTRICT"), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
class FareVersion(Base):
    __tablename__ = "fare_versions"
    __table_args__ = (UniqueConstraint("fare_id", "version_number", name="uq_fare_version"),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    fare_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("fares.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    amount_minor_units: Mapped[int] = mapped_column(BigInteger)
    currency_code: Mapped[str] = mapped_column(String(3), default="ETB")
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="draft")
    proposed_by: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    approved_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True)
    published_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
class FareApproval(Base):
    __tablename__ = "fare_approvals"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    fare_version_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("fare_versions.id", ondelete="CASCADE"), index=True)
    decision: Mapped[str] = mapped_column(String(24))
    reviewer_user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"))
    reason: Mapped[str] = mapped_column(String(500))
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
