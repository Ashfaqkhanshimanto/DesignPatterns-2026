from uuid import UUID

from application.locations.dto import (
    LocationConfigCreateRequest,
    LocationConfigRead,
    LocationRead,
    ZoneCreateRequest,
    ZoneRead,
    ZoneUpdateRequest,
)
from application.locations.mappers import location_config_to_read
from domain.locations.config_builder import (
    LocationConfigBuilder,
    validate_zone,
)
from domain.locations.entity import Zone
from domain.locations.errors import ConfigurationError
from infrastructure.persistence.location_repository import LocationRepository


class LocationNotFoundError(ValueError):
    """Raised when a requested location does not exist."""

    pass


class ZoneNotFoundError(ValueError):
    """Raised when a requested zone does not exist."""

    pass


class LastZoneDeletionError(ValueError):
    """Raised when trying to delete the final zone of a location."""

    pass


class LocationConfigService:
    def __init__(
        self,
        repository: LocationRepository,
    ) -> None:
        self._repository = repository

    def create_config(
        self,
        request: LocationConfigCreateRequest,
    ) -> LocationConfigRead:
        builder = LocationConfigBuilder()

        builder.set_location_name(
            request.location_name
        )

        for zone in request.zones:
            builder.add_zone(
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )

        config = builder.build()

        saved_config = self._repository.save_config(
            config
        )

        return location_config_to_read(
            saved_config
        )

    def get_config(
        self,
        location_id: UUID,
    ) -> LocationConfigRead:
        config = self._repository.get_config(
            location_id
        )

        if config is None:
            raise LocationNotFoundError(
                f"Location {location_id} was not found."
            )

        return location_config_to_read(
            config
        )

    def list_locations(
        self,
    ) -> list[LocationRead]:
        locations = self._repository.list_locations()

        return [
            LocationRead(
                id=location.id,
                name=location.name,
            )
            for location in locations
            if location.id is not None
        ]

    def delete_location(
        self,
        location_id: UUID,
    ) -> None:
        deleted = self._repository.delete_location(
            location_id
        )

        if not deleted:
            raise LocationNotFoundError(
                f"Location {location_id} was not found."
            )

    def add_zone(
        self,
        location_id: UUID,
        request: ZoneCreateRequest,
    ) -> ZoneRead:
        validate_zone(
            request.name,
            request.moisture_threshold_low,
            request.moisture_threshold_high,
        )

        self._ensure_unique_zone_name(
            location_id=location_id,
            name=request.name,
        )

        zone = Zone(
            name=request.name.strip(),
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
            schedule=request.schedule,
        )

        saved_zone = self._repository.add_zone(
            location_id,
            zone,
        )

        if saved_zone is None:
            raise LocationNotFoundError(
                f"Location {location_id} was not found."
            )

        return self._zone_to_read(
            location_id,
            saved_zone,
        )

    def update_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
        request: ZoneUpdateRequest,
    ) -> ZoneRead:
        validate_zone(
            request.name,
            request.moisture_threshold_low,
            request.moisture_threshold_high,
        )

        self._ensure_unique_zone_name(
            location_id=location_id,
            name=request.name,
            excluded_zone_id=zone_id,
        )

        zone = Zone(
            id=zone_id,
            name=request.name.strip(),
            moisture_threshold_low=request.moisture_threshold_low,
            moisture_threshold_high=request.moisture_threshold_high,
            schedule=request.schedule,
        )

        saved_zone = self._repository.update_zone(
            location_id,
            zone_id,
            zone,
        )

        if saved_zone is None:
            raise ZoneNotFoundError(
                f"Zone {zone_id} was not found in location {location_id}."
            )

        return self._zone_to_read(
            location_id,
            saved_zone,
        )

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> None:
        result = self._repository.delete_zone(
            location_id,
            zone_id,
        )

        if result == "location_not_found":
            raise LocationNotFoundError(
                f"Location {location_id} was not found."
            )

        if result == "zone_not_found":
            raise ZoneNotFoundError(
                f"Zone {zone_id} was not found in location {location_id}."
            )

        if result == "last_zone":
            raise LastZoneDeletionError(
                "A location must contain at least one zone."
            )

    def _ensure_unique_zone_name(
        self,
        location_id: UUID,
        name: str,
        excluded_zone_id: UUID | None = None,
    ) -> None:
        config = self._repository.get_config(
            location_id
        )

        if config is None:
            raise LocationNotFoundError(
                f"Location {location_id} was not found."
            )

        normalized_name = name.strip().casefold()

        for existing_zone in config.location.zones:
            if (
                excluded_zone_id is not None
                and existing_zone.id == excluded_zone_id
            ):
                continue

            if existing_zone.name.strip().casefold() == normalized_name:
                raise ConfigurationError(
                    "Zone names must be unique within a location."
                )

    @staticmethod
    def _zone_to_read(
        location_id: UUID,
        zone: Zone,
    ) -> ZoneRead:
        if zone.id is None:
            raise ValueError(
                "Cannot map an unsaved zone to a read DTO."
            )

        return ZoneRead(
            id=zone.id,
            location_id=location_id,
            name=zone.name,
            moisture_threshold_low=zone.moisture_threshold_low,
            moisture_threshold_high=zone.moisture_threshold_high,
            schedule=zone.schedule,
        )