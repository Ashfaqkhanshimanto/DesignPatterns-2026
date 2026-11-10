
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    ActuatorExecutionLogRow,
    ActuatorStateRow,
    DeviceRow,
)
from infrastructure.persistence.session import engine, get_db
from main import app


@pytest.fixture
def db():
    # All test changes are rolled back afterward.
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
        display_name="Phase 9 Test Pump",
        default_config={"protocol": "simulation"},
    )

    db.add(device)
    db.flush()

    return device.id


def test_successful_apply_inserts_execution_log(
    client,
    db,
    actuator_id,
):
    response = client.post(
        "/api/actuators/apply",
        json={
            "device_id": str(actuator_id),
            "command": "unknown_test_command",
            "payload": {},
        },
    )

    assert response.status_code == 200

    # Verify the execution was actually saved.
    db.expire_all()

    rows = db.scalars(
        select(ActuatorExecutionLogRow).where(
            ActuatorExecutionLogRow.device_id == actuator_id
        )
    ).all()

    assert len(rows) == 1
    assert rows[0].success is True
    assert rows[0].policy_applied == ["logging"]
    assert rows[0].message is None


def test_blocked_apply_inserts_failed_execution_log(
    client,
    db,
    actuator_id,
):
    state = ActuatorStateRow(
        device_id=actuator_id,
        state="running",
        updated_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=31)
        ),
    )

    db.add(state)
    db.flush()

    response = client.post(
        "/api/actuators/apply",
        json={
            "device_id": str(actuator_id),
            "command": "test_command",
            "payload": {},
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Max run time exceeded"
    )

    db.expire_all()

    rows = db.scalars(
        select(ActuatorExecutionLogRow).where(
            ActuatorExecutionLogRow.device_id == actuator_id
        )
    ).all()

    assert len(rows) == 1
    assert rows[0].success is False
    assert rows[0].policy_applied == [
        "maxRunTime",
        "logging",
    ]
    assert rows[0].message == "Max run time exceeded"

    # The policy must not change the lifecycle state.
    saved_state = db.get(ActuatorStateRow, actuator_id)

    assert saved_state.state == "running"


def test_execution_endpoint_returns_saved_rows(
    client,
    db,
    actuator_id,
):
    apply_response = client.post(
        "/api/actuators/apply",
        json={
            "device_id": str(actuator_id),
            "command": "test_command",
            "payload": {},
        },
    )

    assert apply_response.status_code == 200

    response = client.get(
        "/api/actuators/executions?limit=20"
    )

    assert response.status_code == 200

    records = response.json()

    matching = [
        record
        for record in records
        if record["device_id"] == str(actuator_id)
    ]

    assert len(matching) == 1
    assert matching[0]["success"] is True
    assert matching[0]["policy_applied"] == ["logging"]
    assert matching[0]["message"] is None
    assert matching[0]["id"]
    assert matching[0]["created_at"]


def test_missing_actuator_returns_404(client):
    response = client.post(
        "/api/actuators/apply",
        json={
            "device_id": str(uuid4()),
            "command": "test_command",
            "payload": {},
        },
    )

    assert response.status_code == 404
