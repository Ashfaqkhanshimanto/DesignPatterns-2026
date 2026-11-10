
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest

from infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRuntimeActuatorDecorator,
    MaxRuntimeExceededError,
)


def make_db(state="running", minutes_ago=0):
    db = Mock()

    state_row = Mock()
    state_row.state = state
    state_row.updated_at = (
        datetime(2026, 11, 10, 12, 0, tzinfo=timezone.utc)
        - timedelta(minutes=minutes_ago)
    )

    db.get.return_value = state_row

    return db


FIXED_NOW = datetime(
    2026, 11, 10, 12, 0, tzinfo=timezone.utc
)


def test_max_runtime_blocks_after_30_minutes():
    inner = Mock()
    db = make_db(minutes_ago=30)

    decorator = MaxRuntimeActuatorDecorator(
        wrapped=inner,
        db=db,
        clock=lambda: FIXED_NOW,
    )

    with pytest.raises(
        MaxRuntimeExceededError,
        match="Max run time exceeded",
    ):
        decorator.apply(uuid4(), "test_command", {})

    inner.apply.assert_not_called()


def test_max_runtime_allows_before_30_minutes():
    inner = Mock()
    db = make_db(minutes_ago=29)
    device_id = uuid4()

    decorator = MaxRuntimeActuatorDecorator(
        wrapped=inner,
        db=db,
        clock=lambda: FIXED_NOW,
    )

    decorator.apply(device_id, "test_command", {})

    inner.apply.assert_called_once_with(
        device_id,
        "test_command",
        {},
    )


def test_non_running_actuator_is_not_blocked():
    inner = Mock()
    db = make_db(state="idle", minutes_ago=60)
    device_id = uuid4()

    decorator = MaxRuntimeActuatorDecorator(
        wrapped=inner,
        db=db,
        clock=lambda: FIXED_NOW,
    )

    decorator.apply(device_id, "unknown_command", {})

    inner.apply.assert_called_once()


def test_logging_records_success():
    inner = Mock()
    repository = Mock()
    device_id = uuid4()

    decorator = LoggingActuatorDecorator(
        wrapped=inner,
        repository=repository,
    )

    decorator.apply(device_id, "test_command", {})

    inner.apply.assert_called_once()

    repository.add.assert_called_once_with(
        device_id=device_id,
        success=True,
        policy_applied=["logging"],
        message=None,
    )


def test_logging_records_blocked_attempt():
    inner = Mock()
    inner.apply.side_effect = MaxRuntimeExceededError()

    repository = Mock()
    device_id = uuid4()

    decorator = LoggingActuatorDecorator(
        wrapped=inner,
        repository=repository,
    )

    with pytest.raises(MaxRuntimeExceededError):
        decorator.apply(device_id, "test_command", {})

    repository.add.assert_called_once_with(
        device_id=device_id,
        success=False,
        policy_applied=["maxRunTime", "logging"],
        message="Max run time exceeded",
    )


def test_logging_records_other_adapter_errors():
    inner = Mock()
    inner.apply.side_effect = RuntimeError("Adapter failed")

    repository = Mock()
    device_id = uuid4()

    decorator = LoggingActuatorDecorator(
        wrapped=inner,
        repository=repository,
    )

    with pytest.raises(RuntimeError, match="Adapter failed"):
        decorator.apply(device_id, "test_command", {})

    repository.add.assert_called_once_with(
        device_id=device_id,
        success=False,
        policy_applied=["logging"],
        message="Adapter failed",
    )
