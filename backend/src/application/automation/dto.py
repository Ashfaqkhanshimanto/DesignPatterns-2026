
from uuid import UUID

from pydantic import BaseModel, Field


class StrategySaveRequest(BaseModel):
    strategy_key: str = Field(min_length=1)


class StrategyRead(BaseModel):
    location_id: UUID
    strategy_key: str


class ZoneRecommendationDto(BaseModel):
    zone_id: UUID
    action: str
    reason: str
    score: float | None = None


class AutomationEvaluationDto(BaseModel):
    location_id: UUID
    strategy_key: str
    action: str
    reason: str
    zones: list[ZoneRecommendationDto]
