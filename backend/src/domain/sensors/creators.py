from abc import ABC, abstractmethod

from domain.sensors.entity import Sensor


class SensorCreator(ABC):
    @abstractmethod
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        pass


class MoistureSensorCreator(SensorCreator):
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        return Sensor(
            id=None,
            device_type="moisture_sensor",
            display_name=display_name or "Soil Moisture Sensor",
            default_config={
                "unit": "percent",
                "sampling_interval_seconds": 300,
                "moisture_threshold_percent": 30,
            },
        )


class LightSensorCreator(SensorCreator):
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        return Sensor(
            id=None,
            device_type="light_sensor",
            display_name=display_name or "Light Sensor",
            default_config={
                "unit": "lux",
                "sampling_interval_seconds": 60,
                "low_light_threshold_lux": 10000,
            },
        )


_CREATORS: dict[str, SensorCreator] = {
    "moisture": MoistureSensorCreator(),
    "light": LightSensorCreator(),
}


def get_creator(sensor_type: str) -> SensorCreator:
    key = sensor_type.strip().lower()

    creator = _CREATORS.get(key)

    if creator is None:
        raise ValueError(
            f"Unknown sensor type '{sensor_type}'. "
            "Supported types are: moisture, light"
        )

    return creator