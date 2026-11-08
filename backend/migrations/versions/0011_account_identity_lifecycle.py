"""Account registration, identifier challenges, sessions and recovery.

Revision ID: 0011_account_identity_lifecycle
Revises: 0010_accounts_trust
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_account_identity_lifecycle"
down_revision = "0010_accounts_trust"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "account_sessions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("secret_digest", sa.String(64), nullable=False, unique=True),
        sa.Column("csrf_digest", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_account_sessions_account_id", "account_sessions", ["account_id"])
    op.create_index("ix_account_sessions_expires_at", "account_sessions", ["expires_at"])

    op.create_table(
        "account_challenges",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("account_id", uuid, sa.ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("identifier_id", uuid, sa.ForeignKey("account_identifiers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.String(32), nullable=False),
        sa.Column("token_digest", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "purpose IN ('identifier_verification', 'password_recovery')",
            name="ck_account_challenge_purpose",
        ),
    )
    op.create_index("ix_account_challenges_account_id", "account_challenges", ["account_id"])
    op.create_index("ix_account_challenges_expires_at", "account_challenges", ["expires_at"])

    op.create_table(
        "account_login_attempts",
        sa.Column("key_digest", sa.String(64), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("account_login_attempts")
    op.drop_index("ix_account_challenges_expires_at", table_name="account_challenges")
    op.drop_index("ix_account_challenges_account_id", table_name="account_challenges")
    op.drop_table("account_challenges")
    op.drop_index("ix_account_sessions_expires_at", table_name="account_sessions")
    op.drop_index("ix_account_sessions_account_id", table_name="account_sessions")
    op.drop_table("account_sessions")
