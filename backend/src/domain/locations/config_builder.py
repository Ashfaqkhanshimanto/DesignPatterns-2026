from domain.locations.entity import Location, LocationConfig, Zone
from domain.locations.errors import ConfigurationError


def validate_zone(
    name: str,
    moisture_threshold_low: float,
    moisture_threshold_high: float,
) -> None:
    """Validate the rules that every zone must follow."""

    if not name or not name.strip():
        raise ConfigurationError("Zone name is required.")

    if not 0.0 <= moisture_threshold_low <= 1.0:
        raise ConfigurationError(
            "Moisture threshold low must be between 0.0 and 1.0."
        )

    if not 0.0 <= moisture_threshold_high <= 1.0:
        raise ConfigurationError(
            "Moisture threshold high must be between 0.0 and 1.0."
        )

    if moisture_threshold_low >= moisture_threshold_high:
        raise ConfigurationError(
            "Moisture threshold low must be less than high."
        )


class LocationConfigBuilder:
    def __init__(self) -> None:
        self._location_name: str | None = None
        self._zones: list[Zone] = []

    def set_location_name(
        self,
        name: str,
    ) -> "LocationConfigBuilder":
        self._location_name = name
        return self

    def add_zone(
        self,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict | None = None,
    ) -> "LocationConfigBuilder":
        zone = Zone(
            name=name,
            moisture_threshold_low=moisture_threshold_low,
            moisture_threshold_high=moisture_threshold_high,
            schedule=schedule or {},
        )

        self._zones.append(zone)
        return self

    def build(self) -> LocationConfig:
        if not self._location_name or not self._location_name.strip():
            raise ConfigurationError("Location name is required.")

        if not self._zones:
            raise ConfigurationError("At least one zone is required.")

        seen_names: set[str] = set()

        for zone in self._zones:
            validate_zone(
                zone.name,
                zone.moisture_threshold_low,
                zone.moisture_threshold_high,
            )

            normalized_name = zone.name.strip().casefold()

            if normalized_name in seen_names:
                raise ConfigurationError(
                    "Zone names must be unique within a location."
                )

            seen_names.add(normalized_name)

        location = Location(
            name=self._location_name.strip(),
            zones=tuple(self._zones),
        )

        return LocationConfig(location=location)