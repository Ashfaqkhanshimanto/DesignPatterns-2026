from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.sensors.reading import Reading
from infrastructure.persistence.models import ReadingRow


class ReadingRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, reading: Reading) -> Reading:
        row = ReadingRow(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return self._row_to_reading(row)

    def list_recent(
        self,
        device_id: UUID,
        limit: int = 50,
    ) -> list[Reading]:
        statement = (
            select(ReadingRow)
            .where(ReadingRow.device_id == device_id)
            .order_by(ReadingRow.recorded_at.desc())
            .limit(limit)
        )

        rows = self._db.scalars(statement).all()

        return [
            self._row_to_reading(row)
            for row in rows
        ]

    def latest(
        self,
        device_id: UUID,
    ) -> Reading | None:
        statement = (
            select(ReadingRow)
            .where(ReadingRow.device_id == device_id)
            .order_by(ReadingRow.recorded_at.desc())
            .limit(1)
        )

        row = self._db.scalar(statement)

        if row is None:
            return None

        return self._row_to_reading(row)

    def latest_recorded_at(
        self,
        device_id: UUID,
    ) -> datetime | None:
        statement = (
            select(ReadingRow.recorded_at)
            .where(ReadingRow.device_id == device_id)
            .order_by(ReadingRow.recorded_at.desc())
            .limit(1)
        )

        return self._db.scalar(statement)

    @staticmethod
    def _row_to_reading(row: ReadingRow) -> Reading:
        return Reading(
            device_id=row.device_id,
            value=float(row.value),
            unit=row.unit,
            source=row.source,
            recorded_at=row.recorded_at,
        )