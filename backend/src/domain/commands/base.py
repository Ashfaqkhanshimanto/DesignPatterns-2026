
from typing import Protocol
from uuid import UUID

from domain.actuators.ports import ActuatorPort


class Command(Protocol):
    """Interface shared by actuator commands."""

    device_id: UUID
    payload: dict[str, object]
    command_type: str
    target_state: str | None

    def execute(self, port: ActuatorPort) -> None:
        """Execute the command using the actuator port."""
        ...

