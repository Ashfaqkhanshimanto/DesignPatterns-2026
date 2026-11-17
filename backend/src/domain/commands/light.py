
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from domain.actuators.ports import ActuatorPort


@dataclass
class SetLightLevelCommand:
    """Command for setting a greenhouse grow light level."""

    device_id: UUID
    payload: dict[str, object] = field(
        default_factory=lambda: {"level": 1}
    )

    command_type: ClassVar[str] = "set_light_level"

    # A running light stays running when its level changes.
    target_state: ClassVar[str | None] = None

    def execute(self, port: ActuatorPort) -> None:
        port.apply(
            device_id=self.device_id,
            command=self.command_type,
            payload=self.payload,
        )
