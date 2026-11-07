from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Uuid, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class BookingContact(Base):
    __tablename__ = "booking_contacts"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160))
    phone_normalized: Mapped[str] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Passenger(Base):
    __tablename__ = "passengers"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    display_name: Mapped[str] = mapped_column(String(160))

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    booking_reference: Mapped[str] = mapped_column(String(32), unique=True)
    booking_contact_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("booking_contacts.id", ondelete="RESTRICT"))
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("trips.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    currency_code: Mapped[str] = mapped_column(String(3), default="ETB")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)

class BookingPassenger(Base):
    __tablename__ = "booking_passengers"
    __table_args__ = (UniqueConstraint("booking_id", "passenger_sequence", name="uq_booking_passenger_sequence"),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    booking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    passenger_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("passengers.id", ondelete="RESTRICT"))
    trip_seat_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("trip_seats.id", ondelete="RESTRICT"))
    passenger_sequence: Mapped[int] = mapped_column(Integer)

class SeatHold(Base):
    __tablename__ = "seat_holds"
    __table_args__ = (Index("uq_active_trip_seat_hold", "trip_id", "trip_seat_id", unique=True,
                            postgresql_where=text("status = 'active'")),)
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    booking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("trips.id", ondelete="RESTRICT"), index=True)
    trip_seat_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("trip_seats.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    release_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)

class SeatAllocation(Base):
    __tablename__ = "seat_allocations"
    __table_args__ = (
        Index("uq_active_trip_seat_allocation", "trip_id", "trip_seat_id", unique=True,
              postgresql_where=text("status = 'active'")),
        Index("uq_active_booking_passenger_allocation", "booking_passenger_id", unique=True,
              postgresql_where=text("status = 'active'")),
    )
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    booking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    booking_passenger_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("booking_passengers.id", ondelete="CASCADE"))
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("trips.id", ondelete="RESTRICT"))
    trip_seat_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("trip_seats.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(24), default="active")
    allocated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class BookingFareSnapshot(Base):
    __tablename__ = "booking_fare_snapshots"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    booking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True)
    fare_version_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("fare_versions.id", ondelete="RESTRICT"))
    amount_minor_units: Mapped[int] = mapped_column(BigInteger)
    currency_code: Mapped[str] = mapped_column(String(3), default="ETB")
    fare_description_snapshot: Mapped[str] = mapped_column(String(240))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
