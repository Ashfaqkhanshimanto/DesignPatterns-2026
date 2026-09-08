from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool


# ---------------------------------------------------------
# Make backend/src available to Python
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"

sys.path.insert(0, str(SRC_DIR))


# ---------------------------------------------------------
# Import the same settings used by the FastAPI application
# ---------------------------------------------------------

from infrastructure.settings import settings


# ---------------------------------------------------------
# Alembic configuration
# ---------------------------------------------------------

config = context.config


# Configure logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Use the exact same DATABASE_URL as the application
config.set_main_option(
    "sqlalchemy.url",
    settings.database_url,
)


# Phase 1 intentionally has no ORM models yet.
# Phase 2 will introduce models and metadata.
target_metadata = None


# ---------------------------------------------------------
# Offline migrations
# ---------------------------------------------------------

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------
# Online migrations
# ---------------------------------------------------------

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------
# Run correct migration mode
# ---------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()