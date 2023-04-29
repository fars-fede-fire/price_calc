"""Helpers for coordinator."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    async_get,
    RegistryEntry,
)


def get_platform(hass: HomeAssistant, entity_id: str):
    entity_registry: EntityRegistry = async_get(hass)
    entities = entity_registry.entities
    entry: RegistryEntry = entities.get(entity_id)
    platform = entry.platform
    return platform
