"""Passenger-owned accounts, credentials, sessions and login throttling.

Revision ID: 0009_passenger_identity
Revises: 0008_wallet_double_entry_ledger
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_passenger_identity"
down_revision = "0008_wallet_double_entry_ledger"
branch_labels = None
depends_on = None

def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "passenger_accounts",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("login_identifier", sa.String(254), nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="active"),
        sa.Column("contact_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("login_identifier", name="uq_passenger_accounts_login_identifier"),
        sa.CheckConstraint("status IN ('active', 'suspended', 'closed')", name="ck_passenger_accounts_status"),
    )
    op.create_index("ix_passenger_accounts_login_identifier", "passenger_accounts", ["login_identifier"])
    op.create_index("ix_passenger_accounts_status", "passenger_accounts", ["status"])
    op.create_table(
        "passenger_credentials",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("passenger_id", uuid, sa.ForeignKey("passenger_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("credential_type", sa.String(32), nullable=False),
        sa.Column("secret_hash", sa.String(512), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_passenger_credentials_passenger_id", "passenger_credentials", ["passenger_id"])
    op.create_table(
        "passenger_sessions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("passenger_id", uuid, sa.ForeignKey("passenger_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("secret_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("csrf_token_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_passenger_sessions_passenger_id", "passenger_sessions", ["passenger_id"])
    op.create_index("ix_passenger_sessions_expires_at", "passenger_sessions", ["expires_at"])
    op.create_table(
        "passenger_login_attempts",
        sa.Column("key_hash", sa.String(64), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )

def downgrade() -> None:
    op.drop_table("passenger_login_attempts")
    op.drop_index("ix_passenger_sessions_expires_at", table_name="passenger_sessions")
    op.drop_index("ix_passenger_sessions_passenger_id", table_name="passenger_sessions")
    op.drop_table("passenger_sessions")
    op.drop_index("ix_passenger_credentials_passenger_id", table_name="passenger_credentials")
    op.drop_table("passenger_credentials")
    op.drop_index("ix_passenger_accounts_status", table_name="passenger_accounts")
    op.drop_index("ix_passenger_accounts_login_identifier", table_name="passenger_accounts")
    op.drop_table("passenger_accounts")
