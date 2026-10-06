from uuid import uuid4

import pytest

from infrastructure.adapters.sensors.mqtt import MqttSensorAdapter
from infrastructure.adapters.sensors.simulation import SimulationSensorAdapter
from infrastructure.adapters.sensors.vendor_stub import VendorStubSensorAdapter


def test_simulation_moisture_sensor_returns_reading():
    adapter = SimulationSensorAdapter()
    device_id = uuid4()

    reading = adapter.read(
        device_id=device_id,
        device_type="moisture_sensor",
    )

    assert reading.device_id == device_id
    assert 0.2 <= reading.value <= 0.6
    assert reading.unit == "vwc"
    assert reading.source == "simulation"
    assert reading.recorded_at.tzinfo is not None


def test_simulation_light_sensor_returns_reading():
    adapter = SimulationSensorAdapter()
    device_id = uuid4()

    reading = adapter.read(
        device_id=device_id,
        device_type="light_sensor",
    )

    assert reading.device_id == device_id
    assert 200 <= reading.value <= 2000
    assert reading.unit == "lux"
    assert reading.source == "simulation"
    assert reading.recorded_at.tzinfo is not None


def test_vendor_adapter_translates_payload():
    adapter = VendorStubSensorAdapter()
    device_id = uuid4()

    reading = adapter.translate(
        device_id=device_id,
        raw_payload={
            "measurement": 0.44,
            "measurement_unit": "vwc",
        },
    )

    assert reading.device_id == device_id
    assert reading.value == 0.44
    assert reading.unit == "vwc"
    assert reading.source == "vendor"
    assert reading.recorded_at.tzinfo is not None


def test_mqtt_adapter_translates_payload():
    adapter = MqttSensorAdapter()
    device_id = uuid4()

    reading = adapter.translate(
        device_id=device_id,
        payload={
            "value": 725,
            "unit": "lux",
        },
    )

    assert reading.device_id == device_id
    assert reading.value == 725
    assert reading.unit == "lux"
    assert reading.source == "mqtt"
    assert reading.recorded_at.tzinfo is not None


def test_mqtt_adapter_rejects_invalid_value():
    adapter = MqttSensorAdapter()

    with pytest.raises(ValueError):
        adapter.translate(
            device_id=uuid4(),
            payload={
                "value": "not-a-number",
                "unit": "lux",
            },
        )