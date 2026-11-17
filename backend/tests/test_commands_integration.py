
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    ActuatorExecutionLogRow,
    ActuatorStateRow,
    CommandLogRow,
    DeviceRow,
)
from infrastructure.persistence.session import engine, get_db
from main import app


@pytest.fixture
def db():
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
def pump_id(db):
    device = DeviceRow(
        id=uuid4(),
        device_type="water_pump",
        role="actuator",
        device_family="simulation",
        display_name="Command Test Pump",
        default_config={"protocol": "simulation"},
    )

    db.add(device)
    db.flush()

    return device.id


def test_start_pump_changes_state_and_logs_success(
    client, db, pump_id
):
    response = client.post(
        "/api/commands",
        json={
            "command_type": "start_pump",
            "device_id": str(pump_id),
            "payload": {},
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    db.expire_all()

    state = db.get(ActuatorStateRow, pump_id)

    assert state is not None
    assert state.state == "running"

    logs = db.scalars(
        select(CommandLogRow).where(
            CommandLogRow.device_id == pump_id
        )
    ).all()

    assert len(logs) == 1
    assert logs[0].status == "success"

    executions = db.scalars(
        select(ActuatorExecutionLogRow).where(
            ActuatorExecutionLogRow.device_id == pump_id
        )
    ).all()

    assert len(executions) == 1
    assert executions[0].success is True


def test_rejected_command_keeps_state_unchanged(
    client, db, pump_id
):
    # First start the pump successfully.
    start = client.post(
        "/api/commands",
        json={
            "command_type": "start_pump",
            "device_id": str(pump_id),
        },
    )

    assert start.status_code == 200

    # Starting an already-running pump is illegal.
    response = client.post(
        "/api/commands",
        json={
            "command_type": "start_pump",
            "device_id": str(pump_id),
        },
    )

    assert response.status_code == 409
    assert response.json()["status"] == "rejected"

    db.expire_all()

    state = db.get(ActuatorStateRow, pump_id)
    assert state.state == "running"

    logs = db.scalars(
        select(CommandLogRow).where(
            CommandLogRow.device_id == pump_id
        )
    ).all()

    assert len(logs) == 2
    assert sorted(log.status for log in logs) == [
        "rejected",
        "success",
    ]

    # Rejection does not reach the decorated port.
    executions = db.scalars(
        select(ActuatorExecutionLogRow).where(
            ActuatorExecutionLogRow.device_id == pump_id
        )
    ).all()

    assert len(executions) == 1


def test_max_runtime_failure_keeps_state_and_logs(
    client, db, pump_id
):
    state = ActuatorStateRow(
        device_id=pump_id,
        state="running",
        updated_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=31)
        ),
    )

    db.add(state)
    db.flush()

    response = client.post(
        "/api/commands",
        json={
            "command_type": "stop_pump",
            "device_id": str(pump_id),
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["error_message"] == (
        "Max run time exceeded"
    )

    db.expire_all()

    saved_state = db.get(ActuatorStateRow, pump_id)
    assert saved_state.state == "running"

    command_logs = db.scalars(
        select(CommandLogRow).where(
            CommandLogRow.device_id == pump_id
        )
    ).all()

    assert len(command_logs) == 1
    assert command_logs[0].status == "failed"

    executions = db.scalars(
        select(ActuatorExecutionLogRow).where(
            ActuatorExecutionLogRow.device_id == pump_id
        )
    ).all()

    assert len(executions) == 1
    assert executions[0].success is False
    assert executions[0].policy_applied == [
        "maxRunTime",
        "logging",
    ]


def test_unknown_command_writes_no_log(
    client, db, pump_id
):
    response = client.post(
        "/api/commands",
        json={
            "command_type": "unknown_command",
            "device_id": str(pump_id),
        },
    )

    assert response.status_code == 400

    logs = db.scalars(
        select(CommandLogRow).where(
            CommandLogRow.device_id == pump_id
        )
    ).all()

    assert len(logs) == 0


def test_missing_device_returns_404(client):
    response = client.post(
        "/api/commands",
        json={
            "command_type": "start_pump",
            "device_id": str(uuid4()),
        },
    )

    assert response.status_code == 404


def test_command_history_returns_newest_first(
    client, pump_id
):
    first = client.post(
        "/api/commands",
        json={
            "command_type": "start_pump",
            "device_id": str(pump_id),
        },
    )

    assert first.status_code == 200

    second = client.post(
        "/api/commands",
        json={
            "command_type": "stop_pump",
            "device_id": str(pump_id),
        },
    )

    assert second.status_code == 200

    history = client.get("/api/commands?limit=200")

    assert history.status_code == 200

    rows = history.json()

    first_id = first.json()["id"]
    second_id = second.json()["id"]

    ids = [row["id"] for row in rows]

    assert ids.index(second_id) < ids.index(first_id)
