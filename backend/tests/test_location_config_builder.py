import pytest

from domain.locations.config_builder import LocationConfigBuilder
from domain.locations.errors import ConfigurationError


def test_builder_creates_location_with_zones():
    config = (
        LocationConfigBuilder()
        .set_location_name("Main Greenhouse")
        .add_zone(
            name="Tomato Zone",
            moisture_threshold_low=0.3,
            moisture_threshold_high=0.7,
            schedule={"watering_time": "08:00"},
        )
        .add_zone(
            name="Herb Zone",
            moisture_threshold_low=0.25,
            moisture_threshold_high=0.6,
            schedule={"watering_time": "18:00"},
        )
        .build()
    )

    assert config.location.name == "Main Greenhouse"
    assert len(config.location.zones) == 2
    assert config.location.zones[0].name == "Tomato Zone"
    assert config.location.zones[1].name == "Herb Zone"


def test_builder_rejects_empty_location_name():
    builder = LocationConfigBuilder()

    builder.set_location_name("")
    builder.add_zone(
        name="Tomato Zone",
        moisture_threshold_low=0.3,
        moisture_threshold_high=0.7,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_requires_at_least_one_zone():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_rejects_low_threshold_below_zero():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")
    builder.add_zone(
        name="Tomato Zone",
        moisture_threshold_low=-0.1,
        moisture_threshold_high=0.7,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_rejects_high_threshold_above_one():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")
    builder.add_zone(
        name="Tomato Zone",
        moisture_threshold_low=0.3,
        moisture_threshold_high=1.1,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_rejects_low_equal_to_high():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")
    builder.add_zone(
        name="Tomato Zone",
        moisture_threshold_low=0.5,
        moisture_threshold_high=0.5,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_rejects_low_greater_than_high():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")
    builder.add_zone(
        name="Tomato Zone",
        moisture_threshold_low=0.8,
        moisture_threshold_high=0.3,
    )

    with pytest.raises(ConfigurationError):
        builder.build()


def test_builder_rejects_duplicate_zone_names():
    builder = LocationConfigBuilder()

    builder.set_location_name("Main Greenhouse")
    builder.add_zone(
        name="Tomato Zone",
        moisture_threshold_low=0.3,
        moisture_threshold_high=0.7,
    )
    builder.add_zone(
        name="tomato zone",
        moisture_threshold_low=0.2,
        moisture_threshold_high=0.8,
    )

    with pytest.raises(ConfigurationError):
        builder.build()