from datetime import datetime, timezone
from uuid import UUID

from domain.sensors.reading import Reading


class MqttSensorAdapter:
    """
    Translate an MQTT-style payload into a normalized Reading.

    Phase 5 does not connect to an MQTT broker.
    """

    def translate(
        self,
        device_id: UUID,
        payload: dict[str, object],
    ) -> Reading:
        try:
            raw_value = payload["value"]
            raw_unit = payload["unit"]
        except KeyError as error:
            raise ValueError(
                f"Invalid MQTT payload. Missing field: {error.args[0]}"
            ) from error

        if not isinstance(raw_value, (int, float)):
            raise ValueError("MQTT value must be numeric.")

        if not isinstance(raw_unit, str) or not raw_unit.strip():
            raise ValueError("MQTT unit is required.")

        return Reading(
            device_id=device_id,
            value=float(raw_value),
            unit=raw_unit.strip(),
            source="mqtt",
            recorded_at=datetime.now(timezone.utc),
        )