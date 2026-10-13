
from uuid import UUID

from application.automation.dto import (
    AutomationEvaluationDto,
    StrategyRead,
    ZoneRecommendationDto,
)
from domain.automation.strategy import (
    STRATEGIES,
    get_strategy,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


class AutomationLocationNotFoundError(Exception):
    pass


class AutomationService:
    def __init__(
        self,
        repository: AutomationRepository,
    ) -> None:
        self._repository = repository

    def _check_location(self, location_id: UUID) -> None:
        if not self._repository.location_exists(location_id):
            raise AutomationLocationNotFoundError(
                f"Location {location_id} was not found."
            )

    def save_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> StrategyRead:
        self._check_location(location_id)

        # Validate before saving anything.
        get_strategy(strategy_key)

        self._repository.save_strategy_key(
            location_id,
            strategy_key,
        )

        return StrategyRead(
            location_id=location_id,
            strategy_key=strategy_key,
        )

    def get_saved_strategy(
        self,
        location_id: UUID,
    ) -> StrategyRead:
        self._check_location(location_id)

        key = self._repository.get_strategy_key(
            location_id
        )

        # A new location uses conservative until
        # an explicit strategy is saved.
        if key is None:
            key = "conservative"

        return StrategyRead(
            location_id=location_id,
            strategy_key=key,
        )

    def evaluate(
        self,
        location_id: UUID,
    ) -> AutomationEvaluationDto:
        self._check_location(location_id)

        saved = self.get_saved_strategy(location_id)
        strategy = get_strategy(saved.strategy_key)

        contexts = self._repository.get_contexts(
            location_id
        )

        zone_results = []

        for context in contexts:
            recommendation = strategy.decide(context)

            zone_results.append(
                ZoneRecommendationDto(
                    zone_id=context.zone_id,
                    action=recommendation.action,
                    reason=recommendation.reason,
                    score=recommendation.score,
                )
            )

        irrigate_count = sum(
            zone.action == "irrigate"
            for zone in zone_results
        )

        if not zone_results:
            action = "wait"
            reason = "No zones exist in this location."

        elif irrigate_count > 0:
            action = "irrigate"
            reason = (
                f"{irrigate_count} of {len(zone_results)} "
                "zones recommend irrigation."
            )

        else:
            action = "wait"
            reason = (
                "No zones currently recommend irrigation."
            )

        return AutomationEvaluationDto(
            location_id=location_id,
            strategy_key=saved.strategy_key,
            action=action,
            reason=reason,
            zones=zone_results,
        )
