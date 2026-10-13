
from abc import ABC, abstractmethod

from domain.automation.context import (
    LocationAutomationContext,
    Recommendation,
)


class AutomationStrategy(ABC):

    @abstractmethod
    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        pass


class ConservativeMoistureStrategy(AutomationStrategy):

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:

        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason=(
                    context.missing_reason
                    or "No moisture reading available in this zone."
                ),
            )

        if context.moisture < context.low:
            return Recommendation(
                action="irrigate",
                reason=(
                    "Moisture is below the zone's low threshold."
                ),
            )

        return Recommendation(
            action="wait",
            reason=(
                "Moisture is not below the zone's low threshold."
            ),
        )


class AggressiveMoistureStrategy(AutomationStrategy):

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:

        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason=(
                    context.missing_reason
                    or "No moisture reading available in this zone."
                ),
            )

        trigger = (
            context.low + context.high
        ) / 2

        if context.moisture < trigger:
            return Recommendation(
                action="irrigate",
                reason="Moisture is below the aggressive trigger.",
            )

        return Recommendation(
            action="wait",
            reason="Moisture is at or above the aggressive trigger.",
        )


STRATEGIES: dict[str, AutomationStrategy] = {
    "conservative": ConservativeMoistureStrategy(),
    "aggressive": AggressiveMoistureStrategy(),
}


def get_strategy(
    key: str,
) -> AutomationStrategy:
    strategy = STRATEGIES.get(key)

    if strategy is None:
        raise ValueError(
            f"Unknown strategy key: {key}"
        )

    return strategy
