from domain.devices.family_factory import get_family_factory


def test_simulation_factory_creates_four_devices():
    factory = get_family_factory("simulation")

    devices = factory.create_device_set()

    assert len(devices) == 4
    assert all(device.device_family == "simulation" for device in devices)

    roles = {device.role for device in devices}

    assert "sensor" in roles
    assert "actuator" in roles


def test_edge_factory_creates_four_devices():
    factory = get_family_factory("edge")

    devices = factory.create_device_set()

    assert len(devices) == 4
    assert all(device.device_family == "edge" for device in devices)

    roles = {device.role for device in devices}

    assert "sensor" in roles
    assert "actuator" in roles


def test_edge_factory_differs_from_simulation():
    simulation_devices = (
        get_family_factory("simulation")
        .create_device_set()
    )

    edge_devices = (
        get_family_factory("edge")
        .create_device_set()
    )

    simulation_protocols = {
        device.default_config.get("protocol")
        for device in simulation_devices
    }

    edge_protocols = {
        device.default_config.get("protocol")
        for device in edge_devices
    }

    assert simulation_protocols != edge_protocols