
# Strategy Pattern — Phase 6

## Problem

In my smart greenhouse project, different locations may need different irrigation rules.

For example, one greenhouse may only need watering when the moisture drops below the low threshold. Another greenhouse may need watering earlier.

If I put all these conditions directly inside the API, the code will become difficult to maintain when I add more automation rules.

## Solution

I used the Strategy design pattern to solve this problem.

The Strategy pattern lets my application select different irrigation algorithms without changing the main application service.

I created two strategies:

- ConservativeMoistureStrategy
- AggressiveMoistureStrategy

Both implement the same AutomationStrategy interface with the decide(context) method.

## How the strategies work

Conservative Strategy:

This strategy recommends irrigation only when the latest moisture reading is below the zone's low threshold.

Aggressive Strategy:

This strategy uses the middle value between the zone's low and high thresholds. It recommends irrigation earlier than the conservative strategy.

For example:

Low threshold: 0.30
High threshold: 0.70
Moisture reading: 0.40

Conservative result: wait

Aggressive result: irrigate

Both strategies use the same information but make different decisions.

## Where the pattern is used

backend/src/domain/automation/context.py

Contains LocationAutomationContext and Recommendation.

backend/src/domain/automation/strategy.py

Contains AutomationStrategy, ConservativeMoistureStrategy, AggressiveMoistureStrategy, and get_strategy().

backend/src/infrastructure/persistence/automation_repository.py

Loads the selected strategy and the latest moisture readings from PostgreSQL. Each zone uses only its own assigned moisture sensors.

backend/src/application/automation/service.py

Selects the saved strategy, prepares the zone contexts, and returns the recommendations.

backend/src/interfaces/api/automation.py

Contains the API endpoints for saving, reading, and evaluating the strategy.

frontend/src/features/automation/StrategyPanel.tsx

Allows the user to select a strategy and evaluate it from the dashboard.

## Saving the strategy

I used a separate automation_rules table.

It stores the strategy_key for each location_id.

The location_id is unique, so each location can have only one active strategy configuration.

## Missing sensor handling

If a zone has no assigned moisture sensor, the application returns wait and explains why.

It also handles cases where a sensor has no stored readings or has an unsupported moisture unit.

The application does not use another zone's sensor reading.

## How I can add a third strategy

For example, I could add BalancedMoistureStrategy.

I would:

1. Create a new class implementing AutomationStrategy.
2. Implement the decide(context) method.
3. Add the new strategy to the STRATEGIES dictionary.
4. Add the strategy option to the frontend dropdown.
5. Write tests for the new strategy.

I would not need to rewrite the API or the automation application service.

## Conclusion

The Strategy pattern makes the irrigation logic easier to change and extend.

Each strategy has its own decision algorithm, while the rest of the application uses the same interface.
