from application.locations.dto import (
    LocationConfigRead,
    LocationRead,
    ZoneRead,
)
from domain.locations.entity import Location, LocationConfig, Zone


def location_config_to_read(
    config: LocationConfig,
) -> LocationConfigRead:
    location: Location = config.location

    if location.id is None:
        raise ValueError(
            "Cannot map an unsaved location configuration to a read DTO."
        )

    location_read = LocationRead(
        id=location.id,
        name=location.name,
    )

    zone_reads: list[ZoneRead] = []

    for zone in location.zones:
        if zone.id is None:
            raise ValueError(
                "Cannot map an unsaved zone to a read DTO."
            )

        zone_reads.append(
            ZoneRead(
                id=zone.id,
                location_id=location.id,
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )
        )

    return LocationConfigRead(
        location=location_read,
        zones=zone_reads,
    )