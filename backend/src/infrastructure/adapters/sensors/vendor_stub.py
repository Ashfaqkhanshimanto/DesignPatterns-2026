from datetime import datetime, timezone
from uuid import UUID

from domain.sensors.reading import Reading


class VendorStubSensorAdapter:
    """
    Adapter for a mocked vendor sensor.

    The vendor uses a different raw payload shape.
    This adapter translates that payload into our domain Reading.
    """

    def translate(
        self,
        device_id: UUID,
        raw_payload: dict[str, object],
    ) -> Reading:
        try:
            raw_value = raw_payload["measurement"]
            raw_unit = raw_payload["measurement_unit"]
        except KeyError as error:
            raise ValueError(
                f"Invalid vendor payload. Missing field: {error.args[0]}"
            ) from error

        if not isinstance(raw_value, (int, float)):
            raise ValueError("Vendor measurement must be numeric.")

        if not isinstance(raw_unit, str) or not raw_unit.strip():
            raise ValueError("Vendor measurement unit is required.")

        return Reading(
            device_id=device_id,
            value=float(raw_value),
            unit=raw_unit.strip(),
            source="vendor",
            recorded_at=datetime.now(timezone.utc),
        )

    def read(
        self,
        device_id: UUID,
        device_type: str,
    ) -> Reading:
        """
        Mock a vendor SDK response and translate it.

        No real hardware or vendor SDK is used in Phase 5.
        """

        normalized_type = device_type.strip().lower()

        if "moisture" in normalized_type:
            raw_payload: dict[str, object] = {
                "measurement": 0.42,
                "measurement_unit": "vwc",
            }
        elif "light" in normalized_type:
            raw_payload = {
                "measurement": 850.0,
                "measurement_unit": "lux",
            }
        else:
            raise ValueError(
                f"Unsupported vendor sensor type: {device_type}"
            )

        return self.translate(
            device_id=device_id,
            raw_payload=raw_payload,
        )