
from uuid import UUID

from application.automation.service import AutomationService
from application.overview.dto import (
    DeviceCountsDto,
    LastRecommendationDto,
    LatestReadingDto,
    LocationOverviewDto,
    OverviewDeviceDto,
    OverviewLocationDto,
    OverviewZoneDto,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from infrastructure.persistence.overview_repository import (
    OverviewRepository,
)


class OverviewLocationNotFoundError(Exception):
    pass


class LocationOverviewFacade:
    def __init__(
        self,
        overview_repository: OverviewRepository,
        automation_repository: AutomationRepository,
        automation_service: AutomationService,
    ) -> None:
        self._overview_repository = overview_repository
        self._automation_repository = automation_repository
        self._automation_service = automation_service

    def get_overview(
        self,
        location_id: UUID,
    ) -> LocationOverviewDto:
        location = self._overview_repository.get_location(
            location_id
        )

        if location is None:
            raise OverviewLocationNotFoundError(
                f"Location {location_id} was not found."
            )

        zones = self._overview_repository.get_zones(
            location_id
        )

        devices = self._overview_repository.get_assigned_devices(
            location_id
        )

        latest_readings = (
            self._overview_repository.get_latest_readings(
                [device.id for device in devices]
            )
        )

        device_counts = DeviceCountsDto(
            sensor=sum(
                device.role == "sensor"
                for device in devices
            ),
            actuator=sum(
                device.role == "actuator"
                for device in devices
            ),
        )

        zone_results = []

        for zone in zones:
            zone_devices = [
                device
                for device in devices
                if device.zone_id == zone.id
            ]

            zone_readings = []

            for device in zone_devices:
                reading = latest_readings.get(device.id)

                if reading is not None:
                    zone_readings.append(
                        LatestReadingDto(
                            device_id=device.id,
                            value=float(reading.value),
                            unit=reading.unit,
                            recorded_at=reading.recorded_at,
                            tracking_enabled=device.tracking_enabled,
                            sampling_interval_seconds=(
                                device.sampling_interval_seconds
                            ),
                        )
                    )

            zone_results.append(
                OverviewZoneDto(
                    id=zone.id,
                    name=zone.name,
                    moisture_threshold_low=float(
                        zone.moisture_threshold_low
                    ),
                    moisture_threshold_high=float(
                        zone.moisture_threshold_high
                    ),
                    devices=[
                        OverviewDeviceDto(
                            id=device.id,
                            device_type=device.device_type,
                            role=device.role,
                            display_name=device.display_name,
                        )
                        for device in zone_devices
                    ],
                    latest_readings=zone_readings,
                )
            )

        strategy_key = (
            self._automation_repository.get_strategy_key(
                location_id
            )
        )

        last_recommendation = None

        # Only evaluate when a strategy has been saved.
        # A location without one still returns a valid overview.
        if strategy_key is not None:
            evaluation = self._automation_service.evaluate(
                location_id
            )

            last_recommendation = LastRecommendationDto(
                action=evaluation.action,
                reason=evaluation.reason,
            )

        return LocationOverviewDto(
            location=OverviewLocationDto(
                id=location.id,
                name=location.name,
            ),
            device_counts=device_counts,
            zones=zone_results,
            strategy_key=strategy_key,
            last_recommendation=last_recommendation,
        )
