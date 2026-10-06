import random
from datetime import datetime, timezone
from uuid import UUID

from domain.sensors.reading import Reading


class SimulationSensorAdapter:
    """Generate simulated sensor readings in code."""

    def read(
        self,
        device_id: UUID,
        device_type: str,
    ) -> Reading:
        normalized_type = device_type.strip().lower()

        if "moisture" in normalized_type:
            value = random.uniform(0.2, 0.6)
            unit = "vwc"

        elif "light" in normalized_type:
            value = random.uniform(200.0, 2000.0)
            unit = "lux"

        else:
            raise ValueError(
                f"Unsupported simulation sensor type: {device_type}"
            )

        return Reading(
            device_id=device_id,
            value=value,
            unit=unit,
            source="simulation",
            recorded_at=datetime.now(timezone.utc),
        )