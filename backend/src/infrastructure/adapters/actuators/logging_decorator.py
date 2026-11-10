
from uuid import UUID

from domain.actuators.ports import ActuatorPort
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRuntimeExceededError,
)
from infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


class LoggingActuatorDecorator:
    """Records every actuator attempt in PostgreSQL."""

    def __init__(
        self,
        wrapped: ActuatorPort,
        repository: ExecutionLogRepository,
    ) -> None:
        self._wrapped = wrapped
        self._repository = repository

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict[str, object],
    ) -> None:
        try:
            self._wrapped.apply(
                device_id,
                command,
                payload,
            )

        except MaxRuntimeExceededError as error:
            self._repository.add(
                device_id=device_id,
                success=False,
                policy_applied=["maxRunTime", "logging"],
                message=str(error),
            )
            raise

        except Exception as error:
            self._repository.add(
                device_id=device_id,
                success=False,
                policy_applied=["logging"],
                message=str(error),
            )
            raise

        else:
            self._repository.add(
                device_id=device_id,
                success=True,
                policy_applied=["logging"],
                message=None,
            )
