"""Sensor of price_calc."""
from __future__ import annotations

import os

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import CONF_NAME
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_SOURCE_SENSOR, LOGGER, CONF_APPLIANCE_FILE
from .helpers.coordinator import get_platform

from .price_calc import Calculator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize price calc."""
    registry = er.async_get(hass)
    source_entity_id = er.async_validate_entity_id(
        registry, config_entry.options[CONF_SOURCE_SENSOR]
    )
    appliance_file = config_entry.options[CONF_APPLIANCE_FILE]

    prices = PriceSensor(
        name=config_entry.title,
        source_entity=source_entity_id,
    )

    LOGGER.debug(get_platform(hass, entity_id=config_entry.options[CONF_SOURCE_SENSOR]))
    LOGGER.debug(source_entity_id)
    LOGGER.debug(os.listdir(os.getcwd()))
    price_state = hass.states.get(source_entity_id)
    LOGGER.debug(price_state.attributes["tomorrow"])

    calc = Calculator(
        appliance_file=appliance_file,
        electricity_prices=price_state.attributes["today"],
    )

    LOGGER.debug(calc.calculate_prices())

    async_add_entities([prices])


async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup price calc sensor."""
    prices = PriceSensor(
        name=config.get(CONF_NAME), source_entity=config[CONF_SOURCE_SENSOR]
    )

    async_add_entities([prices])


class PriceSensor(SensorEntity):
    """Representation of a price calc sensor."""

    _attr_should_poll = False

    def __init__(self, *, name: str | None, source_entity: str) -> None:
        """Initialize price calc sensor."""
        self._sensor_source_id = source_entity
        self._attr_name = name
        self._attr_icon = "mdi:chart-histogram"

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

    @property
    def native_value(self):
        return 5
