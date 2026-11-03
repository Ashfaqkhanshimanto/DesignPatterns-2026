
"""add actuator states

Revision ID: 30fab383bd23
Revises: f981d7c7d388
Create Date: 2026-11-03 10:51:48.625470

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "30fab383bd23"
down_revision: Union[str, Sequence[str], None] = (
    "f981d7c7d388"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create actuator states and initialize existing actuators."""

    # Create the new table.
    op.create_table(
        "actuator_states",
        sa.Column(
            "device_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=32),
            server_default=sa.text("'idle'"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("device_id"),
    )

    # Give all existing actuator devices an initial idle state.
    op.execute(
        """
        INSERT INTO actuator_states (device_id, state)
        SELECT id, 'idle'
        FROM devices
        WHERE role = 'actuator'
        """
    )


def downgrade() -> None:
    """Remove the actuator states table."""

    op.drop_table("actuator_states")
