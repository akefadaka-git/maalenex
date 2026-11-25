from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LedgerAccount(Base):
    __tablename__ = "ledger_accounts"
    __table_args__ = (
        CheckConstraint("normal_balance IN ('debit', 'credit')", name="ck_ledger_accounts_normal_balance"),
        CheckConstraint("status IN ('active', 'frozen', 'closed')", name="ck_ledger_accounts_status"),
        Index("ix_ledger_accounts_owner", "owner_type", "owner_ref"),
        Index(
            "uq_passenger_wallet_owner_currency",
            "owner_type",
            "owner_ref",
            "account_kind",
            "currency_code",
            unique=True,
            postgresql_where=text(
                "owner_type = 'passenger' AND account_kind = 'passenger_wallet' "
                "AND owner_ref IS NOT NULL"
            ),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    account_code: Mapped[str] = mapped_column(String(64), unique=True)
    account_kind: Mapped[str] = mapped_column(String(40))
    owner_type: Mapped[str] = mapped_column(String(32))
    owner_ref: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3))
    normal_balance: Mapped[str] = mapped_column(String(6))
    allow_negative: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LedgerTransaction(Base):
    __tablename__ = "ledger_transactions"
    __table_args__ = (
        CheckConstraint("amount_minor_units > 0", name="ck_ledger_transactions_positive_amount"),
        CheckConstraint("status IN ('posted', 'reversed')", name="ck_ledger_transactions_status"),
        Index("ix_ledger_transactions_created_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    reference: Mapped[str] = mapped_column(String(40), unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    transaction_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(16))
    amount_minor_units: Mapped[int] = mapped_column(BigInteger)
    currency_code: Mapped[str] = mapped_column(String(3))
    description: Mapped[str] = mapped_column(String(240))
    external_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LedgerPosting(Base):
    __tablename__ = "ledger_postings"
    __table_args__ = (
        CheckConstraint("side IN ('debit', 'credit')", name="ck_ledger_postings_side"),
        CheckConstraint("amount_minor_units > 0", name="ck_ledger_postings_positive_amount"),
        UniqueConstraint(
            "transaction_id", "account_id", "side",
            name="uq_ledger_posting_transaction_account_side",
        ),
        Index("ix_ledger_postings_transaction_id", "transaction_id"),
        Index("ix_ledger_postings_account", "account_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("ledger_transactions.id", ondelete="RESTRICT")
    )
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("ledger_accounts.id", ondelete="RESTRICT")
    )
    side: Mapped[str] = mapped_column(String(6))
    amount_minor_units: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
