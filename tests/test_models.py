from pykomfovent.models import KomfoventState


def _make_state(**kwargs) -> KomfoventState:
    defaults = {
        "mode": "NORMALNY",
        "supply_temp": 20.6,
        "extract_temp": 23.2,
        "outdoor_temp": 5.4,
        "supply_temp_setpoint": 21.0,
        "extract_temp_setpoint": None,
        "supply_fan_percent": 50.0,
        "extract_fan_percent": 50.0,
        "supply_fan_intensity": 50.0,
        "extract_fan_intensity": 50.0,
        "heat_exchanger_percent": 6.0,
        "electric_heater_percent": 0.0,
        "filter_contamination": 47.0,
        "heat_exchanger_efficiency": 83.0,
        "heat_recovery_power": 243.0,
        "power_consumption": 63.0,
        "heating_power": 0.0,
        "spi_actual": 0.36,
        "spi_daily": 0.35,
        "energy_consumed_daily": 1.21,
        "energy_consumed_monthly": 42.13,
        "energy_consumed_total": 204.73,
        "energy_heating_daily": 0.0,
        "energy_heating_monthly": 0.0,
        "energy_heating_total": 0.04,
        "energy_recovered_daily": 3.23,
        "energy_recovered_monthly": 184.40,
        "energy_recovered_total": 1285.67,
        "air_quality": 25.0,
        "humidity": 25.0,
        "flags": 0,
    }
    defaults.update(kwargs)
    return KomfoventState(**defaults)


def test_state_creation() -> None:
    state = _make_state(flags=203571212)
    assert state.mode == "NORMALNY"
    assert state.supply_temp == 20.6
    assert state.filter_contamination == 47.0


def test_state_with_none_values() -> None:
    state = _make_state(
        mode="POZA DOMEM",
        supply_temp=None,
        extract_temp=None,
        supply_fan_percent=None,
    )
    assert state.supply_temp is None


def test_is_on_true() -> None:
    assert _make_state(mode="NORMALNY").is_on is True
    assert _make_state(mode="INTENSYWNY").is_on is True


def test_is_on_false() -> None:
    assert _make_state(mode="").is_on is False
    assert _make_state(mode="OFF").is_on is False
    assert _make_state(mode="WYŁĄCZONY").is_on is False


def test_heating_active_with_heater() -> None:
    assert _make_state(electric_heater_percent=50.0).heating_active is True


def test_heating_active_with_power() -> None:
    assert _make_state(heating_power=100.0).heating_active is True


def test_heating_active_false() -> None:
    assert _make_state(electric_heater_percent=0.0, heating_power=0.0).heating_active is False
    assert _make_state(electric_heater_percent=None, heating_power=None).heating_active is False


def test_eco_mode() -> None:
    assert _make_state(flags=4).eco_mode is True
    assert _make_state(flags=0).eco_mode is False
    assert _make_state(flags=5).eco_mode is True
