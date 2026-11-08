from uuid import UUID, uuid4
from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class Location(Base):
    __tablename__ = "locations"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160))
    location_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
class Terminal(Base):
    __tablename__ = "terminals"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    location_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("locations.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(24), default="draft")
class Route(Base):
    __tablename__ = "routes"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(60), unique=True)
    origin_location_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("locations.id", ondelete="RESTRICT"))
    destination_location_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("locations.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
class RouteStop(Base):
    __tablename__ = "route_stops"
    __table_args__ = (UniqueConstraint("route_id", "sequence_number", name="uq_route_stop_sequence"),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    route_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("locations.id", ondelete="RESTRICT"))
    sequence_number: Mapped[int] = mapped_column(Integer)
    boarding_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    alighting_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(24), default="draft")
