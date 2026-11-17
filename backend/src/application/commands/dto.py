
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CommandRequestDto(BaseModel):
    command_type: str
    device_id: UUID
    payload: dict[str, object] | None = None


class CommandLogDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    command_type: str
    device_id: UUID
    payload: dict[str, object]
    status: str
    error_message: str | None
    created_at: datetime
