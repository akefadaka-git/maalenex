"""Operator invitations and passenger support case workflows.

Revision ID: 0007_operator_invites_support
Revises: 0006_guest_access_rate_limits
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_operator_invites_support"
down_revision = "0006_guest_access_rate_limits"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "organization_invitations",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("organization_id", uuid, sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("login_identifier", sa.String(254), nullable=False),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("role_id", uuid, sa.ForeignKey("access_roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("created_by", uuid, sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_organization_invitations_organization_id", "organization_invitations", ["organization_id"])
    op.create_index("ix_organization_invitations_expires_at", "organization_invitations", ["expires_at"])
    op.execute("""
        CREATE UNIQUE INDEX uq_open_organization_invitation
        ON organization_invitations(organization_id, login_identifier)
        WHERE accepted_at IS NULL AND revoked_at IS NULL
    """)

    op.create_table(
        "support_cases",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("case_reference", sa.String(32), nullable=False, unique=True),
        sa.Column("booking_id", uuid, sa.ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("subject", sa.String(160), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("assigned_to", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL")),
        sa.Column("resolution_code", sa.String(80)),
        sa.Column("resolution_note", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_support_cases_status_created", "support_cases", ["status", "created_at"])
    op.create_index("ix_support_cases_booking_id", "support_cases", ["booking_id"])


def downgrade() -> None:
    op.drop_table("support_cases")
    op.drop_index("uq_open_organization_invitation", table_name="organization_invitations")
    op.drop_table("organization_invitations")
