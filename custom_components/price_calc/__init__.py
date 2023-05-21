"""
Custom integration to integrate price calc with Home Assistant.

For more details about this integration, please refer to
https://github.com/fars-fede-fire/price_calc
"""
from __future__ import annotations

from asyncio import sleep
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_FILE_PATH
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.dt import now

from homeassistant.components.recorder import history, get_instance

from .const import (
    CONF_SOURCE_SENSOR,
    DOMAIN,
    LOGGER,
    EDS_TODAY,
    EDS_TOMORROW,
    EDS_TOMORROW_VALID,
)
from .coordinator import (
    PriceCalcUpdateCoordinator,
    PriceCalcData,
    price_now,
)
from .price_calc import Calculator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up price calc from a config entry."""
    appliance_file = entry.data[CONF_FILE_PATH]
    while hass.states.get(entry.data[CONF_SOURCE_SENSOR]) is None:
        LOGGER.debug("Waiting for 'Energi Data Service' to fetch data")
        await sleep(3)

    if (
        hass.states.get(entry.data[CONF_SOURCE_SENSOR]).attributes[
            EDS_TOMORROW_VALID
        ]
        is True
    ):
        electricity_prices = (
            hass.states.get(entry.data[CONF_SOURCE_SENSOR]).attributes[EDS_TODAY]
            + hass.states.get(entry.data[CONF_SOURCE_SENSOR]).attributes[
                EDS_TOMORROW
            ]
        )

    else:
        electricity_prices = hass.states.get(
            entry.data[CONF_SOURCE_SENSOR]
        ).attributes[EDS_TODAY]

    price_calc = Calculator(appliance_file=appliance_file).calculate_prices(
        electricity_prices
    )

    coordinator: DataUpdateCoordinator = PriceCalcUpdateCoordinator(hass, entry)

    coordinator.async_set_updated_data(
        PriceCalcData(
            calcs=price_calc,
            updated=price_now(
                price_calc.prices_by_price,
                now(),
                price_calc.latest_start_time,
                price_calc.energy_use_resolution_in_seconds
            ),
        )
    )


    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload price calc config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        del hass.data[DOMAIN][entry.entry_id]
    return unload_ok
