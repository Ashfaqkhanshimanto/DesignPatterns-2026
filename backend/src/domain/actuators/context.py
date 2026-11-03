
from dataclasses import dataclass
from uuid import UUID

from domain.actuators.state import (
    TRANSITIONS,
    allowed_commands,
    transition,
)


@dataclass
class ActuatorContext:
    device_id: UUID
    state: str = "idle"

    def __post_init__(self) -> None:
        if self.state not in TRANSITIONS:
            raise ValueError(
                f"Unknown actuator state: {self.state}"
            )

    @property
    def allowed_commands(self) -> list[str]:
        return allowed_commands(self.state)

    def change_state(self, target: str) -> None:
        # Only update the state if the transition is legal.
        new_state = transition(self.state, target)
        self.state = new_state
