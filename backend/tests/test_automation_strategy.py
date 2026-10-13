
from uuid import uuid4

import pytest

from domain.automation.context import LocationAutomationContext
from domain.automation.strategy import get_strategy


@pytest.fixture
def context():
    return LocationAutomationContext(
        location_id=uuid4(),
        zone_id=uuid4(),
        moisture=0.40,
        low=0.30,
        high=0.70,
    )


def test_conservative_waits(context):
    result = get_strategy("conservative").decide(context)

    assert result.action == "wait"


def test_aggressive_irrigates(context):
    result = get_strategy("aggressive").decide(context)

    assert result.action == "irrigate"


def test_strategies_produce_different_results(context):
    conservative = get_strategy("conservative").decide(context)
    aggressive = get_strategy("aggressive").decide(context)

    assert conservative.action != aggressive.action


@pytest.mark.parametrize(
    "strategy_key",
    ["conservative", "aggressive"],
)
def test_missing_sensor_waits(strategy_key):
    context = LocationAutomationContext(
        location_id=uuid4(),
        zone_id=uuid4(),
        moisture=None,
        low=0.30,
        high=0.70,
        missing_reason="No moisture sensor assigned to this zone.",
    )

    result = get_strategy(strategy_key).decide(context)

    assert result.action == "wait"
    assert result.reason == (
        "No moisture sensor assigned to this zone."
    )


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError):
        get_strategy("invalid_strategy")
