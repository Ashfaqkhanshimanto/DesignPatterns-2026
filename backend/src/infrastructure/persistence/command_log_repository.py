
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import CommandLogRow


class CommandLogRepository:
    """Saves and retrieves actuator command history."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(
        self,
        command_type: str,
        device_id: UUID,
        payload: dict,
        status: str,
        error_message: str | None = None,
    ) -> CommandLogRow:
        if status not in {"success", "failed", "rejected"}:
            raise ValueError(
                f"Invalid command status: {status}"
            )

        row = CommandLogRow(
            command_type=command_type,
            device_id=device_id,
            payload=payload,
            status=status,
            error_message=error_message,
            # Use the actual insertion time instead of
            # PostgreSQL's transaction start timestamp.
            created_at=func.clock_timestamp(),
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return row

    def list_recent(
        self,
        limit: int = 50,
    ) -> list[CommandLogRow]:
        statement = (
            select(CommandLogRow)
            .order_by(
                CommandLogRow.created_at.desc(),
                CommandLogRow.id.desc(),
            )
            .limit(limit)
        )

        return list(self._db.scalars(statement).all())
