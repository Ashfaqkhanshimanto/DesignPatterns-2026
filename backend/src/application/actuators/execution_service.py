
from uuid import UUID

from sqlalchemy.orm import Session

from domain.actuators.ports import ActuatorPort

from infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRuntimeActuatorDecorator,
)
from infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


def build_actuator_port(
    db: Session,
    repository: ExecutionLogRepository | None = None,
) -> ActuatorPort:
    """
    Build the decorated actuator port.

    Order:
    Logging -> Max Runtime -> Simulation
    """

    if repository is None:
        repository = ExecutionLogRepository(db)

    # Existing Phase 5 simulation adapter
    simulation: ActuatorPort = SimulationActuatorAdapter()

    # Phase 9 maximum runtime policy
    max_runtime: ActuatorPort = MaxRuntimeActuatorDecorator(
        wrapped=simulation,
        db=db,
    )

    # Outermost decorator records all attempts
    logging: ActuatorPort = LoggingActuatorDecorator(
        wrapped=max_runtime,
        repository=repository,
    )

    return logging


class ActuatorExecutionService:
    """Executes commands through the decorated actuator port."""

    def __init__(self, db: Session) -> None:
        self._repository = ExecutionLogRepository(db)

        self._port = build_actuator_port(
            db=db,
            repository=self._repository,
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict[str, object],
    ) -> None:
        self._port.apply(
            device_id=device_id,
            command=command,
            payload=payload,
        )

    def list_recent(
        self,
        limit: int = 20,
    ):
        return self._repository.list_recent(limit)
