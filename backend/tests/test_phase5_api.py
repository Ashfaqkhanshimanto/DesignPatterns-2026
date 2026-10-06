from uuid import uuid4

from fastapi.testclient import TestClient

from domain.devices.entity import Device
from infrastructure.persistence.session import get_db
from interfaces.api.devices import DeviceRepository
from main import app


class FakeDb:
    pass


def override_get_db():
    yield FakeDb()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def make_device(device_id=None):
    return Device(
        id=device_id or uuid4(),
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


def test_sampling_endpoint_updates_settings(monkeypatch):
    device = make_device()

    def fake_update_sampling(
        self,
        device_id,
        sampling_interval_seconds,
        tracking_enabled,
    ):
        return Device(
            id=device_id,
            device_type=device.device_type,
            role=device.role,
            device_family=device.device_family,
            display_name=device.display_name,
            default_config=device.default_config,
            sampling_interval_seconds=(
                sampling_interval_seconds
            ),
            tracking_enabled=tracking_enabled,
        )

    monkeypatch.setattr(
        DeviceRepository,
        "update_sampling",
        fake_update_sampling,
    )

    response = client.patch(
        f"/api/devices/{device.id}/sampling",
        json={
            "sampling_interval_seconds": 120,
            "tracking_enabled": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(device.id)
    assert data["sampling_interval_seconds"] == 120
    assert data["tracking_enabled"] is False


def test_sampling_endpoint_rejects_interval_below_five():
    device_id = uuid4()

    response = client.patch(
        f"/api/devices/{device_id}/sampling",
        json={
            "sampling_interval_seconds": 4,
            "tracking_enabled": True,
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"][0]["loc"] == [
        "body",
        "sampling_interval_seconds",
    ]


def test_sampling_endpoint_returns_404_for_missing_device(
    monkeypatch,
):
    def fake_update_sampling(
        self,
        device_id,
        sampling_interval_seconds,
        tracking_enabled,
    ):
        return None

    monkeypatch.setattr(
        DeviceRepository,
        "update_sampling",
        fake_update_sampling,
    )

    device_id = uuid4()

    response = client.patch(
        f"/api/devices/{device_id}/sampling",
        json={
            "sampling_interval_seconds": 300,
            "tracking_enabled": True,
        },
    )

    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]