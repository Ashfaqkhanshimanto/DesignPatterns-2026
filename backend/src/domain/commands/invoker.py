
from typing import Type
from uuid import UUID

from domain.actuators.ports import ActuatorPort
from domain.commands.base import Command
from domain.commands.pump import (
    StartPumpCommand,
    StopPumpCommand,
)
from domain.commands.light import SetLightLevelCommand


class UnknownCommandError(ValueError):
    """Raised when a command type is not registered."""


class CommandInvoker:
    """Selects and executes commands using a registry."""

    def __init__(self) -> None:
        self._registry: dict[str, Type[Command]] = {
            "start_pump": StartPumpCommand,
            "stop_pump": StopPumpCommand,
            "set_light_level": SetLightLevelCommand,
        }

    def supports(self, command_type: str) -> bool:
        return command_type in self._registry

    def create(
        self,
        command_type: str,
        device_id: UUID,
        payload: dict[str, object] | None = None,
    ) -> Command:
        command_class = self._registry.get(command_type)

        if command_class is None:
            raise UnknownCommandError(
                f"Unknown command type: {command_type}"
            )

        # Each command class supplies its own default payload.
        if payload is None:
            return command_class(device_id=device_id)

        return command_class(
            device_id=device_id,
            payload=payload,
        )

    def execute(
        self,
        command: Command,
        port: ActuatorPort,
    ) -> None:
        command.execute(port)

    def invoke(
        self,
        command_type: str,
        device_id: UUID,
        payload: dict[str, object] | None,
        port: ActuatorPort,
    ) -> Command:
        command = self.create(
            command_type,
            device_id,
            payload,
        )

        self.execute(command, port)
        return command
