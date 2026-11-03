
from uuid import UUID

from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    ActuatorStateRow,
    DeviceRow,
)


class ActuatorStateRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_actuator(self, device_id: UUID):
        device = self._db.get(DeviceRow, device_id)

        if device is None or device.role != "actuator":
            return None

        return device

    def get_state(self, device_id: UUID) -> str | None:
        actuator = self.get_actuator(device_id)

        if actuator is None:
            return None

        state_row = self._db.get(
            ActuatorStateRow,
            device_id,
        )

        if state_row is None:
            return None

        return state_row.state

    def ensure_state(self, device_id: UUID) -> str | None:
        # Only actuators can have lifecycle states.
        actuator = self.get_actuator(device_id)

        if actuator is None:
            return None

        state_row = self._db.get(
            ActuatorStateRow,
            device_id,
        )

        if state_row is None:
            state_row = ActuatorStateRow(
                device_id=device_id,
                state="idle",
            )

            self._db.add(state_row)
            self._db.commit()

        return state_row.state

    def save_state(
        self,
        device_id: UUID,
        new_state: str,
    ) -> None:
        state_row = self._db.get(
            ActuatorStateRow,
            device_id,
        )

        if state_row is None:
            raise ValueError(
                f"No state record for actuator {device_id}"
            )

        state_row.state = new_state

        self._db.commit()
