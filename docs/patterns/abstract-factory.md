# Abstract Factory Pattern

## Problem

In this smart greenhouse project we need different groups of devices depending on the environment.

For example, in simulation mode we do not use real hardware, so the devices should have simulation based settings.

For the edge environment the devices should have hardware related settings such as modbus, i2c or gpio.

The problem is that we do not want to create random sensors and actuators separately. We want one matching device family where all the devices belong to the same environment.

## Solution

To solve this I used the Abstract Factory pattern.

The factory creates a complete set of devices for one selected family.

At the moment the project has two families:

- `simulation`
- `edge`

Each family creates four devices:

- moisture sensor
- light sensor
- water pump
- grow light

So instead of creating these devices one by one from different places, the family factory creates the complete set together.

## Where the pattern is used

The main Abstract Factory file is:

`backend/src/domain/devices/family_factory.py`

The abstract factory is:

`DeviceFamilyFactory`

The concrete factories are:

`SimulationDeviceFamilyFactory`

and:

`EdgeDeviceFamilyFactory`

Each factory has its own family key and implements:

`create_device_set()`

This method returns the complete list of devices for that family.

## Simulation family

The simulation factory creates devices with:

`device_family = simulation`

The devices use simulation related configuration.

For example:

`protocol = simulation`

This is useful when developing or testing the application without using real greenhouse hardware.

## Edge family

The edge factory creates devices with:

`device_family = edge`

The edge configuration is different from simulation.

For example:

- moisture sensor uses `modbus`
- light sensor uses `i2c`
- water pump uses `gpio`
- grow light uses `gpio`

These are currently example hardware settings. The project is not controlling real GPIO devices yet.

## Abstract Factory and Factory Method

Phase 2 used the Factory Method pattern.

In Phase 2 the project had creators such as:

`MoistureSensorCreator`

and:

`LightSensorCreator`

These creators are responsible for creating one sensor type with the correct default settings.

I did not remove these creators in Phase 3.

The Abstract Factory uses the Phase 2 creators when it creates the sensor part of a device family.

So the difference is:

Factory Method creates one type of product.

Abstract Factory creates a group of related products that belong together.

In this project the related products are sensors and actuators from the same device family.

## Device domain model

The unified Device entity is located in:

`backend/src/domain/devices/entity.py`

It contains:

- `id`
- `device_type`
- `role`
- `device_family`
- `display_name`
- `default_config`

The `role` tells whether the device is a sensor or actuator.

The `device_family` tells whether it belongs to simulation or edge.

## Why Device and DTO are separate

The domain `Device` is not directly used as the HTTP response model.

For the API I created a separate DTO in:

`backend/src/application/devices/dto.py`

The mapper is in:

`backend/src/application/devices/mappers.py`

I kept them separate because the domain layer should not depend on FastAPI or Pydantic.

The domain Device represents the actual application concept.

The DTO represents the data that is sent through the API.

This also keeps the different layers more separated.

## Database and repository

I reused the existing `devices` table from Phase 2.

I did not create another devices table.

I added the new:

`device_family`

column.

Existing Phase 2 sensors automatically got:

`simulation`

as their family.

The repository can now:

- save one device
- save multiple devices
- list devices
- filter by family
- filter by role

The old sensor repository methods are also still working.

## API

The devices API has:

`GET /api/devices`

This endpoint can use optional filters such as:

`family`

and:

`role`

The provisioning endpoint is:

`POST /api/devices/provision`

It uses the selected family.

For example:

`family=simulation`

or:

`family=edge`

When a family is provisioned, four devices are created and saved to PostgreSQL.

## Frontend

I added a Devices section to the dashboard.

The user can switch between:

- Simulation
- Edge

The user can also provision the selected family.

The dashboard shows:

- device name
- device type
- sensor or actuator role
- device family
- configuration values

When the selected family changes, the frontend loads only devices from that family.

The provisioned devices are saved in PostgreSQL, so they are still available after refreshing the page.

## Adding another family later

Another family can be added later without changing the whole system.

For example, we could add:

`industrial`

Then we could create:

`IndustrialDeviceFamilyFactory`

It could create the same types of sensors and actuators but with different industrial protocols and configuration.

