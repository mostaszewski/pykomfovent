from unittest.mock import patch

import pytest
from aioresponses import aioresponses

from pykomfovent.discovery import KomfoventDiscovery, get_local_subnet


def test_get_local_subnet() -> None:
    with patch("socket.socket") as mock_socket:
        mock_sock = mock_socket.return_value.__enter__.return_value
        mock_sock.getsockname.return_value = ("192.168.1.100", 0)
        subnet = get_local_subnet()
        assert subnet == "192.168.1.0/24"


def test_get_local_subnet_failure() -> None:
    with patch("socket.socket") as mock_socket:
        mock_socket.return_value.__enter__.return_value.connect.side_effect = OSError()
        subnet = get_local_subnet()
        assert subnet is None


@pytest.fixture
def mock_aiohttp() -> aioresponses:
    with aioresponses() as m:
        yield m


async def test_discover_finds_device(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.get(
        "http://192.168.1.137/",
        headers={"Server": "C6"},
        body="<html><title>Komfovent</title></html>",
    )
    for i in range(1, 255):
        if i != 137:
            mock_aiohttp.get(f"http://192.168.1.{i}/", exception=TimeoutError())

    discovery = KomfoventDiscovery(subnet="192.168.1.0/24", timeout=0.1)
    devices = await discovery.discover()

    assert len(devices) == 1
    assert devices[0].host == "192.168.1.137"
    assert devices[0].name == "Komfovent"


async def test_discover_device_without_title(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.get(
        "http://192.168.1.137/",
        headers={"Server": "C6"},
        body="<html>no title here</html>",
    )
    for i in range(1, 255):
        if i != 137:
            mock_aiohttp.get(f"http://192.168.1.{i}/", exception=TimeoutError())

    discovery = KomfoventDiscovery(subnet="192.168.1.0/24", timeout=0.1)
    devices = await discovery.discover()

    assert len(devices) == 1
    assert devices[0].name == "Komfovent"


async def test_discover_device_with_empty_title(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.get(
        "http://192.168.1.137/",
        headers={"Server": "C6"},
        body="<html><title>   </title></html>",
    )
    for i in range(1, 255):
        if i != 137:
            mock_aiohttp.get(f"http://192.168.1.{i}/", exception=TimeoutError())

    discovery = KomfoventDiscovery(subnet="192.168.1.0/24", timeout=0.1)
    devices = await discovery.discover()

    assert len(devices) == 1
    assert devices[0].name == "Komfovent"


async def test_discover_no_devices(mock_aiohttp: aioresponses) -> None:
    for i in range(1, 255):
        mock_aiohttp.get(f"http://192.168.1.{i}/", exception=TimeoutError())

    discovery = KomfoventDiscovery(subnet="192.168.1.0/24", timeout=0.1)
    devices = await discovery.discover()

    assert len(devices) == 0


async def test_discover_ignores_non_c6_servers(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.get(
        "http://192.168.1.1/",
        headers={"Server": "Apache"},
        body="<html></html>",
    )
    for i in range(2, 255):
        mock_aiohttp.get(f"http://192.168.1.{i}/", exception=TimeoutError())

    discovery = KomfoventDiscovery(subnet="192.168.1.0/24", timeout=0.1)
    devices = await discovery.discover()

    assert len(devices) == 0


async def test_discover_no_subnet() -> None:
    with patch("pykomfovent.discovery.get_local_subnet", return_value=None):
        discovery = KomfoventDiscovery()
        devices = await discovery.discover()
        assert devices == []
