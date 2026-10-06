from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.devices.entity import Device
from domain.sensors.entity import Sensor
from infrastructure.persistence.models import DeviceRow, ZoneRow


class DeviceRepository:
    def __init__(self, db: Session):
        self._db = db

    # ---------------------------------------------------------
    # Phase 2 sensor methods
    # ---------------------------------------------------------

    def save_sensor(self, sensor: Sensor) -> Sensor:
        row = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            device_family="simulation",
            display_name=sensor.display_name,
            default_config=sensor.default_config,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return self._row_to_sensor(row)

    def list_sensors(self) -> list[Sensor]:
        statement = (
            select(DeviceRow)
            .where(DeviceRow.role == "sensor")
            .order_by(DeviceRow.created_at.desc())
        )

        rows = self._db.scalars(statement).all()

        return [
            self._row_to_sensor(row)
            for row in rows
        ]

    # ---------------------------------------------------------
    # Phase 3 unified device methods
    # ---------------------------------------------------------

    def save_device(self, device: Device) -> Device:
        row = DeviceRow(
            device_type=device.device_type,
            role=device.role,
            device_family=device.device_family,
            display_name=device.display_name,
            default_config=device.default_config,
            zone_id=device.zone_id,
            location_id=device.location_id,
            sampling_interval_seconds=device.sampling_interval_seconds,
            tracking_enabled=device.tracking_enabled,
        )

        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)

        return self._row_to_device(row)

    def save_devices(self, devices: list[Device]) -> list[Device]:
        rows = [
            DeviceRow(
                device_type=device.device_type,
                role=device.role,
                device_family=device.device_family,
                display_name=device.display_name,
                default_config=device.default_config,
                zone_id=device.zone_id,
                location_id=device.location_id,
                sampling_interval_seconds=device.sampling_interval_seconds,
                tracking_enabled=device.tracking_enabled,
            )
            for device in devices
        ]

        self._db.add_all(rows)
        self._db.commit()

        for row in rows:
            self._db.refresh(row)

        return [
            self._row_to_device(row)
            for row in rows
        ]

    def list_devices(
        self,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        statement = select(DeviceRow)

        if device_family is not None:
            statement = statement.where(
                DeviceRow.device_family == device_family
            )

        if role is not None:
            statement = statement.where(
                DeviceRow.role == role
            )

        statement = statement.order_by(
            DeviceRow.created_at.desc()
        )

        rows = self._db.scalars(statement).all()

        return [
            self._row_to_device(row)
            for row in rows
        ]

    # ---------------------------------------------------------
    # Phase 4 device assignment methods
    # ---------------------------------------------------------

    def get_device(
        self,
        device_id: UUID,
    ) -> Device | None:
        row = self._db.get(
            DeviceRow,
            device_id,
        )

        if row is None:
            return None

        return self._row_to_device(row)

    def assign_device_to_zone(
        self,
        device_id: UUID,
        zone_id: UUID,
    ) -> Device | None:
        device_row = self._db.get(
            DeviceRow,
            device_id,
        )

        if device_row is None:
            return None

        zone_row = self._db.get(
            ZoneRow,
            zone_id,
        )

        if zone_row is None:
            raise LookupError(
                f"Zone {zone_id} was not found."
            )

        try:
            device_row.zone_id = zone_row.id
            device_row.location_id = zone_row.location_id

            self._db.commit()
            self._db.refresh(device_row)

            return self._row_to_device(device_row)

        except Exception:
            self._db.rollback()
            raise

    def unassign_device(
        self,
        device_id: UUID,
    ) -> Device | None:
        device_row = self._db.get(
            DeviceRow,
            device_id,
        )

        if device_row is None:
            return None

        try:
            device_row.zone_id = None
            device_row.location_id = None

            self._db.commit()
            self._db.refresh(device_row)

            return self._row_to_device(device_row)

        except Exception:
            self._db.rollback()
            raise

    # ---------------------------------------------------------
    # Phase 5 sampling methods
    # ---------------------------------------------------------

    def update_sampling(
        self,
        device_id: UUID,
        sampling_interval_seconds: int,
        tracking_enabled: bool,
    ) -> Device | None:
        device_row = self._db.get(
            DeviceRow,
            device_id,
        )

        if device_row is None:
            return None

        try:
            device_row.sampling_interval_seconds = (
                sampling_interval_seconds
            )
            device_row.tracking_enabled = tracking_enabled

            self._db.commit()
            self._db.refresh(device_row)

            return self._row_to_device(device_row)

        except Exception:
            self._db.rollback()
            raise

    def list_tracked_simulation_sensors(
        self,
    ) -> list[Device]:
        statement = (
            select(DeviceRow)
            .where(DeviceRow.role == "sensor")
            .where(DeviceRow.tracking_enabled.is_(True))
            .where(
                DeviceRow.default_config["protocol"].astext
                == "simulation"
            )
            .order_by(DeviceRow.created_at.asc())
        )

        rows = self._db.scalars(statement).all()

        return [
            self._row_to_device(row)
            for row in rows
        ]

    # ---------------------------------------------------------
    # Row -> domain mapping
    # ---------------------------------------------------------

    @staticmethod
    def _row_to_sensor(row: DeviceRow) -> Sensor:
        return Sensor(
            id=row.id,
            device_type=row.device_type,
            display_name=row.display_name or "",
            default_config=row.default_config,
        )

    @staticmethod
    def _row_to_device(row: DeviceRow) -> Device:
        return Device(
            id=row.id,
            device_type=row.device_type,
            role=row.role,
            device_family=row.device_family,
            display_name=row.display_name or "",
            default_config=row.default_config,
            zone_id=row.zone_id,
            location_id=row.location_id,
            sampling_interval_seconds=row.sampling_interval_seconds,
            tracking_enabled=row.tracking_enabled,
        )