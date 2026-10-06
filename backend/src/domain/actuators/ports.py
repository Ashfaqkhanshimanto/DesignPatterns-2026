from typing import Protocol
from uuid import UUID


class ActuatorPort(Protocol):
    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict[str, object],
    ) -> None:
        """Apply a command to an actuator."""
        ...