from datetime import datetime, timezone

from application.readings.service import ReadingIngest
from infrastructure.persistence.device_repository import DeviceRepository
from infrastructure.persistence.reading_repository import ReadingRepository


class ReadingSampler:
    def __init__(
        self,
        device_repository: DeviceRepository,
        reading_repository: ReadingRepository,
        reading_ingest: ReadingIngest,
    ) -> None:
        self._device_repository = device_repository
        self._reading_repository = reading_repository
        self._reading_ingest = reading_ingest

    def run_once(
        self,
        now: datetime | None = None,
    ) -> int:
        if now is None:
            now = datetime.now(timezone.utc)

        if now.tzinfo is None:
            raise ValueError(
                "Sampler time must be timezone-aware."
            )

        devices = (
            self._device_repository
            .list_tracked_simulation_sensors()
        )

        readings_created = 0

        for device in devices:
            if device.id is None:
                continue

            last_recorded_at = (
                self._reading_repository
                .latest_recorded_at(device.id)
            )

            if last_recorded_at is not None:
                elapsed_seconds = (
                    now - last_recorded_at
                ).total_seconds()

                if (
                    elapsed_seconds
                    < device.sampling_interval_seconds
                ):
                    continue

            self._reading_ingest.record(device.id)
            readings_created += 1

        return readings_created