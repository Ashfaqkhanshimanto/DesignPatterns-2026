from abc import ABC, abstractmethod

from domain.devices.entity import Device
from domain.sensors.creators import get_creator


class DeviceFamilyFactory(ABC):
    @property
    @abstractmethod
    def family_key(self) -> str:
        pass

    @abstractmethod
    def create_device_set(self) -> list[Device]:
        pass


class SimulationDeviceFamilyFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "simulation"

    def create_device_set(self) -> list[Device]:
        moisture_sensor = get_creator("moisture").create_sensor(
            display_name="Simulation Soil Moisture Sensor"
        )

        light_sensor = get_creator("light").create_sensor(
            display_name="Simulation Light Sensor"
        )

        return [
            Device(
                id=None,
                device_type=moisture_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture_sensor.display_name,
                default_config={
                    **moisture_sensor.default_config,
                    "protocol": "simulation",
                },
            ),
            Device(
                id=None,
                device_type=light_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light_sensor.display_name,
                default_config={
                    **light_sensor.default_config,
                    "protocol": "simulation",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Simulation Water Pump",
                default_config={
                    "protocol": "simulation",
                    "flow_rate_liters_per_minute": 5,
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Simulation Grow Light",
                default_config={
                    "protocol": "simulation",
                    "max_brightness_percent": 100,
                },
            ),
        ]


class EdgeDeviceFamilyFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "edge"

    def create_device_set(self) -> list[Device]:
        moisture_sensor = get_creator("moisture").create_sensor(
            display_name="Edge Soil Moisture Sensor"
        )

        light_sensor = get_creator("light").create_sensor(
            display_name="Edge Light Sensor"
        )

        return [
            Device(
                id=None,
                device_type=moisture_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture_sensor.display_name,
                default_config={
                    **moisture_sensor.default_config,
                    "protocol": "modbus",
                },
            ),
            Device(
                id=None,
                device_type=light_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light_sensor.display_name,
                default_config={
                    **light_sensor.default_config,
                    "protocol": "i2c",
                },
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge Water Pump",
                default_config={
                    "protocol": "gpio",
                    "gpio_pin": 17,
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge Grow Light",
                default_config={
                    "protocol": "gpio",
                    "gpio_pin": 27,
                },
            ),
        ]


_FACTORIES: dict[str, DeviceFamilyFactory] = {
    "simulation": SimulationDeviceFamilyFactory(),
    "edge": EdgeDeviceFamilyFactory(),
}


def get_family_factory(family: str) -> DeviceFamilyFactory:
    key = family.strip().lower()

    factory = _FACTORIES.get(key)

    if factory is None:
        raise ValueError(
            f"Unknown device family '{family}'. "
            "Supported families are: simulation, edge"
        )

    return factory