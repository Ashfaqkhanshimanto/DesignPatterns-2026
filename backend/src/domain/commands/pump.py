
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from domain.actuators.ports import ActuatorPort


@dataclass
class StartPumpCommand:
    """Command for starting a greenhouse water pump."""

    device_id: UUID
    payload: dict[str, object] = field(default_factory=dict)

    command_type: ClassVar[str] = "start_pump"
    target_state: ClassVar[str] = "running"

    def execute(self, port: ActuatorPort) -> None:
        port.apply(
            device_id=self.device_id,
            command=self.command_type,
            payload=self.payload,
        )


@dataclass
class StopPumpCommand:
    """Command for stopping a greenhouse water pump."""

    device_id: UUID
    payload: dict[str, object] = field(default_factory=dict)

    command_type: ClassVar[str] = "stop_pump"
    target_state: ClassVar[str] = "idle"

    def execute(self, port: ActuatorPort) -> None:
        port.apply(
            device_id=self.device_id,
            command=self.command_type,
            payload=self.payload,
        )
