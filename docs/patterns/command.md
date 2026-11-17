
# Phase 10 - Command Pattern

## What is the Command Pattern?

The Command Pattern turns an action into its own object.

Instead of calling the actuator directly from the API, my greenhouse application creates a command object and asks an invoker to execute it.

This keeps the code organized and makes it easier to add new commands later.

## Why I used it

In my greenhouse application, I need to control water pumps and grow lights.

Different commands should work through the same system, but they can have different actions and state requirements.

I used the Command Pattern so each operation has its own class.

The application also records command attempts in PostgreSQL, so I can see what happened.

## Where the pattern is used

The main files are:

- `backend/src/domain/commands/base.py`

  Defines the shared Command interface.

- `backend/src/domain/commands/pump.py`

  Contains StartPumpCommand and StopPumpCommand.

- `backend/src/domain/commands/light.py`

  Contains SetLightLevelCommand.

- `backend/src/domain/commands/invoker.py`

  Contains CommandInvoker and its command registry.

- `backend/src/application/commands/service.py`

  Connects command execution with actuator state checks, decorators and logging.

- `backend/src/application/commands/dto.py`

  Defines the API request and result data.

- `backend/src/infrastructure/persistence/command_log_repository.py`

  Saves and retrieves command history.

- `backend/src/interfaces/api/commands.py`

  Provides the command API endpoints.

- `frontend/src/components/commands/CommandPanel.tsx`

  Displays actuator controls and command history.

## Command participants

The Command interface defines execute(port).

The concrete commands are StartPumpCommand, StopPumpCommand and SetLightLevelCommand.

CommandInvoker selects commands from a registry and executes them.

The actuator port is the receiver used by the command objects.

The application service connects everything and handles state checks and database logging.

## How a command executes

1. The frontend sends a command to POST /api/commands.
2. The application checks whether the device exists and is an actuator.
3. The invoker selects the command class using its registry.
4. The service reads the actuator's persisted state.
5. The service checks the allowed commands for that state.
6. If the command is not allowed, it is rejected and saved in command_log.
7. Otherwise, the command executes through the Phase 9 decorated actuator port.
8. If the decorator blocks execution, command_log records failed.
9. After a successful execution, the state changes if the command requires a different target state.
10. The successful result is saved in command_log.

## Commands implemented

### StartPumpCommand

This command starts a simulated water pump.

It changes the state from idle to running after successful execution.

### StopPumpCommand

This command stops a simulated water pump.

It changes the state from running to idle after successful execution.

### SetLightLevelCommand

This command changes the brightness of a simulated grow light.

The default payload is {"level": 1}.

The command is allowed when a grow light is running.

Changing the brightness does not change the running state.

## Integration with Phase 8 - State Pattern

Phase 8 introduced actuator lifecycle states and legal transitions.

Phase 10 uses those existing state rules before executing commands.

For example, trying to start an already-running water pump is rejected.

A rejected command does not call the actuator adapter or change the saved state.

## Integration with Phase 9 - Decorator Pattern

Phase 9 introduced logging and maximum run-time decorators.

Phase 10 executes commands through the same decorated ActuatorPort.

The order is:

LoggingActuatorDecorator
    |
MaxRuntimeActuatorDecorator
    |
SimulationActuatorAdapter

This means the Phase 9 execution log continues working.

If the max-runtime policy blocks a command, Phase 10 records failed in command_log.

## Command history database

Command history is saved in the command_log table.

Each row contains:

- id
- command_type
- device_id
- payload
- status
- error_message
- created_at

There are three possible statuses:

- success: the command executed successfully
- failed: execution was attempted but failed
- rejected: the command was not permitted in the actuator's state

Unknown command types do not create a command_log row.

## API

POST /api/commands

Executes a command using the command service.

GET /api/commands?limit=50

Returns recent command history, newest first.

API results:

- 200 for success and failed execution
- 409 for rejected commands
- 400 for unknown command types
- 404 for missing devices or non-actuator devices

Both endpoints are documented in Scalar.

## Frontend

The dashboard contains actuator controls and command history.

Users can start and stop simulated pumps or set the light level.

Buttons are disabled when the command is absent from allowed_commands.

After sending a command, the frontend refreshes device states and command history.

The Phase 9 execution log remains visible below the controls.

## Why not call the port directly from the router?

If the HTTP router called the actuator port directly, the API would need to handle command selection, validation, state changes and logging.

That would mix too many responsibilities into one place.

With the Command Pattern, the router only passes the request to the command service.

The command objects handle operations, and the service handles the rules and history.

This makes the code easier to maintain and test.

## Testing

I tested the commands manually using the API and dashboard.

I verified successful pump start and stop, rejected light commands, failed commands blocked by the runtime policy, and successful light-level changes.

I also created six automated integration tests.

The tests check:

- Successful pump start updates state and saves logs.
- Rejected commands do not change state.
- Runtime failures are saved in both log tables.
- Unknown commands return HTTP 400 without inserting a log.
- Missing actuators return HTTP 404.
- Command history is returned newest first.

All six Phase 10 integration tests passed.

## Conclusion

The Command Pattern helped me separate greenhouse actions into their own objects.

The invoker can execute different commands using the same interface.

The application also checks actuator states and saves command history, making the system safer and easier to understand.

In Phase 11, the Observer Pattern can use command results to publish events.
