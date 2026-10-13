
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class LocationAutomationContext:
    location_id: UUID
    zone_id: UUID
    moisture: float | None
    low: float
    high: float
    light: float | None = None
    missing_reason: str | None = None


@dataclass(frozen=True)
class Recommendation:
    action: str
    reason: str
    score: float | None = None
