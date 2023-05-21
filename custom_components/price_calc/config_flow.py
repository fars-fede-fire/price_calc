"""Adds config flow for Price calculator integration."""
from __future__ import annotations

import json
import os

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.recorder import history, get_instance
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_NAME, CONF_FILE_PATH, CONF_URL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector
from homeassistant.util.dt import as_local, parse_datetime

from .const import (
    DOMAIN,
    CONF_SOURCE_SENSOR,
    LOGGER,
    CONF_HISTORY_SENSOR,
    CONF_START_TIME,
    CONF_END_TIME,
    CONF_MODE,
    CONF_MEASURE_METHOD,
    CONF_TYPE,
    CONF_MODEL,
    CONF_MANUFACTOR,
    CONF_FILE_SELECTOR,
    CONF_ADD_PRICE_DATA
)

from .cal import prepare_data
from .models import ApplianceData

HISTORY_SOURCE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TYPE): selector.TextSelector(),
        vol.Required(CONF_MANUFACTOR): selector.TextSelector(),
        vol.Required(CONF_MODEL): selector.TextSelector(),
        vol.Required(CONF_MODE): selector.TextSelector(),
        vol.Required(CONF_MEASURE_METHOD): selector.TextSelector(),
        vol.Required(CONF_HISTORY_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=SENSOR_DOMAIN)
        ),
        vol.Required(
            CONF_START_TIME
        ): selector.DateTimeSelector(selector.DateTimeSelectorConfig()),
        vol.Required(
            CONF_END_TIME
        ): selector.DateTimeSelector(selector.DateTimeSelectorConfig()),
    }
)

def get_files():
    """Function to get files from data dir"""
    data_dir = f"{os.path.dirname(__file__)}/data"
    files = [file for file in os.listdir(data_dir) if file.endswith('.json')]
    return files

FILES_IN_DATA_DIR = get_files()

FILE_SOURCE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_FILE_SELECTOR): selector.SelectSelector(selector.SelectSelectorConfig(options=FILES_IN_DATA_DIR)),

    }
)
URL_SOURCE_SCHEMA = vol.Schema({
    vol.Required(CONF_URL): selector.TextSelector(selector.TextSelectorConfig(type='url'))
})

ENERGY_PRICE_SCHEMA = vol.Schema(
    {
    vol.Required(CONF_NAME, default='my appliance'): selector.TextSelector(),
    vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(selector.EntitySelectorConfig(domain=SENSOR_DOMAIN)),
    vol.Required(CONF_ADD_PRICE_DATA): selector.BooleanSelector()
    }
)


class PriceCalcConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Price calc config flow."""

    def __init__(self) -> None:
        self.device = None

    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
    #    return super().async_get_options_flow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}

        if user_input is not None:
            LOGGER.debug("User initiated config_flow")

        return self.async_show_menu(
            step_id="user",
            menu_options={
                "from_sensor_history": "From sensor history",
                "from_file": "From file",
                "from_url": "From URL",
            },
        )

    async def async_step_from_sensor_history(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Setup Price calc from sensor history."""

        errors = {}

        if user_input is not None:
            if user_input[CONF_START_TIME] < user_input[CONF_END_TIME]:
                start_time = as_local(parse_datetime(user_input[CONF_START_TIME]))
                end_time = as_local(parse_datetime(user_input[CONF_END_TIME]))
                entity_id = [user_input[CONF_HISTORY_SENSOR]]
                filters = None
                include_start_time_state = True
                significant_changes_only = False
                minimal_response = True

                history_data = await get_instance(self.hass).async_add_executor_job(
                    history.get_significant_states,
                    self.hass,
                    start_time,
                    end_time,
                    entity_id,
                    filters,
                    include_start_time_state,
                    significant_changes_only,
                    minimal_response,
                )

                filtered_items = [item for item in history_data.get(entity_id[0]) if isinstance(item, dict) and 'friendly_name' not in item]
                self.file_path = prepare_data(user_input[CONF_MANUFACTOR], user_input[CONF_MODEL],user_input[CONF_TYPE], user_input[CONF_MODE], user_input[CONF_MEASURE_METHOD], filtered_items)

                return await self.async_step_select_energy_price()

        return self.async_show_form(
            step_id="from_sensor_history",
            data_schema=HISTORY_SOURCE_SCHEMA,
            errors=errors,
        )

    async def async_step_from_file(self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        if user_input is not None:
            appliance_file = f"{os.path.dirname(__file__)}/data/{user_input[CONF_FILE_SELECTOR]}"
            try:
                ApplianceData.parse_file(appliance_file)
                self.file_path = appliance_file
                return await self.async_step_select_energy_price()
            except:
                LOGGER.error("File not formatted correctly.")
                return self.async_abort

        return self.async_show_form(step_id='from_file', data_schema=FILE_SOURCE_SCHEMA, errors=errors)

    async def async_step_from_url(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            resp = await session.get(user_input[CONF_URL])
            data = await resp.json(content_type='text/plain')
            try:
                appliance_data = ApplianceData.parse_obj(data)
                data_dir = f"{os.path.dirname(__file__)}/data/"
                file_name = f"{appliance_data.appliance_manufactor}_{appliance_data.appliance_model}_{appliance_data.appliance_mode}"
                file_path = f"{data_dir}{file_name}.json"
                with open(f"{file_path}", "w", encoding='utf-8') as file:
                    file.write(json.dumps(data))
                self.file_path = file_path
                LOGGER.debug("Created file at: %s", file_path )
                return await self.async_step_select_energy_price()
            except:
                LOGGER.error("File not formatted correctly.")
                return self.async_abort


        return self.async_show_form(step_id='from_url', data_schema=URL_SOURCE_SCHEMA, errors=errors)



    async def async_step_select_energy_price(self, user_input: dict[str, Any] | None = None) -> FlowResult:

        errors = {}

        if user_input is not None:
            data = {CONF_SOURCE_SENSOR: user_input[CONF_SOURCE_SENSOR],
                    CONF_FILE_PATH: self.file_path,
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_ADD_PRICE_DATA: user_input[CONF_ADD_PRICE_DATA]}

            return self.async_create_entry(title=user_input[CONF_NAME], data=data)

        return self.async_show_form(step_id='select_energy_price', data_schema=ENERGY_PRICE_SCHEMA, errors=errors)