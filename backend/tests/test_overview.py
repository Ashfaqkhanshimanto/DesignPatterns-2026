
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from application.automation.service import AutomationService
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from infrastructure.persistence.models import (
    AutomationRuleRow,
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)
from infrastructure.persistence.session import engine, get_db
from main import app


@pytest.fixture
def db():
    # Roll back test data so the real greenhouse stays unchanged.
    with engine.connect() as connection:
        transaction = connection.begin()

        session = Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )

        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def client(db):
    previous_override = app.dependency_overrides.get(get_db)

    def test_get_db():
        yield db

    app.dependency_overrides[get_db] = test_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


def test_overview_returns_404_for_missing_location(client):
    response = client.get(
        f"/api/locations/{uuid4()}/overview"
    )

    assert response.status_code == 404


def test_overview_without_saved_strategy(client, db):
    location = LocationRow(
        id=uuid4(),
        name="No Strategy Greenhouse",
    )

    db.add(location)
    db.flush()

    response = client.get(
        f"/api/locations/{location.id}/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["strategy_key"] is None
    assert data["last_recommendation"] is None
    assert data["device_counts"] == {
        "sensor": 0,
        "actuator": 0,
    }
    assert data["zones"] == []


def test_overview_returns_strategy_and_readings(client, db):
    location = LocationRow(
        id=uuid4(),
        name="Test Greenhouse",
    )

    tomato_zone = ZoneRow(
        id=uuid4(),
        location_id=location.id,
        name="Tomato Zone",
        moisture_threshold_low=0.30,
        moisture_threshold_high=0.70,
    )

    empty_zone = ZoneRow(
        id=uuid4(),
        location_id=location.id,
        name="Empty Zone",
        moisture_threshold_low=0.25,
        moisture_threshold_high=0.60,
    )

    sensor = DeviceRow(
        id=uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Assigned Moisture Sensor",
        zone_id=tomato_zone.id,
        location_id=location.id,
        tracking_enabled=True,
        sampling_interval_seconds=120,
    )

    actuator = DeviceRow(
        id=uuid4(),
        device_type="water_pump",
        role="actuator",
        device_family="simulation",
        display_name="Assigned Water Pump",
        zone_id=tomato_zone.id,
        location_id=location.id,
    )

    unassigned_sensor = DeviceRow(
        id=uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Unassigned Sensor",
        location_id=location.id,
        zone_id=None,
    )

    rule = AutomationRuleRow(
        id=uuid4(),
        location_id=location.id,
        strategy_key="aggressive",
    )

    earlier_time = datetime.now(timezone.utc) - timedelta(
        hours=2
    )
    later_time = earlier_time + timedelta(hours=1)

    old_reading = ReadingRow(
        id=uuid4(),
        device_id=sensor.id,
        value=0.60,
        unit="vwc",
        source="simulation",
        recorded_at=earlier_time,
    )

    new_reading = ReadingRow(
        id=uuid4(),
        device_id=sensor.id,
        value=0.35,
        unit="vwc",
        source="manual",
        recorded_at=later_time,
    )

    # Insert the location first.
    db.add(location)
    db.flush()

    # Insert zones before assigned devices.
    db.add_all([tomato_zone, empty_zone])
    db.flush()

    # Insert devices before sensor readings.
    db.add_all([sensor, actuator, unassigned_sensor])
    db.flush()

    # Foreign key relationships now exist.
    db.add_all([rule, old_reading, new_reading])
    db.flush()

    response = client.get(
        f"/api/locations/{location.id}/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["location"]["name"] == "Test Greenhouse"
    assert data["device_counts"] == {
        "sensor": 1,
        "actuator": 1,
    }

    assert len(data["zones"]) == 2

    zones = {
        zone["name"]: zone
        for zone in data["zones"]
    }

    assert zones["Empty Zone"]["devices"] == []
    assert zones["Empty Zone"]["latest_readings"] == []

    tomato = zones["Tomato Zone"]

    assert len(tomato["devices"]) == 2

    device_ids = {
        device["id"]
        for device in tomato["devices"]
    }

    assert str(sensor.id) in device_ids
    assert str(actuator.id) in device_ids
    assert str(unassigned_sensor.id) not in device_ids

    # Only the newest sensor reading should be returned.
    assert len(tomato["latest_readings"]) == 1

    reading = tomato["latest_readings"][0]

    assert reading["device_id"] == str(sensor.id)
    assert reading["value"] == pytest.approx(0.35)
    assert reading["unit"] == "vwc"
    assert reading["tracking_enabled"] is True
    assert reading["sampling_interval_seconds"] == 120

    assert data["strategy_key"] == "aggressive"

    # The overview must agree with Phase 6 evaluation.
    automation_service = AutomationService(
        AutomationRepository(db)
    )

    evaluation = automation_service.evaluate(location.id)

    assert data["last_recommendation"] == {
        "action": evaluation.action,
        "reason": evaluation.reason,
    }

    assert evaluation.action == "irrigate"
