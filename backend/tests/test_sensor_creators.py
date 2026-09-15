from domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
)


def test_moisture_creator_defaults():
    creator = MoistureSensorCreator()

    sensor = creator.create_sensor()

    assert sensor.device_type == "moisture_sensor"
    assert sensor.default_config["unit"] == "percent"
    assert "moisture_threshold_percent" in sensor.default_config


def test_light_creator_defaults():
    creator = LightSensorCreator()

    sensor = creator.create_sensor()

    assert sensor.device_type == "light_sensor"
    assert sensor.default_config["unit"] == "lux"
    assert "low_light_threshold_lux" in sensor.default_config


def test_sensor_creators_have_different_defaults():
    moisture = MoistureSensorCreator().create_sensor()
    light = LightSensorCreator().create_sensor()

    assert moisture.default_config != light.default_config
    assert moisture.default_config["unit"] != light.default_config["unit"]