"""MITP device registry, vehicle assignment history and telemetry.

Revision ID: 0008_mitp_tracking
Revises: 0007_operator_invites_support
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_mitp_tracking"
down_revision = "0007_operator_invites_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "tracking_devices",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("device_identifier", sa.String(80), nullable=False, unique=True),
        sa.Column("credential_ciphertext", sa.String(512), nullable=False),
        sa.Column("credential_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("last_sequence", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_tracking_devices_device_identifier", "tracking_devices", ["device_identifier"])
    op.create_index("ix_tracking_devices_status", "tracking_devices", ["status"])

    op.create_table(
        "vehicle_device_assignments",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("device_id", uuid, sa.ForeignKey("tracking_devices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vehicle_id", uuid, sa.ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assigned_by", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL")),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("unassigned_by", uuid, sa.ForeignKey("staff_users.id", ondelete="SET NULL")),
        sa.Column("unassigned_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_vehicle_device_assignments_device_id", "vehicle_device_assignments", ["device_id"])
    op.create_index("ix_vehicle_device_assignments_vehicle_id", "vehicle_device_assignments", ["vehicle_id"])
    op.execute("""
        CREATE UNIQUE INDEX uq_active_device_assignment_device
        ON vehicle_device_assignments(device_id) WHERE unassigned_at IS NULL
    """)
    op.execute("""
        CREATE UNIQUE INDEX uq_active_device_assignment_vehicle
        ON vehicle_device_assignments(vehicle_id) WHERE unassigned_at IS NULL
    """)

    op.create_table(
        "vehicle_telemetry",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("device_id", uuid, sa.ForeignKey("tracking_devices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vehicle_id", uuid, sa.ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("speed_kph", sa.Numeric(6, 2), nullable=False),
        sa.Column("heading_degrees", sa.Numeric(6, 2), nullable=False),
        sa.Column("accuracy_meters", sa.Numeric(7, 2), nullable=False),
        sa.UniqueConstraint("device_id", "sequence", name="uq_vehicle_telemetry_device_sequence"),
    )
    op.create_index("ix_vehicle_telemetry_device_id", "vehicle_telemetry", ["device_id"])
    op.create_index("ix_vehicle_telemetry_vehicle_id", "vehicle_telemetry", ["vehicle_id"])
    op.create_index("ix_vehicle_telemetry_recorded_at", "vehicle_telemetry", ["recorded_at"])
    op.create_index("ix_vehicle_telemetry_vehicle_recorded", "vehicle_telemetry", ["vehicle_id", "recorded_at"])

    op.execute("""
        INSERT INTO access_permissions (id, code, description)
        VALUES
          (gen_random_uuid(), 'platform.tracking.manage', 'Register, assign, rotate and revoke tracking devices'),
          (gen_random_uuid(), 'platform.tracking.read', 'Read vehicle tracking positions')
        ON CONFLICT (code) DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table("vehicle_telemetry")
    op.execute("DROP INDEX IF EXISTS uq_active_device_assignment_vehicle")
    op.execute("DROP INDEX IF EXISTS uq_active_device_assignment_device")
    op.drop_table("vehicle_device_assignments")
    op.drop_table("tracking_devices")
    op.execute("""
        DELETE FROM access_permissions
        WHERE code IN ('platform.tracking.manage', 'platform.tracking.read')
          AND NOT EXISTS (
              SELECT 1 FROM access_role_permissions rp
              WHERE rp.permission_id = access_permissions.id
          )
    """)
