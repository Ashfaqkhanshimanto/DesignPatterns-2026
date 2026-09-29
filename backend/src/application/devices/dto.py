from uuid import UUID

from pydantic import BaseModel


class DeviceDto(BaseModel):
    id: UUID
    device_type: str
    role: str
    device_family: str
    display_name: str
    default_config: dict[str, object]
    zone_id: UUID | None = None
    location_id: UUID | None = None


class DeviceZoneAssignmentRequest(BaseModel):
    zone_id: UUID | None