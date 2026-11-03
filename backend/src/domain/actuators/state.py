
class IllegalTransitionError(ValueError):
    """Raised when an actuator cannot change to a target state."""


# Legal transitions between actuator states.
TRANSITIONS = {
    "idle": {
        "running": "start_pump",
        "off": "turn_off",
        "error": "report_error",
        "maintenance": "enter_maintenance",
    },
    "running": {
        "idle": "stop_pump",
        "error": "report_error",
    },
    "off": {
        "idle": "turn_on",
        "error": "report_error",
    },
    "error": {
        "idle": "reset",
    },
    "maintenance": {
        "idle": "finish_maintenance",
        "error": "report_error",
    },
}


def allowed_commands(state: str) -> list[str]:
    if state not in TRANSITIONS:
        raise ValueError(f"Unknown actuator state: {state}")

    return list(TRANSITIONS[state].values())


def transition(current_state: str, target_state: str) -> str:
    if current_state not in TRANSITIONS:
        raise ValueError(f"Unknown actuator state: {current_state}")

    if target_state not in TRANSITIONS[current_state]:
        raise IllegalTransitionError(
            f"Cannot transition from '{current_state}' "
            f"to '{target_state}'. "
            f"Allowed commands: {allowed_commands(current_state)}"
        )

    return target_state
