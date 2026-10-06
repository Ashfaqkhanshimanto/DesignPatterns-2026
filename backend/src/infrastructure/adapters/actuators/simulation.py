from uuid import UUID


class SimulationActuatorAdapter:
    """
    Simulation-only actuator adapter.

    It records actuator commands in memory.
    No GPIO or real hardware is used.
    """

    def __init__(self) -> None:
        self.applied_commands: list[dict[str, object]] = []

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict[str, object],
    ) -> None:
        self.applied_commands.append(
            {
                "device_id": device_id,
                "command": command,
                "payload": payload,
            }
        )