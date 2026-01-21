from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KomfoventState:
    mode: str
    supply_temp: float | None
    extract_temp: float | None
    outdoor_temp: float | None
    supply_temp_setpoint: float | None
    extract_temp_setpoint: float | None
    supply_fan_percent: float | None
    extract_fan_percent: float | None
    supply_fan_intensity: float | None
    extract_fan_intensity: float | None
    heat_exchanger_percent: float | None
    electric_heater_percent: float | None
    filter_contamination: float | None
    heat_exchanger_efficiency: float | None
    heat_recovery_power: float | None
    power_consumption: float | None
    heating_power: float | None
    spi_actual: float | None
    spi_daily: float | None
    energy_consumed_daily: float | None
    energy_consumed_monthly: float | None
    energy_consumed_total: float | None
    energy_heating_daily: float | None
    energy_heating_monthly: float | None
    energy_heating_total: float | None
    energy_recovered_daily: float | None
    energy_recovered_monthly: float | None
    energy_recovered_total: float | None
    air_quality: float | None
    humidity: float | None
    flags: int

    @property
    def is_on(self) -> bool:
        return bool(self.mode and self.mode.upper() not in ("OFF", "WYŁĄCZONY", "WYLACZONY", ""))

    @property
    def heating_active(self) -> bool:
        return (self.electric_heater_percent or 0) > 0 or (self.heating_power or 0) > 0

    @property
    def eco_mode(self) -> bool:
        return bool(self.flags & (1 << 2))
