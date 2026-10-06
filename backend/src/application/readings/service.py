from domain.sensors.reading import Reading
from infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from infrastructure.adapters.sensors.simulation import SimulationSensorAdapter
from infrastructure.adapters.sensors.vendor_stub import VendorStubSensorAdapter
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.reading_repository import ReadingRepository

from application.readings.dto import ReadingDto


class DeviceNotFoundError(ValueError):
    pass


class AdapterSelectionError(ValueError):
    pass


class ReadingIngest:
    def __init__(
        self,
        device_repository: DeviceRepository,
        reading_repository: ReadingRepository,
    ) -> None:
        self._device_repository = device_repository
        self._reading_repository = reading_repository

    def record(self, device_id) -> ReadingDto:
        device = self._device_repository.get_device(device_id)

        if device is None:
            raise DeviceNotFoundError(
                f"Device {device_id} was not found."
            )

        if device.role != "sensor":
            raise AdapterSelectionError(
                f"Device {device_id} is not a sensor."
            )

        adapter = self._select_adapter(device.default_config)

        reading = adapter.read(
            device_id=device_id,
            device_type=device.device_type,
        )

        stored = self._reading_repository.add(reading)

        return self._to_dto(stored)

    def record_translated(
        self,
        reading: Reading,
    ) -> ReadingDto:
        device = self._device_repository.get_device(
            reading.device_id
        )

        if device is None:
            raise DeviceNotFoundError(
                f"Device {reading.device_id} was not found."
            )

        if device.role != "sensor":
            raise AdapterSelectionError(
                f"Device {reading.device_id} is not a sensor."
            )

        stored = self._reading_repository.add(reading)

        return self._to_dto(stored)

    @staticmethod
    def _select_adapter(default_config: dict[str, object]):
        protocol = str(
            default_config.get("protocol", "simulation")
        ).strip().lower()

        if protocol == "simulation":
            return SimulationSensorAdapter()

        if protocol == "vendor":
            return VendorStubSensorAdapter()

        if protocol == "mqtt":
            raise AdapterSelectionError(
                "MQTT sensors require an already translated payload."
            )

        raise AdapterSelectionError(
            f"Unsupported sensor protocol: {protocol}"
        )

    @staticmethod
    def translate_mqtt(
        device_id,
        payload: dict[str, object],
    ) -> Reading:
        adapter = MqttSensorAdapter()

        return adapter.translate(
            device_id=device_id,
            payload=payload,
        )

    @staticmethod
    def _to_dto(reading: Reading) -> ReadingDto:
        return ReadingDto(
            device_id=reading.device_id,
            value=reading.value,
            unit=reading.unit,
            source=reading.source,
            recorded_at=reading.recorded_at,
        )