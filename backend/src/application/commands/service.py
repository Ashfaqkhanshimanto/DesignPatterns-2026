
from uuid import UUID

from sqlalchemy.orm import Session

from application.actuators.execution_service import (
    build_actuator_port,
)
from domain.actuators.context import ActuatorContext
from domain.commands.invoker import (
    CommandInvoker,
    UnknownCommandError,
)
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.command_log_repository import (
    CommandLogRepository,
)


class CommandDeviceNotFoundError(ValueError):
    """Device is missing or is not an actuator."""


def commands_allowed_for_device(
    context: ActuatorContext,
    device_type: str,
) -> list[str]:
    """Include device-specific commands without changing state transitions."""
    commands = context.allowed_commands.copy()

    if device_type == "grow_light" and context.state == "running":
        commands.append("set_light_level")

    return commands


class CommandService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._states = ActuatorStateRepository(db)
        self._logs = CommandLogRepository(db)
        self._invoker = CommandInvoker()
        self._port = build_actuator_port(db)

    def execute(
        self,
        command_type: str,
        device_id: UUID,
        payload: dict[str, object] | None = None,
    ):
        # 1. Device must exist and have actuator role.
        device = self._states.get_actuator(device_id)

        if device is None:
            raise CommandDeviceNotFoundError(
                f"Actuator {device_id} not found"
            )

        # 2. Unknown types must not create a log row.
        if not self._invoker.supports(command_type):
            raise UnknownCommandError(
                f"Unknown command type: {command_type}"
            )

        # Create a command, but do not execute it yet.
        command = self._invoker.create(
            command_type,
            device_id,
            payload,
        )

        saved_state = self._states.ensure_state(device_id)

        if saved_state is None:
            raise CommandDeviceNotFoundError(
                f"Actuator {device_id} not found"
            )

        context = ActuatorContext(
            device_id=device_id,
            state=saved_state,
        )

        allowed = commands_allowed_for_device(
            context,
            device.device_type,
        )

        # Commands must also match their device type.
        suitable_device = (
            command_type in {"start_pump", "stop_pump"}
            and device.device_type == "water_pump"
        ) or (
            command_type == "set_light_level"
            and device.device_type == "grow_light"
        )

        # 3. Rejected commands never reach the adapter.
        if command_type not in allowed or not suitable_device:
            return self._logs.add(
                command_type=command_type,
                device_id=device_id,
                payload=command.payload,
                status="rejected",
                error_message=(
                    f"Command '{command_type}' is not allowed "
                    f"for {device.device_type} in state '{context.state}'"
                ),
            )

        # 4. Run through the Phase 9 decorator stack.
        try:
            self._invoker.execute(command, self._port)
        except Exception as error:
            # The logging decorator already records the failed
            # execution attempt in actuator_execution_log.
            return self._logs.add(
                command_type=command_type,
                device_id=device_id,
                payload=command.payload,
                status="failed",
                error_message=str(error),
            )

        # 5. Update state only after a successful apply.
        target_state = command.target_state

        if target_state is not None and target_state != context.state:
            context.change_state(target_state)
            self._states.save_state(device_id, context.state)

        return self._logs.add(
            command_type=command_type,
            device_id=device_id,
            payload=command.payload,
            status="success",
            error_message=None,
        )

    def list_recent(self, limit: int = 50):
        return self._logs.list_recent(limit)
