
# State Pattern — Phase 8

## What is the State Pattern?

The State Pattern helps an object behave differently depending on its current state.

In our Smart Greenhouse application, we use it to manage actuator lifecycle states. For example, a water pump can be idle, running, off, in error, or in maintenance.

Not every state change is allowed.

## Why we used it

Our greenhouse has actuators such as water pumps and grow lights.

We need to know their current state and which commands are allowed before trying to control them.

Instead of writing state checks in different API handlers, we keep the transition rules in the domain layer.

This makes the rules easier to understand, test, and reuse in Phase 10.

## Where the pattern is used

### Domain

- `backend/src/domain/actuators/state.py`

  Contains the transition table, allowed commands, and IllegalTransitionError.

- `backend/src/domain/actuators/context.py`

  Contains ActuatorContext, which manages an actuator's current state.

### Application

- `backend/src/application/actuators/service.py`

  Loads the actuator's state, checks the transition, and saves a valid new state.

- `backend/src/application/devices/dto.py`

  Includes state and allowed_commands in device responses.

### Infrastructure

- `backend/src/infrastructure/persistence/models.py`

  Defines the ActuatorStateRow database model.

- `backend/src/infrastructure/persistence/actuator_state_repository.py`

  Loads and saves states in PostgreSQL.

### API

- `backend/src/interfaces/api/actuator_states.py`

  Contains the endpoints for reading and changing actuator states.

- `backend/src/interfaces/api/devices.py`

  Includes state information in existing device responses.

### Frontend

- `frontend/src/features/devices/DeviceList.tsx`

  Displays state badges and allowed commands for actuators.

## Actuator states

We support five states:

- idle
- running
- off
- error
- maintenance

Existing actuators were initialized to idle in the Phase 8 database migration.

New actuators without a state record receive idle when the application state service initializes them.

## Allowed transitions

| Current state | Target state | Command |
|---|---|---|
| idle | running | start_pump |
| idle | off | turn_off |
| idle | error | report_error |
| idle | maintenance | enter_maintenance |
| running | idle | stop_pump |
| running | error | report_error |
| off | idle | turn_on |
| off | error | report_error |
| error | idle | reset |
| maintenance | idle | finish_maintenance |
| maintenance | error | report_error |

All other transitions are rejected.

For example, running directly to maintenance is not allowed.

The domain raises IllegalTransitionError and the API returns HTTP 409.

An invalid transition does not update the saved database state.

These are lifecycle rules. Changing the state currently does not physically operate a water pump or grow light.

## Database persistence

We added the actuator_states table with:

- device_id: primary key and foreign key to devices.id
- state: current lifecycle state
- updated_at: timestamp

The migration was generated with Alembic.

We added a data migration step that initializes existing actuator devices to idle.

The application uses ActuatorStateRepository to read and save the state.

This means states are stored in PostgreSQL instead of only being kept in Python memory.

## API

We added:

GET /api/devices/{device_id}/state

This returns the current state and allowed commands.

POST /api/devices/{device_id}/transition

This accepts a target state and attempts a transition.

The API returns HTTP 404 for a missing actuator and HTTP 409 for an illegal transition.

The existing devices API also includes state and allowed_commands for actuator devices.

Sensors have no actuator lifecycle state.

Scalar documents these endpoints and response fields.

## Frontend

The Devices section displays actuator state badges.

For example:

- running: green badge
- idle: blue badge
- error: red badge
- maintenance: yellow badge
- off: gray badge

The cards also show which commands are allowed in the current state.

These command labels are not execution buttons. Phase 10 will add the Command Pattern and actual command handling.

## Testing

We added:

- `backend/tests/test_actuator_state.py`
- `backend/tests/test_actuator_state_integration.py`

The unit tests check legal transitions, illegal transitions, allowed commands, and ActuatorContext.

The integration tests check PostgreSQL persistence, rejected transitions, initial idle state, and missing actuators.

Results:

- 10 unit tests passed.
- 4 integration tests passed.

## Benefits

The main benefit is that state rules are kept in one place.

The API and frontend do not need to decide which transitions are legal.

The application can show the current state, reject illegal transitions, and keep the state saved after restarting the backend.

Phase 10 can reuse these allowed commands and state guards.
