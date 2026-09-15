# Factory Method - Phase 2

## Problem

In the smart greenhouse project we need different sensor types such as moisture sensors and light sensors.

Each sensor type has different default settings. For example the moisture sensor uses percent and has a moisture threshold while the light sensor uses lux and has a light threshold.

If every part of the application created these sensors directly then the creation logic would be repeated in different places. Adding another sensor type later would also require changing many parts of the application.

## Solution

Factory Method is used to keep sensor creation in one clear structure.

The project has a common SensorCreator interface and separate concrete creators for each sensor type.

MoistureSensorCreator creates a moisture sensor with moisture specific defaults.

LightSensorCreator creates a light sensor with light specific defaults.

The application uses get_creator with a short type such as moisture or light. The selected creator then decides the device_type and default configuration of the sensor.

This means the API does not need to know how each sensor type is built.

## Where the pattern is used

The main Factory Method files are:

backend/src/domain/sensors/entity.py

This contains the plain Python Sensor domain entity.

backend/src/domain/sensors/creators.py

This contains SensorCreator, MoistureSensorCreator, LightSensorCreator and the creator registry.

backend/src/application/sensors/service.py

The SensorService gets the correct creator and asks it to create the sensor.

backend/src/infrastructure/persistence/device_repository.py

The repository saves the created sensor into the devices table.

## Flow

The sensor creation flow is:

API request
-> SensorService
-> get_creator
-> concrete SensorCreator
-> Sensor
-> DeviceRepository
-> PostgreSQL devices table

## Why this helps

The API and other callers do not need to create specific sensor types directly.

If another sensor type is added later we can create another creator and register it without putting sensor construction code inside the API routes.

## Small extension exercise

A temperature sensor could be added by creating a TemperatureSensorCreator.

It could create:

device_type = temperature_sensor

and default settings such as:

unit = celsius

sampling_interval_seconds = 120

high_temperature_threshold = 30

After that the creator could be registered with the key temperature.
