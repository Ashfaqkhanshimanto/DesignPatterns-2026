# Adapter Pattern – Smart Greenhouse

## What is the Adapter pattern?

The Adapter pattern allows the application to work with different external systems through one common interface.

In this greenhouse project, sensors can provide data in different formats. A simulation sensor, a vendor sensor, and an MQTT message do not necessarily return their data in the same way.

Instead of making the rest of the application understand every sensor format, adapters convert the different inputs into the same `Reading` format.

This keeps the application code simpler and separates device-specific details from the main greenhouse logic.


## Why I used Adapter in this project

The greenhouse needs to support different ways of receiving sensor readings.

For example:

- simulation sensors generate values inside the application
- the vendor stub represents a sensor with its own payload format
- MQTT can provide readings using an MQTT-style payload

These sources are different, but the application should not need separate logic everywhere for each one.

The adapters normalize the data before it is used by the application.


## Common sensor interface

The sensor side uses `SensorPort`.

The main operation is:

`read(device_id, device_type)`

A sensor adapter that supports direct reading can implement this interface and return a normalized `Reading`.

The application can therefore work with the sensor abstraction instead of depending on the details of the physical device.


## Normalized Reading

Different sensor inputs are converted into the same domain object:

`Reading`

A reading contains:

- `device_id`
- `value`
- `unit`
- `source`
- `recorded_at`

The timestamp must be timezone-aware.

This means the persistence and application layers do not need to understand the original format used by each sensor.


## Simulation sensor adapter

`SimulationSensorAdapter` is used for simulation sensors.

For a moisture sensor, it generates a simulated moisture value and returns the unit `vwc`.

For a light sensor, it generates a simulated light value and returns the unit `lux`.

The source is stored as `simulation`.

This adapter is useful for developing and testing the greenhouse without connecting real sensor hardware.


## Vendor stub adapter

`VendorStubSensorAdapter` represents a possible third-party sensor system.

The vendor payload uses fields such as:

- `measurement`
- `measurement_unit`

The adapter translates those fields into the application's normal `Reading` structure.

The source is stored as `vendor`.

In this implementation, the vendor adapter can be selected using the `vendor` protocol value. It is only a stub for demonstrating how another sensor format can be adapted.


## MQTT adapter

`MqttSensorAdapter` translates an MQTT-style payload into a `Reading`.

For example, the incoming payload can contain:

- `value`
- `unit`

The adapter validates and translates this data into the common `Reading` format.

The source is stored as `mqtt`.

The MQTT adapter does not connect to an MQTT broker. Its responsibility in this phase is only payload translation.


## Actuator adapter

The project also contains an `ActuatorPort`.

Its main operation is:

`apply(device_id, command, payload)`

`SimulationActuatorAdapter` provides a simple simulation implementation.

Instead of controlling real hardware, it stores the applied commands in memory. This gives the project an actuator-side port and adapter without requiring physical greenhouse equipment.


## Reading ingest flow

The main sensor reading flow is:

1. The application receives a device ID.
2. `ReadingIngest` loads the device.
3. The sensor protocol is checked.
4. The appropriate adapter is selected.
5. The adapter produces a normalized `Reading`.
6. `ReadingRepository` persists the reading.
7. The application returns a `ReadingDto`.

For translated MQTT data, the MQTT adapter first converts the payload into a `Reading`, and `record_translated()` sends the normalized reading through the persistence path.


## Automatic sampling

The application also has a `ReadingSampler`.

It finds tracked simulation sensors and checks their `sampling_interval_seconds`.

If enough time has passed since the previous reading, the sampler asks `ReadingIngest` to create another reading.

The background sampling loop runs from the FastAPI lifespan, so simulation sensors can generate readings automatically while the backend is running.


## Why Adapter is useful here

Without adapters, the application would need sensor-specific code in many places.

For example, application services might need to know that one source uses `measurement`, another uses `value`, and another generates the value internally.

With Adapter, those differences stay inside the adapter classes.

The rest of the greenhouse application can work with the same `Reading` structure.


## Benefits in this project

The main benefits are:

- different sensor formats are converted into one format
- external device details are separated from application logic
- simulation can be used without real hardware
- new sensor integrations can be added with less impact on existing code
- persistence works with normalized readings instead of vendor-specific payloads
- adapters can be tested independently


## Main files

The main Adapter-related files in this phase are:

`backend/src/domain/sensors/ports.py`

Defines the `SensorPort`.

`backend/src/domain/actuators/ports.py`

Defines the `ActuatorPort`.

`backend/src/domain/sensors/reading.py`

Defines the normalized `Reading` domain object.

`backend/src/infrastructure/adapters/sensors/simulation.py`

Implements the simulation sensor adapter.

`backend/src/infrastructure/adapters/sensors/vendor_stub.py`

Implements the vendor stub adapter.

`backend/src/infrastructure/adapters/sensors/mqtt.py`

Translates MQTT payloads.

`backend/src/infrastructure/adapters/actuators/simulation.py`

Implements the simulation actuator adapter.

`backend/src/application/readings/service.py`

Coordinates adapter selection and reading persistence.

`backend/src/application/readings/sampler.py`

Handles automatic sampling of tracked simulation sensors.


## Summary

In this greenhouse application, Adapter gives different sensor sources a common form that the rest of the system can understand.

Simulation, vendor, and MQTT data may start in different formats, but they are converted into the same `Reading` model before the application works with them.

This keeps hardware and integration details outside the main application logic and makes it easier to add more sensor types later.