# Abstract Factory Pattern

## Problem

In this smart greenhouse project we need different groups of devices depending on the environment.

For example, in simulation mode we do not use real hardware, so the devices should have simulation based settings.

For the edge environment the devices should have hardware related settings such as modbus, i2c or gpio.

The problem is that we do not want to create random sensors and actuators separately. We want one matching device family where all the devices belong to the same environment.

## Solution

To solve this I used the Abstract Factory pattern.

The factory creates a complete set of devices for one selected family.

At the moment the project has two families:

- `simulation`
- `edge`

Each family creates four devices:

- moisture sensor
- light sensor
- water pump
- grow light

So instead of creating these devices one by one from different places, the family factory creates the complete set together.

## Where the pattern is used

The main Abstract Factory file is:

`backend/src/domain/devices/family_factory.py`

The abstract factory is:

`DeviceFamilyFactory`

The concrete factories are:

`SimulationDeviceFamilyFactory`

and:

`EdgeDeviceFamilyFactory`

Each factory has its own family key and implements:

`create_device_set()`

This method returns the complete list of devices for that family.

## Simulation family

The simulation factory creates devices with:

`device_family = simulation`

The devices use simulation related configuration.

For example:

`protocol = simulation`

This is useful when developing or testing the application without using real greenhouse hardware.

## Edge family

The edge factory creates devices with:

`device_family = edge`

The edge configuration is different from simulation.

For example:

- moisture sensor uses `modbus`
- light sensor uses `i2c`
- water pump uses `gpio`
- grow light uses `gpio`

These are currently example hardware settings. The project is not controlling real GPIO devices yet.

## Abstract Factory and Factory Method

Phase 2 used the Factory Method pattern.

In Phase 2 the project had creators such as:

`MoistureSensorCreator`

and:

`LightSensorCreator`

These creators are responsible for creating one sensor type with the correct default settings.

I did not remove these creators in Phase 3.

The Abstract Factory uses the Phase 2 creators when it creates the sensor part of a device family.

So the difference is:

Factory Method creates one type of product.

Abstract Factory creates a group of related products that belong together.

In this project the related products are sensors and actuators from the same device family.

## Device domain model

The unified Device entity is located in:

`backend/src/domain/devices/entity.py`

It contains:

- `id`
- `device_type`
- `role`
- `device_family`
- `display_name`
- `default_config`

The `role` tells whether the device is a sensor or actuator.

The `device_family` tells whether it belongs to simulation or edge.

## Why Device and DTO are separate

The domain `Device` is not directly used as the HTTP response model.

For the API I created a separate DTO in:

`backend/src/application/devices/dto.py`

The mapper is in:

`backend/src/application/devices/mappers.py`

I kept them separate because the domain layer should not depend on FastAPI or Pydantic.

The domain Device represents the actual application concept.

The DTO represents the data that is sent through the API.

This also keeps the different layers more separated.

## Database and repository

I reused the existing `devices` table from Phase 2.

I did not create another devices table.

I added the new:

`device_family`

column.

Existing Phase 2 sensors automatically got:

`simulation`

as their family.

The repository can now:

- save one device
- save multiple devices
- list devices
- filter by family
- filter by role

The old sensor repository methods are also still working.

## API

The devices API has:

`GET /api/devices`

This endpoint can use optional filters such as:

`family`

and:

`role`

The provisioning endpoint is:

`POST /api/devices/provision`

It uses the selected family.

For example:

`family=simulation`

or:

`family=edge`

When a family is provisioned, four devices are created and saved to PostgreSQL.

## Frontend

I added a Devices section to the dashboard.

The user can switch between:

- Simulation
- Edge

The user can also provision the selected family.

The dashboard shows:

- device name
- device type
- sensor or actuator role
- device family
- configuration values

When the selected family changes, the frontend loads only devices from that family.

The provisioned devices are saved in PostgreSQL, so they are still available after refreshing the page.

## Adding another family later

Another family can be added later without changing the whole system.

For example, we could add:

`industrial`

Then we could create:

`IndustrialDeviceFamilyFactory`

It could create the same types of sensors and actuators but with different industrial protocols and configuration.

After that the new factory could be added to the factory registry.