import os

import pytest

from pykomfovent import KomfoventClient, KomfoventDiscovery

pytestmark = pytest.mark.skipif(
    os.environ.get("KOMFOVENT_HOST") is None,
    reason="Set KOMFOVENT_HOST, KOMFOVENT_USER, KOMFOVENT_PASS to run integration tests",
)


@pytest.fixture
def host() -> str:
    return os.environ.get("KOMFOVENT_HOST", "192.168.0.137")


@pytest.fixture
def username() -> str:
    return os.environ.get("KOMFOVENT_USER", "user")


@pytest.fixture
def password() -> str:
    return os.environ.get("KOMFOVENT_PASS", "user")


async def test_real_device_authenticate(host: str, username: str, password: str) -> None:
    async with KomfoventClient(host, username, password) as client:
        result = await client.authenticate()
        assert result is True


async def test_real_device_get_state(host: str, username: str, password: str) -> None:
    async with KomfoventClient(host, username, password) as client:
        state = await client.get_state()

        print(f"\nMode: {state.mode}")
        print(f"Supply temp: {state.supply_temp}°C")
        print(f"Extract temp: {state.extract_temp}°C")
        print(f"Outdoor temp: {state.outdoor_temp}°C")
        print(f"Supply fan: {state.supply_fan_percent}%")
        print(f"Extract fan: {state.extract_fan_percent}%")
        print(f"Filter: {state.filter_contamination}%")
        print(f"Heat recovery: {state.heat_recovery_power}W")
        print(f"Power: {state.power_consumption}W")
        print(f"Efficiency: {state.heat_exchanger_efficiency}%")

        assert state.mode is not None
        assert state.outdoor_temp is not None


async def test_real_device_discovery() -> None:
    discovery = KomfoventDiscovery(timeout=3.0)
    devices = await discovery.discover()

    print(f"\nFound {len(devices)} device(s):")
    for device in devices:
        print(f"  - {device.host}: {device.name}")
