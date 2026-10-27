
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class OverviewRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_location(self, location_id: UUID):
        return self._db.get(LocationRow, location_id)

    def get_zones(self, location_id: UUID):
        return self._db.scalars(
            select(ZoneRow)
            .where(ZoneRow.location_id == location_id)
            .order_by(ZoneRow.name, ZoneRow.id)
        ).all()

    def get_assigned_devices(self, location_id: UUID):
        # Only devices assigned to zones in this location.
        # Excludes devices with no zone assignment.
        return self._db.scalars(
            select(DeviceRow)
            .join(
                ZoneRow,
                DeviceRow.zone_id == ZoneRow.id,
            )
            .where(
                DeviceRow.location_id == location_id,
                ZoneRow.location_id == location_id,
                DeviceRow.zone_id.is_not(None),
            )
            .order_by(DeviceRow.display_name, DeviceRow.id)
        ).all()

    def get_latest_readings(self, device_ids: list[UUID]):
        if not device_ids:
            return {}

        # Rank readings separately for each device.
        # This avoids a separate SQL query for each device.
        ranked = (
            select(
                ReadingRow.id.label("reading_id"),
                ReadingRow.device_id.label("device_id"),
                func.row_number().over(
                    partition_by=ReadingRow.device_id,
                    order_by=(
                        ReadingRow.recorded_at.desc(),
                        ReadingRow.id.desc(),
                    ),
                ).label("reading_rank"),
            )
            .where(ReadingRow.device_id.in_(device_ids))
            .subquery()
        )

        statement = (
            select(ReadingRow)
            .join(
                ranked,
                ReadingRow.id == ranked.c.reading_id,
            )
            .where(ranked.c.reading_rank == 1)
        )

        rows = self._db.scalars(statement).all()

        return {
            row.device_id: row
            for row in rows
        }
