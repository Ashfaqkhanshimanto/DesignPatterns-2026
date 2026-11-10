
"""add actuator execution log

Revision ID: 25b6b118afd7
Revises: 30fab383bd23
Create Date: 2026-11-10 11:29:11.944126

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers used by Alembic.
revision: str = "25b6b118afd7"
down_revision: Union[str, Sequence[str], None] = (
    "30fab383bd23"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the actuator execution log table."""

    op.create_table(
        "actuator_execution_log",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "success",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "policy_applied",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_actuator_execution_log_device_created",
        "actuator_execution_log",
        [
            "device_id",
            sa.text("created_at DESC"),
        ],
        unique=False,
    )


def downgrade() -> None:
    """Remove the actuator execution log table."""

    op.drop_index(
        "ix_actuator_execution_log_device_created",
        table_name="actuator_execution_log",
    )

    op.drop_table("actuator_execution_log")
