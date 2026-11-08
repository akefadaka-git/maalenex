"""Persistent staff login throttling and CSRF session token storage.

Revision ID: 0004_staff_auth_controls
Revises: 0003_passenger_domains
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_staff_auth_controls"
down_revision = "0003_passenger_domains"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("staff_sessions", sa.Column("csrf_token_hash", sa.String(128), nullable=False, server_default=""))
    op.create_table(
        "auth_login_attempts",
        sa.Column("key_hash", sa.String(64), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
    )

def downgrade() -> None:
    op.drop_table("auth_login_attempts")
    op.drop_column("staff_sessions", "csrf_token_hash")
