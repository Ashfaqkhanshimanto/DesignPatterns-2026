
from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import UUID

from sqlalchemy.orm import Session

from domain.actuators.ports import ActuatorPort
from infrastructure.persistence.models import ActuatorStateRow


class MaxRuntimeExceededError(Exception):
    """Raised when an actuator exceeds its maximum run time."""

    policy_name = "maxRunTime"

    def __init__(self) -> None:
        super().__init__("Max run time exceeded")


class MaxRuntimeActuatorDecorator:
    """Blocks commands when an actuator has run for 30+ minutes."""

    MAX_RUNTIME = timedelta(minutes=30)

    def __init__(
        self,
        wrapped: ActuatorPort,
        db: Session,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._wrapped = wrapped
        self._db = db
        self._clock = clock or (
            lambda: datetime.now(timezone.utc)
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict[str, object],
    ) -> None:
        state_row = self._db.get(
            ActuatorStateRow,
            device_id,
        )

        if state_row is not None and state_row.state == "running":
            running_since = state_row.updated_at
            current_time = self._clock()

            if current_time - running_since >= self.MAX_RUNTIME:
                raise MaxRuntimeExceededError()

        self._wrapped.apply(
            device_id,
            command,
            payload,
        )
