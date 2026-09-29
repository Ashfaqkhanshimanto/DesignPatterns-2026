from uuid import UUID

from domain.devices.entity import Device
from infrastructure.persistence.device_repository import DeviceRepository


class DeviceNotFoundError(ValueError):
    """Raised when a requested device does not exist."""
    pass


class ZoneNotFoundError(ValueError):
    """Raised when a requested zone does not exist."""
    pass


class DeviceAssignmentService:
    def __init__(
        self,
        repository: DeviceRepository,
    ) -> None:
        self._repository = repository

    def assign_device(
        self,
        device_id: UUID,
        zone_id: UUID,
    ) -> Device:
        try:
            device = self._repository.assign_device_to_zone(
                device_id=device_id,
                zone_id=zone_id,
            )
        except LookupError as exc:
            raise ZoneNotFoundError(
                f"Zone {zone_id} was not found."
            ) from exc

        if device is None:
            raise DeviceNotFoundError(
                f"Device {device_id} was not found."
            )

        return device

    def unassign_device(
        self,
        device_id: UUID,
    ) -> Device:
        device = self._repository.unassign_device(
            device_id=device_id,
        )

        if device is None:
            raise DeviceNotFoundError(
                f"Device {device_id} was not found."
            )

        return device