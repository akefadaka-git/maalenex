# ruff: noqa: I001
"""Fleet compliance evidence and seat-map geometry metadata.

Revision ID: 0016_fleet_compliance_and_geometry
Revises: 0015_scheduler_operations_rbac
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0016_fleet_compliance_and_geometry"
down_revision = "0015_scheduler_operations_rbac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "seat_layout_versions",
        sa.Column("geometry_metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_table(
        "vehicle_compliance_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(40), nullable=False),
        sa.Column("evidence_reference", sa.String(255), nullable=False, unique=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("review_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_vehicle_compliance_documents_vehicle_id", "vehicle_compliance_documents", ["vehicle_id"])
    op.create_index("ix_vehicle_compliance_documents_document_type", "vehicle_compliance_documents", ["document_type"])
    op.create_index("ix_vehicle_compliance_documents_status", "vehicle_compliance_documents", ["status"])
    op.create_table(
        "trip_operational_exceptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("resolution", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    for column in ("trip_id", "organization_id", "category", "status"):
        op.create_index(f"ix_trip_operational_exceptions_{column}", "trip_operational_exceptions", [column])


def downgrade() -> None:
    op.drop_index("ix_vehicle_compliance_documents_status", table_name="vehicle_compliance_documents")
    op.drop_index("ix_vehicle_compliance_documents_document_type", table_name="vehicle_compliance_documents")
    op.drop_index("ix_vehicle_compliance_documents_vehicle_id", table_name="vehicle_compliance_documents")
    op.drop_table("trip_operational_exceptions")
    op.drop_table("vehicle_compliance_documents")
    op.drop_column("seat_layout_versions", "geometry_metadata")
