"""Support for price calc sensors."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict


from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_FILE_PATH
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .coordinator import PriceCalcUpdateCoordinator, PriceCalcData
from .const import DOMAIN, LOGGER, CONF_ADD_PRICE_DATA
from .entity import PriceCalcEntity


@dataclass
class PriceCalcEntityMixin:
    """Mixin values for price calc entities."""

    value_fn: Callable[[PriceCalcData], float]
    attrs: Dict[str, Callable[[PriceCalcData], Any]]


@dataclass
class PriceCalcSensorEntityDescription(SensorEntityDescription, PriceCalcEntityMixin):
    """Price calc sensor description."""

    key: str
    has_entity_name: bool = False
    device_class = SensorDeviceClass.MONETARY
    icon: str = "mdi:timer-play-outline"
    native_unit_of_measurement = SensorDeviceClass.MONETARY


SENSORS = [
    PriceCalcSensorEntityDescription(
        key="price_now",
        value_fn=lambda x: round(x.updated.current_price,2),
        attrs={
            "current_time": lambda x: x.updated.current_time,
            "next_lowest": lambda x: x.updated.next_lowest_price_dt,
            "next_lowest price": lambda x: x.updated.next_low_price,
            "diff_now_and_next_lowest": lambda x: x.updated.diff_now_and_next_lowest,
            "delay_hours": lambda x: x.updated.delay_hours,
            "delay_hours_price": lambda x: x.updated.delay_hours_price,
            "diff_now_and_delay": lambda x: x.updated.diff_now_and_delay,
            "todays_highest": lambda x: x.calcs.highest_price,
            "today_highest_time": lambda x: x.calcs.highest_price_dt,
            "todays_lowest": lambda x: x.calcs.lowest_price,
            "todays_lowest_time": lambda x: x.calcs.lowest_price_dt
        },
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup price calc entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities(
        PriceCalcSensor(coordinator, description, entry) for description in SENSORS
    )


class PriceCalcSensor(PriceCalcEntity, SensorEntity):
    """Representation of Price calc sensor."""

    entity_description: PriceCalcSensorEntityDescription

    def __init__(
        self,
        coordinator: PriceCalcUpdateCoordinator,
        description: PriceCalcSensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)

        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{entry.data[CONF_NAME]}_{entry.data[CONF_FILE_PATH]}"
        self._attr_name = f"{entry.data[CONF_NAME]}"

    @property
    def native_value(self) -> date | None:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        attr = {}
        for key in self.entity_description.attrs:
            attr[key] = self.entity_description.attrs[key](self.coordinator.data)
        if self.coordinator.config_entry.data[CONF_ADD_PRICE_DATA] is True:
            attr['price_data'] = self.coordinator.data.calcs.prices_by_price

        return attr
