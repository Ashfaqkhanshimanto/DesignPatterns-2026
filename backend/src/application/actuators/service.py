
from uuid import UUID

from domain.actuators.context import ActuatorContext
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)


class ActuatorNotFoundError(Exception):
    """Raised when a device is missing or is not an actuator."""


class ActuatorStateService:
    def __init__(
        self,
        repository: ActuatorStateRepository,
    ) -> None:
        self._repository = repository

    def get_state(self, device_id: UUID) -> ActuatorContext:
        actuator = self._repository.get_actuator(device_id)

        if actuator is None:
            raise ActuatorNotFoundError(
                f"Actuator {device_id} was not found."
            )

        current_state = self._repository.ensure_state(
            device_id
        )

        if current_state is None:
            raise ActuatorNotFoundError(
                f"Actuator {device_id} was not found."
            )

        return ActuatorContext(
            device_id=device_id,
            state=current_state,
        )

    def transition(
        self,
        device_id: UUID,
        target: str,
    ) -> ActuatorContext:
        # Load the currently stored state.
        context = self.get_state(device_id)

        # The domain checks whether this change is legal.
        # Illegal transitions raise an error here.
        context.change_state(target)

        # Save only after the transition is accepted.
        self._repository.save_state(
            device_id,
            context.state,
        )

        return context
