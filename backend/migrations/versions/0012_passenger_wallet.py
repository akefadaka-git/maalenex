"""Enforce one ETB passenger wallet account per passenger.

Revision ID: 0012_passenger_wallet
Revises: 0011_passenger_reports
"""
import sqlalchemy as sa
from alembic import op

revision = "0012_passenger_wallet"
down_revision = "0011_passenger_reports"
branch_labels = None
depends_on = None

_WALLET_PREDICATE = "owner_type = 'passenger' AND account_kind = 'passenger_wallet' AND owner_ref IS NOT NULL"


def upgrade() -> None:
    op.create_index(
        "uq_passenger_wallet_owner_currency",
        "ledger_accounts",
        ["owner_type", "owner_ref", "account_kind", "currency_code"],
        unique=True,
        postgresql_where=sa.text(_WALLET_PREDICATE),
        sqlite_where=sa.text(_WALLET_PREDICATE),
    )


def downgrade() -> None:
    op.drop_index("uq_passenger_wallet_owner_currency", table_name="ledger_accounts")
