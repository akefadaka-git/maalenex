"""G1 schema baseline; business tables remain pending G2 approval.

Revision ID: 0001_g1_foundation
Revises:
Create Date: 2026-11-06
"""

from collections.abc import Sequence

revision: str = "0001_g1_foundation"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Deliberately no application tables before G2 domain approval.
    pass


def downgrade() -> None:
    # The baseline owns no application objects.
    pass
