from datetime import datetime, timezone
from uuid import uuid4

import pytest

from application.readings.service import (
    AdapterSelectionError,
    DeviceNotFoundError,
    ReadingIngest,
)
from domain.devices.entity import Device
from domain.sensors.reading import Reading


class FakeDeviceRepository:
    def __init__(self, device=None):
        self.device = device

    def get_device(self, device_id):
        return self.device


class FakeReadingRepository:
    def __init__(self):
        self.saved_readings = []

    def add(self, reading):
        self.saved_readings.append(reading)
        return reading


def make_simulation_sensor():
    return Device(
        id=uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Test Moisture Sensor",
        default_config={
            "protocol": "simulation",
            "unit": "vwc",
        },
        sampling_interval_seconds=300,
        tracking_enabled=True,
    )


def test_record_reads_and_saves_simulation_sensor():
    sensor = make_simulation_sensor()

    device_repository = FakeDeviceRepository(
        sensor
    )
    reading_repository = FakeReadingRepository()

    service = ReadingIngest(
        device_repository,
        reading_repository,
    )

    result = service.record(sensor.id)

    assert result.device_id == sensor.id
    assert result.source == "simulation"
    assert result.unit == "vwc"

    assert len(
        reading_repository.saved_readings
    ) == 1

    saved = reading_repository.saved_readings[0]

    assert saved.device_id == sensor.id
    assert saved.source == "simulation"


def test_record_rejects_missing_device():
    service = ReadingIngest(
        FakeDeviceRepository(None),
        FakeReadingRepository(),
    )

    with pytest.raises(
        DeviceNotFoundError,
        match="was not found",
    ):
        service.record(uuid4())


def test_record_rejects_non_sensor_device():
    actuator = Device(
        id=uuid4(),
        device_type="water_pump",
        role="actuator",
        device_family="simulation",
        display_name="Test Water Pump",
        default_config={
            "protocol": "simulation",
        },
        sampling_interval_seconds=300,
        tracking_enabled=True,
    )

    service = ReadingIngest(
        FakeDeviceRepository(actuator),
        FakeReadingRepository(),
    )

    with pytest.raises(
        AdapterSelectionError,
        match="is not a sensor",
    ):
        service.record(actuator.id)


def test_record_rejects_unsupported_protocol():
    sensor = Device(
        id=uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="edge",
        display_name="Edge Moisture Sensor",
        default_config={
            "protocol": "modbus",
        },
        sampling_interval_seconds=300,
        tracking_enabled=True,
    )

    service = ReadingIngest(
        FakeDeviceRepository(sensor),
        FakeReadingRepository(),
    )

    with pytest.raises(
        AdapterSelectionError,
        match="Unsupported sensor protocol",
    ):
        service.record(sensor.id)


def test_record_translated_saves_reading():
    sensor = make_simulation_sensor()

    reading = Reading(
        device_id=sensor.id,
        value=0.45,
        unit="vwc",
        source="mqtt",
        recorded_at=datetime.now(
            timezone.utc
        ),
    )

    reading_repository = FakeReadingRepository()

    service = ReadingIngest(
        FakeDeviceRepository(sensor),
        reading_repository,
    )

    result = service.record_translated(
        reading
    )

    assert result.device_id == sensor.id
    assert result.value == 0.45
    assert result.unit == "vwc"
    assert result.source == "mqtt"

    assert reading_repository.saved_readings == [
        reading
    ]


def test_translate_mqtt_returns_normalized_reading():
    device_id = uuid4()

    reading = ReadingIngest.translate_mqtt(
        device_id,
        {
            "value": 900,
            "unit": "lux",
        },
    )

    assert reading.device_id == device_id
    assert reading.value == 900
    assert reading.unit == "lux"
    assert reading.source == "mqtt"
    assert reading.recorded_at.tzinfo is not None