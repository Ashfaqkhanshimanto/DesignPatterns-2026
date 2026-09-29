from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from domain.locations.entity import Location, LocationConfig, Zone
from infrastructure.persistence.models import DeviceRow, LocationRow, ZoneRow


class LocationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_config(
        self,
        config: LocationConfig,
    ) -> LocationConfig:
        """Save a new location and all of its zones as one transaction."""

        try:
            location_row = LocationRow(
                name=config.location.name,
            )

            self._session.add(location_row)
            self._session.flush()

            zone_rows: list[ZoneRow] = []

            for zone in config.location.zones:
                zone_row = ZoneRow(
                    location_id=location_row.id,
                    name=zone.name,
                    moisture_threshold_low=zone.moisture_threshold_low,
                    moisture_threshold_high=zone.moisture_threshold_high,
                    schedule=zone.schedule,
                )

                self._session.add(zone_row)
                zone_rows.append(zone_row)

            self._session.flush()
            self._session.commit()

            saved_zones = tuple(
                self._zone_row_to_domain(zone_row)
                for zone_row in zone_rows
            )

            saved_location = Location(
                id=location_row.id,
                name=location_row.name,
                zones=saved_zones,
            )

            return LocationConfig(
                location=saved_location,
            )

        except Exception:
            self._session.rollback()
            raise

    def get_config(
        self,
        location_id: UUID,
    ) -> LocationConfig | None:
        location_row = self._session.get(
            LocationRow,
            location_id,
        )

        if location_row is None:
            return None

        zone_rows = self._session.scalars(
            select(ZoneRow)
            .where(ZoneRow.location_id == location_id)
            .order_by(ZoneRow.name)
        ).all()

        zones = tuple(
            self._zone_row_to_domain(zone_row)
            for zone_row in zone_rows
        )

        location = Location(
            id=location_row.id,
            name=location_row.name,
            zones=zones,
        )

        return LocationConfig(
            location=location,
        )

    def list_locations(self) -> list[Location]:
        rows = self._session.scalars(
            select(LocationRow)
            .order_by(LocationRow.created_at.desc())
        ).all()

        return [
            Location(
                id=row.id,
                name=row.name,
                zones=(),
            )
            for row in rows
        ]

    def delete_location(
        self,
        location_id: UUID,
    ) -> bool:
        location_row = self._session.get(
            LocationRow,
            location_id,
        )

        if location_row is None:
            return False

        try:
            self._session.execute(
                update(DeviceRow)
                .where(DeviceRow.location_id == location_id)
                .values(
                    zone_id=None,
                    location_id=None,
                )
            )

            self._session.delete(location_row)
            self._session.commit()

            return True

        except Exception:
            self._session.rollback()
            raise

    def add_zone(
        self,
        location_id: UUID,
        zone: Zone,
    ) -> Zone | None:
        location_row = self._session.get(
            LocationRow,
            location_id,
        )

        if location_row is None:
            return None

        try:
            zone_row = ZoneRow(
                location_id=location_id,
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )

            self._session.add(zone_row)
            self._session.flush()
            self._session.commit()

            return self._zone_row_to_domain(zone_row)

        except Exception:
            self._session.rollback()
            raise

    def update_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
        zone: Zone,
    ) -> Zone | None:
        zone_row = self._session.scalar(
            select(ZoneRow).where(
                ZoneRow.id == zone_id,
                ZoneRow.location_id == location_id,
            )
        )

        if zone_row is None:
            return None

        try:
            zone_row.name = zone.name
            zone_row.moisture_threshold_low = (
                zone.moisture_threshold_low
            )
            zone_row.moisture_threshold_high = (
                zone.moisture_threshold_high
            )
            zone_row.schedule = zone.schedule

            self._session.flush()
            self._session.commit()

            return self._zone_row_to_domain(zone_row)

        except Exception:
            self._session.rollback()
            raise

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> str:
        location_row = self._session.get(
            LocationRow,
            location_id,
        )

        if location_row is None:
            return "location_not_found"

        zone_row = self._session.scalar(
            select(ZoneRow).where(
                ZoneRow.id == zone_id,
                ZoneRow.location_id == location_id,
            )
        )

        if zone_row is None:
            return "zone_not_found"

        zone_count = self._session.scalar(
            select(func.count())
            .select_from(ZoneRow)
            .where(
                ZoneRow.location_id == location_id
            )
        )

        if zone_count is None or zone_count <= 1:
            return "last_zone"

        try:
            self._session.execute(
                update(DeviceRow)
                .where(DeviceRow.zone_id == zone_id)
                .values(
                    zone_id=None,
                    location_id=None,
                )
            )

            self._session.delete(zone_row)
            self._session.commit()

            return "deleted"

        except Exception:
            self._session.rollback()
            raise

    @staticmethod
    def _zone_row_to_domain(
        zone_row: ZoneRow,
    ) -> Zone:
        return Zone(
            id=zone_row.id,
            name=zone_row.name,
            moisture_threshold_low=float(
                zone_row.moisture_threshold_low
            ),
            moisture_threshold_high=float(
                zone_row.moisture_threshold_high
            ),
            schedule=zone_row.schedule,
        )