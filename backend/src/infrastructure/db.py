from sqlalchemy import create_engine, text

from infrastructure.settings import settings


engine = create_engine(settings.database_url)


def check_database_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False