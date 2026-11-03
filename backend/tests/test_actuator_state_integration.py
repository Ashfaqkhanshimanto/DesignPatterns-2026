
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    ActuatorStateRow,
    DeviceRow,
)
from infrastructure.persistence.session import engine, get_db
from main import app


@pytest.fixture
def db():
    # Keep test changes separate from real greenhouse data.
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


@pytest.fixture
def actuator_id(db):
    device = DeviceRow(
        id=uuid4(),
        device_type="water_pump",
        role="actuator",
        device_family="simulation",
        display_name="Integration Test Water Pump",
        default_config={"protocol": "simulation"},
    )

    db.add(device)
    db.flush()

    return device.id


def test_new_actuator_receives_idle_state(
    client,
    db,
    actuator_id,
):
    response = client.get(
        f"/api/devices/{actuator_id}/state"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["state"] == "idle"
    assert "start_pump" in data["allowed_commands"]

    db.expire_all()

    saved = db.get(ActuatorStateRow, actuator_id)

    assert saved is not None
    assert saved.state == "idle"


def test_legal_transition_is_saved(
    client,
    db,
    actuator_id,
):
    response = client.post(
        f"/api/devices/{actuator_id}/transition",
        json={"target": "running"},
    )

    assert response.status_code == 200
    assert response.json()["state"] == "running"

    # Check the actual database, not only the API response.
    db.expire_all()

    saved = db.get(ActuatorStateRow, actuator_id)

    assert saved is not None
    assert saved.state == "running"

    # A new GET must return the persisted state.
    response = client.get(
        f"/api/devices/{actuator_id}/state"
    )

    assert response.status_code == 200
    assert response.json()["state"] == "running"


def test_illegal_transition_does_not_change_database(
    client,
    db,
    actuator_id,
):
    # First perform a legal transition.
    start_response = client.post(
        f"/api/devices/{actuator_id}/transition",
        json={"target": "running"},
    )

    assert start_response.status_code == 200

    # running -> maintenance is illegal.
    response = client.post(
        f"/api/devices/{actuator_id}/transition",
        json={"target": "maintenance"},
    )

    assert response.status_code == 409

    db.expire_all()

    saved = db.get(ActuatorStateRow, actuator_id)

    assert saved is not None
    assert saved.state == "running"

    # The API must also report the unchanged state.
    check_response = client.get(
        f"/api/devices/{actuator_id}/state"
    )

    assert check_response.status_code == 200
    assert check_response.json()["state"] == "running"


def test_missing_actuator_returns_404(client):
    missing_id = uuid4()

    response = client.get(
        f"/api/devices/{missing_id}/state"
    )

    assert response.status_code == 404
