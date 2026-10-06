from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from application.readings.sampler import ReadingSampler
from domain.devices.entity import Device


class FakeDeviceRepository:
    def __init__(self, devices):
        self.devices = devices

    def list_tracked_simulation_sensors(self):
        return self.devices


class FakeReadingRepository:
    def __init__(self, latest=None):
        self.latest = latest

    def latest_recorded_at(self, device_id):
        return self.latest


class FakeReadingIngest:
    def __init__(self):
        self.recorded_device_ids = []

    def record(self, device_id):
        self.recorded_device_ids.append(device_id)


def make_sensor(interval=300):
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
        sampling_interval_seconds=interval,
        tracking_enabled=True,
    )


def test_sampler_records_sensor_with_no_previous_reading():
    sensor = make_sensor()

    device_repository = FakeDeviceRepository(
        [sensor]
    )
    reading_repository = FakeReadingRepository(
        latest=None
    )
    reading_ingest = FakeReadingIngest()

    sampler = ReadingSampler(
        device_repository,
        reading_repository,
        reading_ingest,
    )

    now = datetime(
        2026,
        10,
        6,
        12,
        0,
        tzinfo=timezone.utc,
    )

    created = sampler.run_once(now=now)

    assert created == 1
    assert reading_ingest.recorded_device_ids == [
        sensor.id
    ]


def test_sampler_skips_sensor_before_interval_is_due():
    sensor = make_sensor(interval=300)

    now = datetime(
        2026,
        10,
        6,
        12,
        0,
        tzinfo=timezone.utc,
    )

    reading_repository = FakeReadingRepository(
        latest=now - timedelta(seconds=299)
    )
    reading_ingest = FakeReadingIngest()

    sampler = ReadingSampler(
        FakeDeviceRepository([sensor]),
        reading_repository,
        reading_ingest,
    )

    created = sampler.run_once(now=now)

    assert created == 0
    assert reading_ingest.recorded_device_ids == []


def test_sampler_records_sensor_when_interval_is_due():
    sensor = make_sensor(interval=300)

    now = datetime(
        2026,
        10,
        6,
        12,
        0,
        tzinfo=timezone.utc,
    )

    reading_repository = FakeReadingRepository(
        latest=now - timedelta(seconds=300)
    )
    reading_ingest = FakeReadingIngest()

    sampler = ReadingSampler(
        FakeDeviceRepository([sensor]),
        reading_repository,
        reading_ingest,
    )

    created = sampler.run_once(now=now)

    assert created == 1
    assert reading_ingest.recorded_device_ids == [
        sensor.id
    ]


def test_sampler_rejects_naive_datetime():
    sensor = make_sensor()

    sampler = ReadingSampler(
        FakeDeviceRepository([sensor]),
        FakeReadingRepository(),
        FakeReadingIngest(),
    )

    naive_time = datetime(
        2026,
        10,
        6,
        12,
        0,
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        sampler.run_once(now=naive_time)