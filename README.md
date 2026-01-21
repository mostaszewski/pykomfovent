# pykomfovent

[![CI](https://github.com/mostaszewski/pykomfovent/actions/workflows/ci.yml/badge.svg)](https://github.com/mostaszewski/pykomfovent/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pykomfovent)](https://pypi.org/project/pykomfovent/)
[![Python](https://img.shields.io/pypi/pyversions/pykomfovent)](https://pypi.org/project/pykomfovent/)
[![License](https://img.shields.io/github/license/mostaszewski/pykomfovent)](LICENSE)

Async Python client for Komfovent C6 ventilation units.

## Installation

```bash
pip install pykomfovent
```

## Quick Start

```python
import asyncio
from pykomfovent import KomfoventClient

async def main():
    async with KomfoventClient("192.168.1.100", "user", "password") as client:
        state = await client.get_state()
        print(f"Mode: {state.mode}")
        print(f"Supply temp: {state.supply_temp}°C")
        print(f"Outdoor temp: {state.outdoor_temp}°C")

asyncio.run(main())
```

## Features

### Control

```python
await client.set_mode("intensive")  # away, normal, intensive, boost
await client.set_supply_temp(22.5)  # 10-35°C
```

### Schedule Management

```python
schedule = await client.get_schedule()
await client.set_schedule({"key": value})
```

### Device Discovery

```python
from pykomfovent import KomfoventDiscovery

discovery = KomfoventDiscovery()
devices = await discovery.discover()
for device in devices:
    print(f"{device.host} - {device.name}")
```

## Available Data

The `KomfoventState` object provides:

| Property | Description |
|----------|-------------|
| `mode` | Operating mode |
| `supply_temp` | Supply air temperature (°C) |
| `extract_temp` | Extract air temperature (°C) |
| `outdoor_temp` | Outdoor temperature (°C) |
| `supply_fan_percent` | Supply fan speed (%) |
| `extract_fan_percent` | Extract fan speed (%) |
| `filter_contamination` | Filter contamination level (%) |
| `heat_exchanger_efficiency` | Heat exchanger efficiency (%) |
| `power_consumption` | Power consumption (W) |
| `heating_power` | Heating power (W) |
| `energy_consumed_daily/monthly/total` | Energy consumption (kWh) |
| `energy_recovered_daily/monthly/total` | Energy recovered (kWh) |
| `air_quality` | Air quality (%) |
| `humidity` | Humidity (%) |

### Computed Properties

- `is_on` - True if unit is running
- `heating_active` - True if heater is active
- `eco_mode` - True if ECO mode is enabled

## Requirements

- Python 3.11+
- Komfovent C6 ventilation unit with web interface

## License

MIT
