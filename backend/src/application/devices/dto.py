
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceDto(BaseModel):
    id: UUID
    device_type: str
    role: str
    device_family: str
    display_name: str
    default_config: dict[str, object]
    zone_id: UUID | None = None
    location_id: UUID | None = None
    sampling_interval_seconds: int
    tracking_enabled: bool

    # Phase 8: Actuator lifecycle information.
    # Sensors do not have actuator states.
    state: str | None = None
    allowed_commands: list[str] = Field(default_factory=list)


class DeviceZoneAssignmentRequest(BaseModel):
    zone_id: UUID | None


class DeviceSamplingRequest(BaseModel):
    sampling_interval_seconds: int = Field(
        ge=5,
    )
    tracking_enabled: bool
