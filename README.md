# pykomfovent

[![CI](https://github.com/mostaszewski/pykomfovent/actions/workflows/ci.yml/badge.svg)](https://github.com/mostaszewski/pykomfovent/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pykomfovent)](https://pypi.org/project/pykomfovent/)
[![Python](https://img.shields.io/pypi/pyversions/pykomfovent)](https://pypi.org/project/pykomfovent/)
[![License](https://img.shields.io/github/license/mostaszewski/pykomfovent)](LICENSE)

Async Python client for Komfovent C6 ventilation units.

> **Support:** [Open an issue](https://github.com/mostaszewski/pykomfovent/issues) or contact pykomfovent@ostaszewski.pl

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
        # Read state
        state = await client.get_state()
        print(f"Mode: {state.mode}, Supply: {state.supply_temp}°C")
        
        # Control
        await client.set_mode("normal")
        await client.set_supply_temp(22.5)

asyncio.run(main())
```

---

## API Reference

### KomfoventClient

The main client for communicating with Komfovent C6 units.

- Async context manager for automatic session cleanup
- Automatic retry (3 attempts) with exponential backoff
- 10 second timeout per request

```python
client = KomfoventClient(
    host="192.168.1.100",  # IP address of your unit
    username="user",       # Web interface username
    password="password",   # Web interface password
    port=80                # Optional, defaults to 80
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `authenticate()` | Verify credentials, returns `bool` |
| `get_state()` | Get current unit state, returns `KomfoventState` |
| `set_mode(mode)` | Set mode: `"away"`, `"normal"`, `"intensive"`, `"boost"` |
| `set_supply_temp(temp)` | Set target supply temperature (10-35°C) |
| `get_schedule()` | Get weekly schedule configuration |
| `set_schedule(commands)` | Update schedule settings |
| `set_register(register, value)` | Low-level register access |
| `close()` | Close the HTTP session |

---

### KomfoventState

Immutable dataclass containing all sensor values.

#### Temperatures

| Property | Description |
|----------|-------------|
| `supply_temp` | Supply air temperature (°C) |
| `extract_temp` | Extract air temperature (°C) |
| `outdoor_temp` | Outdoor temperature (°C) |
| `supply_temp_setpoint` | Target supply temperature (°C) |
| `extract_temp_setpoint` | Target extract temperature (°C) |

#### Fan Status

| Property | Description |
|----------|-------------|
| `supply_fan_percent` | Supply fan speed (%) |
| `extract_fan_percent` | Extract fan speed (%) |
| `supply_fan_intensity` | Supply fan intensity |
| `extract_fan_intensity` | Extract fan intensity |

#### Heat Exchanger & Heating

| Property | Description |
|----------|-------------|
| `heat_exchanger_percent` | Heat exchanger position (%) |
| `heat_exchanger_efficiency` | Heat recovery efficiency (%) |
| `heat_recovery_power` | Heat recovery power (W) |
| `electric_heater_percent` | Electric heater power (%) |
| `heating_power` | Total heating power (W) |

#### Energy Statistics

| Property | Description |
|----------|-------------|
| `power_consumption` | Current power consumption (W) |
| `energy_consumed_daily` | Energy consumed today (kWh) |
| `energy_consumed_monthly` | Energy consumed this month (kWh) |
| `energy_consumed_total` | Total energy consumed (kWh) |
| `energy_heating_daily` | Heating energy today (kWh) |
| `energy_heating_monthly` | Heating energy this month (kWh) |
| `energy_heating_total` | Total heating energy (kWh) |
| `energy_recovered_daily` | Energy recovered today (kWh) |
| `energy_recovered_monthly` | Energy recovered this month (kWh) |
| `energy_recovered_total` | Total energy recovered (kWh) |
| `spi_actual` | Current SPI - Specific Power Input (W/(m³/h)) |
| `spi_daily` | Daily average SPI |

#### Other

| Property | Description |
|----------|-------------|
| `mode` | Current operating mode (string) |
| `filter_contamination` | Filter contamination level (%) |
| `air_quality` | Air quality sensor (%) |
| `humidity` | Humidity sensor (%) |
| `flags` | Raw status flags (int) |
| `is_on` | `True` if unit is running |
| `heating_active` | `True` if heater is active |
| `eco_mode` | `True` if ECO mode is enabled |

---

### KomfoventDiscovery

Auto-discover Komfovent devices on your local network.

```python
from pykomfovent import KomfoventDiscovery

discovery = KomfoventDiscovery(
    subnet="192.168.1.0/24",  # Optional, auto-detected
    timeout=2.0,              # Per-host timeout (default: 2.0)
    max_concurrent=10         # Parallel connections (default: 10)
)

devices = await discovery.discover()
for device in devices:
    print(f"{device.host} - {device.name}")
```

Returns list of `DiscoveredDevice` with `host` and `name` properties.

---

### Schedules

The schedule is a dictionary mapping days to mode/time sequences:

```python
schedule = await client.get_schedule()
# {'p0r0': [1, 360, 2, 1020, 1], 'p0r1': [...], ...}
```

| Format | Description |
|--------|-------------|
| Key: `p0r{day}` | Day of week (0=Monday, 6=Sunday) |
| Value: `[mode, minutes, ...]` | Alternating mode and time from midnight |

**Mode codes:** 1=away, 2=normal, 3=intensive, 4=boost

**Setting a schedule:**

```python
# Monday: away→6:00→normal→17:00→away
await client.set_schedule({
    "p0r0_0": 1,     # Away
    "p0r0_1": 360,   # 6:00
    "p0r0_2": 2,     # Normal
    "p0r0_3": 1020,  # 17:00
    "p0r0_4": 1,     # Away
})
```

---

### Exceptions

| Exception | Description |
|-----------|-------------|
| `KomfoventAuthError` | Invalid credentials |
| `KomfoventConnectionError` | Network or connection issues |
| `KomfoventParseError` | Failed to parse device response |

---

## Examples

### Energy Monitoring

```python
async def monitor_efficiency():
    async with KomfoventClient("192.168.1.100", "user", "pass") as client:
        state = await client.get_state()
        print(f"Efficiency: {state.heat_exchanger_efficiency}%")
        print(f"Power: {state.power_consumption}W")
        print(f"Recovered: {state.heat_recovery_power}W")
```

### Filter Alert

```python
async def check_filter():
    async with KomfoventClient("192.168.1.100", "user", "pass") as client:
        state = await client.get_state()
        if state.filter_contamination and state.filter_contamination > 80:
            print(f"⚠️ Replace filter: {state.filter_contamination}%")
```

### Auto Mode Based on Temperature

```python
async def auto_mode():
    async with KomfoventClient("192.168.1.100", "user", "pass") as client:
        state = await client.get_state()
        if state.outdoor_temp and state.outdoor_temp > 25:
            await client.set_mode("intensive")
        elif state.outdoor_temp and state.outdoor_temp < 5:
            await client.set_mode("normal")
            await client.set_supply_temp(23.0)
```

### Periodic Monitoring

```python
async def monitor_loop():
    async with KomfoventClient("192.168.1.100", "user", "pass") as client:
        while True:
            state = await client.get_state()
            print(f"[{state.mode}] {state.supply_temp}°C / {state.outdoor_temp}°C")
            await asyncio.sleep(60)
```

### Set Workday Schedule

```python
async def set_workday_schedule():
    async with KomfoventClient("192.168.1.100", "user", "pass") as client:
        workday = {
            "0": 1, "1": 360, "2": 2, "3": 480,      # Away→6:00→Normal→8:00
            "4": 1, "5": 1020, "6": 2, "7": 1320,    # Away→17:00→Normal→22:00
            "8": 1                                    # Away
        }
        for day in range(5):  # Mon-Fri
            await client.set_schedule({f"p0r{day}_{k}": v for k, v in workday.items()})
```

---

## Error Handling

```python
from pykomfovent import KomfoventClient, KomfoventAuthError, KomfoventConnectionError

try:
    async with KomfoventClient("192.168.1.100", "user", "pass") as client:
        state = await client.get_state()
except KomfoventAuthError:
    print("Invalid credentials")
except KomfoventConnectionError as e:
    print(f"Connection failed: {e}")
```

---

## Requirements

- Python 3.11+
- Komfovent C6 ventilation unit with web interface enabled

## License

MIT
