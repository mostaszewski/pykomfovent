import re
import xml.etree.ElementTree as ET

from pykomfovent.models import KomfoventState


class KomfoventParseError(Exception):
    pass


_NUM_PATTERN = re.compile(r"(-?\d+(?:\.\d+)?)")


def _parse_float(value: str) -> float | None:
    value = value.strip()
    if not value or value.startswith("*") or value.startswith("#") or value.startswith("--."):
        return None
    match = _NUM_PATTERN.search(value)
    return float(match.group(1)) if match else None


def _get_text(root: ET.Element, tag: str) -> str:
    el = root.find(tag)
    return el.text.strip() if el is not None and el.text else ""


def _get_int(root: ET.Element, tag: str) -> int:
    text = _get_text(root, tag)
    if not text:
        return 0
    match = _NUM_PATTERN.search(text)
    return int(match.group(1).split(".")[0]) if match else 0


def _get_float(root: ET.Element, tag: str) -> float | None:
    return _parse_float(_get_text(root, tag))


def parse_state(main_xml: bytes, detail_xml: bytes) -> KomfoventState:
    try:
        main = ET.fromstring(main_xml.decode("windows-1250"))
        detail = ET.fromstring(detail_xml.decode("windows-1250"))
    except ET.ParseError as e:
        raise KomfoventParseError(f"Failed to parse XML: {e}") from e

    return KomfoventState(
        mode=_get_text(main, "OMO"),
        supply_temp=_get_float(main, "AI0"),
        extract_temp=_get_float(main, "AI1"),
        outdoor_temp=_get_float(main, "AI2"),
        supply_temp_setpoint=_get_float(main, "ST"),
        extract_temp_setpoint=_get_float(main, "ET"),
        supply_fan_percent=_get_float(main, "SAF"),
        extract_fan_percent=_get_float(main, "EAF"),
        supply_fan_intensity=_get_float(detail, "SFI"),
        extract_fan_intensity=_get_float(detail, "EFI"),
        heat_exchanger_percent=_get_float(detail, "HE"),
        electric_heater_percent=_get_float(detail, "EH"),
        filter_contamination=_get_float(main, "FCG"),
        heat_exchanger_efficiency=_get_float(main, "EC1"),
        heat_recovery_power=_get_float(main, "EC2"),
        power_consumption=_get_float(main, "EC3"),
        heating_power=_get_float(main, "EC4"),
        spi_actual=_get_float(main, "EC5A"),
        spi_daily=_get_float(main, "EC5D"),
        energy_consumed_daily=_get_float(main, "EC6D"),
        energy_consumed_monthly=_get_float(main, "EC6M"),
        energy_consumed_total=_get_float(main, "EC6T"),
        energy_heating_daily=_get_float(main, "EC7D"),
        energy_heating_monthly=_get_float(main, "EC7M"),
        energy_heating_total=_get_float(main, "EC7T"),
        energy_recovered_daily=_get_float(main, "EC8D"),
        energy_recovered_monthly=_get_float(main, "EC8M"),
        energy_recovered_total=_get_float(main, "EC8T"),
        air_quality=_get_float(main, "AQ"),
        humidity=_get_float(main, "AH"),
        flags=_get_int(main, "VF"),
    )
