"""Phase 1 baseline.

Revision ID: 001
Revises:
Create Date: 2026-09-08

Phase 1 intentionally contains no business tables.
"""

from typing import Sequence, Union


from alembic import op


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No business tables are created in Phase 1.
    pass


def downgrade() -> None:
    # Nothing to remove because the baseline is empty.
    pass