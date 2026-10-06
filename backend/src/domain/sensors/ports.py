from typing import Protocol
from uuid import UUID

from domain.sensors.reading import Reading


class SensorPort(Protocol):
    def read(
        self,
        device_id: UUID,
        device_type: str,
    ) -> Reading:
        """Read a sensor and return a normalized Reading."""
        ...