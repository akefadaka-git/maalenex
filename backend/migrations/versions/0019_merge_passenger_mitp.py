"""Merge passenger and MITP migration histories.

Revision ID: 0019_merge_passenger_mitp
Revises: 0018_koybe_boarding_point, 0008_mitp_tracking

This is a graph-only merge. It preserves both parent histories and performs
no schema or data mutation.
"""
revision = "0019_merge_passenger_mitp"
down_revision = ("0018_koybe_boarding_point", "0008_mitp_tracking")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
