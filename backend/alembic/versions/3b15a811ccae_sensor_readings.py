"""sensor_readings

Revision ID: 3b15a811ccae
Revises: 61918ae6817c
Create Date: 2026-10-06 11:00:14.449496

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3b15a811ccae"
down_revision: Union[str, Sequence[str], None] = "61918ae6817c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "sensor_readings",
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
            "value",
            sa.Numeric(),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "recorded_at",
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
        "ix_sensor_readings_device_recorded_at",
        "sensor_readings",
        ["device_id", sa.literal_column("recorded_at DESC")],
        unique=False,
    )

    op.add_column(
        "devices",
        sa.Column(
            "sampling_interval_seconds",
            sa.Integer(),
            server_default=sa.text("300"),
            nullable=False,
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "tracking_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    # Phase 5 requirement:
    # Existing devices may already have sampling_interval_seconds
    # inside default_config from an earlier phase.
    # Copy valid numeric values into the new database column.
    op.execute(
        """
        UPDATE devices
        SET sampling_interval_seconds =
            (default_config ->> 'sampling_interval_seconds')::integer
        WHERE default_config ? 'sampling_interval_seconds'
          AND jsonb_typeof(default_config -> 'sampling_interval_seconds')
              = 'number'
          AND (default_config ->> 'sampling_interval_seconds')::integer >= 5
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "devices",
        "tracking_enabled",
    )

    op.drop_column(
        "devices",
        "sampling_interval_seconds",
    )

    op.drop_index(
        "ix_sensor_readings_device_recorded_at",
        table_name="sensor_readings",
    )

    op.drop_table(
        "sensor_readings",
    )