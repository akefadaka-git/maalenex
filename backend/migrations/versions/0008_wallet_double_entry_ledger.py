"""Double-entry wallet ledger foundation.

Revision ID: 0008_wallet_double_entry_ledger
Revises: 0007_operator_invites_support
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_wallet_double_entry_ledger"
down_revision = "0007_operator_invites_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "ledger_accounts",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("account_code", sa.String(64), nullable=False, unique=True),
        sa.Column("account_kind", sa.String(40), nullable=False),
        sa.Column("owner_type", sa.String(32), nullable=False),
        sa.Column("owner_ref", uuid, nullable=True),
        sa.Column("currency_code", sa.String(3), nullable=False),
        sa.Column("normal_balance", sa.String(6), nullable=False),
        sa.Column("allow_negative", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("normal_balance IN ('debit', 'credit')", name="ck_ledger_accounts_normal_balance"),
        sa.CheckConstraint("status IN ('active', 'frozen', 'closed')", name="ck_ledger_accounts_status"),
    )
    op.create_index("ix_ledger_accounts_owner", "ledger_accounts", ["owner_type", "owner_ref"])

    op.create_table(
        "ledger_transactions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("reference", sa.String(40), nullable=False, unique=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False, unique=True),
        sa.Column("transaction_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="posted"),
        sa.Column("amount_minor_units", sa.BigInteger(), nullable=False),
        sa.Column("currency_code", sa.String(3), nullable=False),
        sa.Column("description", sa.String(240), nullable=False),
        sa.Column("external_reference", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("amount_minor_units > 0", name="ck_ledger_transactions_positive_amount"),
        sa.CheckConstraint("status IN ('posted', 'reversed')", name="ck_ledger_transactions_status"),
    )
    op.create_index("ix_ledger_transactions_created_at", "ledger_transactions", ["created_at"])

    op.create_table(
        "ledger_postings",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("transaction_id", uuid, sa.ForeignKey("ledger_transactions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("account_id", uuid, sa.ForeignKey("ledger_accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("side", sa.String(6), nullable=False),
        sa.Column("amount_minor_units", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("side IN ('debit', 'credit')", name="ck_ledger_postings_side"),
        sa.CheckConstraint("amount_minor_units > 0", name="ck_ledger_postings_positive_amount"),
        sa.UniqueConstraint("transaction_id", "account_id", "side", name="uq_ledger_posting_transaction_account_side"),
    )
    op.create_index("ix_ledger_postings_transaction_id", "ledger_postings", ["transaction_id"])
    op.create_index("ix_ledger_postings_account", "ledger_postings", ["account_id", "created_at"])


def downgrade() -> None:
    op.drop_table("ledger_postings")
    op.drop_index("ix_ledger_transactions_created_at", table_name="ledger_transactions")
    op.drop_table("ledger_transactions")
    op.drop_index("ix_ledger_accounts_owner", table_name="ledger_accounts")
    op.drop_table("ledger_accounts")
