"""Base entity for the price calc integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_FILE_PATH, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.event import (
    async_track_state_change,
    async_track_time_change,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import CONF_SOURCE_SENSOR, DOMAIN, LOGGER
from .coordinator import PriceCalcUpdateCoordinator
from .models import ApplianceCalculations


class PriceCalcEntity(CoordinatorEntity[PriceCalcUpdateCoordinator]):
    """Defines a price calc entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PriceCalcUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the price calc entity."""
        super().__init__(coordinator=coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, f"{entry.data[CONF_FILE_PATH]}_{entry.data[CONF_NAME]}")
            },
            manufacturer="Price calc",
            name="Price calc",
        )
