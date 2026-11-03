
from uuid import uuid4

import pytest

from domain.actuators.context import ActuatorContext
from domain.actuators.state import (
    IllegalTransitionError,
    allowed_commands,
    transition,
)


def test_idle_to_running():
    assert transition("idle", "running") == "running"


def test_running_to_idle():
    assert transition("running", "idle") == "idle"


def test_running_to_error():
    assert transition("running", "error") == "error"


def test_error_to_idle():
    assert transition("error", "idle") == "idle"


def test_idle_allowed_commands():
    commands = allowed_commands("idle")

    assert "start_pump" in commands
    assert "turn_off" in commands
    assert "report_error" in commands


def test_running_allowed_commands():
    commands = allowed_commands("running")

    assert commands == ["stop_pump", "report_error"]


def test_illegal_transition():
    with pytest.raises(IllegalTransitionError):
        transition("running", "maintenance")


def test_illegal_transition_keeps_state():
    actuator = ActuatorContext(
        device_id=uuid4(),
        state="running",
    )

    with pytest.raises(IllegalTransitionError):
        actuator.change_state("maintenance")

    assert actuator.state == "running"


def test_context_changes_state():
    actuator = ActuatorContext(
        device_id=uuid4(),
    )

    assert actuator.state == "idle"

    actuator.change_state("running")

    assert actuator.state == "running"
    assert actuator.allowed_commands == [
        "stop_pump",
        "report_error",
    ]


def test_unknown_state():
    with pytest.raises(ValueError):
        allowed_commands("unknown")
