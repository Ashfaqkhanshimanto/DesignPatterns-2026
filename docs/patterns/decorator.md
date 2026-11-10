
# Phase 9 - Decorator Pattern

## What is the Decorator Pattern?

The Decorator Pattern lets us add extra functionality around an existing object without changing its original code.

In my greenhouse application, I used this pattern to add logging and maximum running time checks to the actuator system.

The actuator still works through the same `ActuatorPort` interface.

## Why I used it

Previously, the simulation adapter could receive actuator commands, but it did not have the logging and runtime policies required in Phase 9.

Instead of putting all these responsibilities inside `SimulationActuatorAdapter`, I created two decorators.

This keeps the code separated and makes it easier to add more policies later.

## Where the pattern is used

The main files are:

- `backend/src/domain/actuators/ports.py`

  Contains the `ActuatorPort` interface with the `apply()` method.

- `backend/src/infrastructure/adapters/actuators/simulation.py`

  Contains the existing simulation adapter. It is the innermost component.

- `backend/src/infrastructure/adapters/actuators/max_runtime_decorator.py`

  Checks whether the actuator has been running for at least 30 minutes.

- `backend/src/infrastructure/adapters/actuators/logging_decorator.py`

  Records successful and failed attempts in PostgreSQL.

- `backend/src/application/actuators/execution_service.py`

  Connects the simulation adapter and decorators in the correct order.

- `backend/src/infrastructure/persistence/execution_log_repository.py`

  Saves and retrieves actuator execution records.

- `backend/src/interfaces/api/actuators.py`

  Provides endpoints for applying simulated commands and reading execution history.

- `frontend/src/features/devices/ExecutionLog.tsx`

  Displays execution history on the dashboard.

## Decorator order

The decorators are connected like this:

ActuatorExecutionService
    |
    v
LoggingActuatorDecorator
    |
    v
MaxRuntimeActuatorDecorator
    |
    v
SimulationActuatorAdapter

Logging is the outermost decorator.

This is important because it must record both successful attempts and attempts blocked by another decorator.

## How an execution works

When the application receives a simulated command:

1. The execution service calls the logging decorator.
2. The logging decorator calls the max-runtime decorator.
3. The max-runtime decorator checks the actuator's persisted state.
4. If the actuator has been running for at least 30 minutes, it blocks the command.
5. Otherwise, the command reaches the simulation adapter.
6. The logging decorator records the result in PostgreSQL.

The runtime policy uses `actuator_states.updated_at`.

The command name is not validated in Phase 9. Command validation will be handled in Phase 10.

## Execution log database

Execution attempts are stored in:

`actuator_execution_log`

The table contains:

- `id` - unique execution identifier
- `device_id` - actuator identifier
- `success` - true or false
- `policy_applied` - JSONB list of policies
- `message` - optional execution message
- `created_at` - execution timestamp

Successful attempts contain:

- `success = true`
- `policy_applied = ["logging"]`
- `message = null`

Attempts blocked by the runtime policy contain:

- `success = false`
- `policy_applied = ["maxRunTime", "logging"]`
- `message = "Max run time exceeded"`

## API

The application provides:

`POST /api/actuators/apply`

This is a temporary endpoint for testing simulated commands.

`GET /api/actuators/executions?limit=20`

This returns recent execution records.

The endpoints are documented in Scalar.

## Frontend

The dashboard contains an Actuator Execution Log.

It displays:

- Execution time
- Device ID
- Success or failure
- Applied policies
- Error message

Users can refresh the list.

No physical actuator hardware is controlled in this phase.

## Decorator versus inheritance

With inheritance, I could create subclasses that add logging or runtime checks.

However, combining several behaviors using inheritance would require more subclasses and could become difficult to maintain.

With Decorator, I can wrap the same actuator port with different policies.

For example, I can add another policy later without rewriting the original simulation adapter.

This makes the system more flexible.

## Testing

I created six unit tests for the decorators and four database integration tests.

The tests verify:

- The runtime policy blocks an actuator after 30 minutes.
- A blocked command does not reach the inner adapter.
- Commands below the runtime limit are forwarded.
- Successful attempts are logged.
- Failed attempts are logged with policy metadata.
- Execution rows are saved in PostgreSQL.
- The API returns execution records.
- Missing actuators return HTTP 404.

All 10 Phase 9 tests passed.

## Conclusion

The Decorator Pattern helped me add logging and runtime policies without modifying the original actuator adapter.

The decorators share the same interface, so the application can use them as one actuator port.

The execution history is saved in PostgreSQL and displayed on the dashboard.

In Phase 10, the Command Pattern will use this decorated actuator port.
