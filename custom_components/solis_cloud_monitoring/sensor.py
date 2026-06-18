"""Sensor platform for Solis Cloud Monitoring."""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, MANUFACTURER
from .coordinator import SolisCloudDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SolisSensorEntityDescription(SensorEntityDescription):
    """Describes Solis sensor entity."""

    value_fn: Callable[[dict[str, Any]], StateType]
    

def _coerce_float(value: Any) -> float | None:
    """Convert API values to floats when possible."""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# Define all sensor types
SENSOR_TYPES: tuple[SolisSensorEntityDescription, ...] = (
    # Power Sensors
    SolisSensorEntityDescription(
        key="current_power",
        translation_key="current_power",
        name="Current Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _coerce_float(data.get("pac")),
    ),
    SolisSensorEntityDescription(
        key="dc_power",
        translation_key="dc_power",
        name="DC Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _coerce_float(data.get("dcPac")),
    ),
    # Energy Sensors
    SolisSensorEntityDescription(
        key="energy_today",
        translation_key="energy_today",
        name="Energy Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("eToday")),
    ),
    SolisSensorEntityDescription(
        key="energy_month",
        translation_key="energy_month",
        name="Energy This Month",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("eMonth")),
    ),
    SolisSensorEntityDescription(
        key="energy_year",
        translation_key="energy_year",
        name="Energy This Year",
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda data: _coerce_float(data.get("eYear")),
    ),
    SolisSensorEntityDescription(
        key="energy_total",
        translation_key="energy_total",
        name="Total Energy",
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        value_fn=lambda data: _coerce_float(data.get("eTotal")),
    ),
    # PV String Monitoring
    SolisSensorEntityDescription(
        key="pv1_voltage",
        translation_key="pv1_voltage",
        name="PV String 1 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("uPv1")),
    ),
    SolisSensorEntityDescription(
        key="pv1_current",
        translation_key="pv1_current",
        name="PV String 1 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("iPv1")),
    ),
    SolisSensorEntityDescription(
        key="pv1_power",
        translation_key="pv1_power",
        name="PV String 1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _coerce_float(data.get("pow1")),
    ),
    # Grid Monitoring
    SolisSensorEntityDescription(
        key="grid_voltage",
        translation_key="grid_voltage",
        name="Grid Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("uAc1")),
    ),
    SolisSensorEntityDescription(
        key="grid_current",
        translation_key="grid_current",
        name="Grid Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("iAc1")),
    ),
    SolisSensorEntityDescription(
        key="grid_frequency",
        translation_key="grid_frequency",
        name="Grid Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _coerce_float(data.get("fac")),
    ),
    # Status and Diagnostics
    SolisSensorEntityDescription(
        key="inverter_temperature",
        translation_key="inverter_temperature",
        name="Inverter Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("inverterTemperature")),
    ),
    SolisSensorEntityDescription(
        key="daily_runtime",
        translation_key="daily_runtime",
        name="Generation Hours Today",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda data: _coerce_float(data.get("fullHour")),
    ),
    SolisSensorEntityDescription(
        key="inverter_state",
        translation_key="inverter_state",
        name="Inverter Status",
        device_class=SensorDeviceClass.ENUM,
        options=["sleeping", "offline", "standby", "generating"],
        value_fn=lambda data: {
            "0": "sleeping",
            "1": "offline",
            "2": "standby",
            "3": "generating",
        }.get(str(data.get("currentState")), "offline"),
    ),
    SolisSensorEntityDescription(
        key="fault_description",
        translation_key="fault_description",
        name="Fault/Status Description",
        value_fn=lambda data: data.get("faultCodeDesc"),
    ),
    SolisSensorEntityDescription(
        key="insulation_resistance",
        translation_key="insulation_resistance",
        name="Insulation Resistance",
        native_unit_of_measurement="MΩ",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("insulationResistance")),
    ),
    # Grid — Real-time Power
    SolisSensorEntityDescription(
        key="grid_active_power",
        translation_key="grid_active_power",
        name="Grid Active Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        # Solis psum convention is inverted vs HA: negate to match HA (positive = importing)
        value_fn=lambda data: v * -1 if (v := _coerce_float(data.get("psum"))) is not None else None,
    ),
    SolisSensorEntityDescription(
        key="grid_meter_voltage",
        translation_key="grid_meter_voltage",
        name="Grid Meter Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("uA")),
    ),
    SolisSensorEntityDescription(
        key="grid_meter_current",
        translation_key="grid_meter_current",
        name="Grid Meter Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("iA")),
    ),
    SolisSensorEntityDescription(
        key="reactive_power",
        translation_key="reactive_power",
        name="Reactive Power",
        native_unit_of_measurement=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
        device_class=SensorDeviceClass.REACTIVE_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: _coerce_float(data.get("reactivePower")),
    ),
    SolisSensorEntityDescription(
        key="power_factor",
        translation_key="power_factor",
        name="Power Factor",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _coerce_float(data.get("powerFactor")),
    ),
    # Grid — Import Energy
    SolisSensorEntityDescription(
        key="grid_import_today",
        translation_key="grid_import_today",
        name="Grid Import Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("gridPurchasedTodayEnergy")),
    ),
    SolisSensorEntityDescription(
        key="grid_import_month",
        translation_key="grid_import_month",
        name="Grid Import This Month",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("gridPurchasedMonthEnergy")),
    ),
    SolisSensorEntityDescription(
        key="grid_import_year",
        translation_key="grid_import_year",
        name="Grid Import This Year",
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        value_fn=lambda data: _coerce_float(data.get("gridPurchasedYearEnergy")),
    ),
    SolisSensorEntityDescription(
        key="grid_import_total",
        translation_key="grid_import_total",
        name="Grid Import Lifetime",
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        value_fn=lambda data: _coerce_float(data.get("gridPurchasedTotalEnergy")),
    ),
    # Grid — Export Energy
    SolisSensorEntityDescription(
        key="grid_export_today",
        translation_key="grid_export_today",
        name="Grid Export Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("gridSellTodayEnergy")),
    ),
    SolisSensorEntityDescription(
        key="grid_export_month",
        translation_key="grid_export_month",
        name="Grid Export This Month",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("gridSellMonthEnergy")),
    ),
    SolisSensorEntityDescription(
        key="grid_export_year",
        translation_key="grid_export_year",
        name="Grid Export This Year",
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        value_fn=lambda data: _coerce_float(data.get("gridSellYearEnergy")),
    ),
    SolisSensorEntityDescription(
        key="grid_export_total",
        translation_key="grid_export_total",
        name="Grid Export Lifetime",
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        value_fn=lambda data: _coerce_float(data.get("gridSellTotalEnergy")),
    ),
    # Home Consumption
    SolisSensorEntityDescription(
        key="home_load_power",
        translation_key="home_load_power",
        name="Home Load Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda data: _coerce_float(data.get("familyLoadPower")),
    ),
    SolisSensorEntityDescription(
        key="home_load_today",
        translation_key="home_load_today",
        name="Home Consumption Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("homeLoadTodayEnergy")),
    ),
    SolisSensorEntityDescription(
        key="home_load_month",
        translation_key="home_load_month",
        name="Home Consumption This Month",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("homeLoadMonthEnergy")),
    ),
    SolisSensorEntityDescription(
        key="home_load_year",
        translation_key="home_load_year",
        name="Home Consumption This Year",
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        value_fn=lambda data: _coerce_float(data.get("homeLoadYearEnergy")),
    ),
    SolisSensorEntityDescription(
        key="home_load_total",
        translation_key="home_load_total",
        name="Home Consumption Lifetime",
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
        value_fn=lambda data: _coerce_float(data.get("homeLoadTotalEnergy")),
    ),
    # Self-sufficiency
    SolisSensorEntityDescription(
        key="self_sufficiency",
        translation_key="self_sufficiency",
        name="Solar Self-sufficiency",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("oneSelf")),
    ),
    SolisSensorEntityDescription(
        key="self_consumption",
        translation_key="self_consumption",
        name="Solar Self-consumption",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: _coerce_float(data.get("familyLoadPercent")),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Solis Cloud sensors from a config entry."""
    coordinator: SolisCloudDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SolisCloudSensor] = []
    
    # Create sensors for each inverter
    for serial in coordinator.inverter_serials:
        for description in SENSOR_TYPES:
            entities.append(
                SolisCloudSensor(
                    coordinator,
                    description,
                    serial,
                )
            )

    async_add_entities(entities)


class SolisCloudSensor(CoordinatorEntity[SolisCloudDataUpdateCoordinator], SensorEntity):
    """Representation of a Solis Cloud sensor."""

    entity_description: SolisSensorEntityDescription
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SolisCloudDataUpdateCoordinator,
        description: SolisSensorEntityDescription,
        serial_number: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._serial_number = serial_number
        
        # Use last 4 digits of serial for entity ID
        serial_suffix = serial_number[-4:]
        
        # Set unique ID
        self._attr_unique_id = f"{serial_number}_{description.key}"
        
        # Set entity ID with readable format
        self._attr_object_id = f"solis_{serial_suffix}_{description.key}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        if self._serial_number not in self.coordinator.data:
            return {}
            
        data = self.coordinator.data[self._serial_number]
        model = data.get("model", "Unknown")
        machine = data.get("machine", "Unknown")
        
        return {
            "identifiers": {(DOMAIN, self._serial_number)},
            "name": f"Solis Inverter {self._serial_number[-4:]}",
            "manufacturer": MANUFACTURER,
            "model": f"{machine} ({model})",
            "sw_version": data.get("version"),
            "serial_number": self._serial_number,
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self._serial_number not in self.coordinator.data:
            return None
            
        data = self.coordinator.data[self._serial_number]
        return self.entity_description.value_fn(data)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self._serial_number in self.coordinator.data
        )
