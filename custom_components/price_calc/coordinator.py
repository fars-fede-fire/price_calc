"""Coordinator for Price calc."""
from datetime import datetime, timedelta

from dataclasses import dataclass

from homeassistant.const import CONF_FILE_PATH
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import (
    async_track_state_change,
    async_track_time_change,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from homeassistant.util.dt import as_local, now

from .const import (
    CONF_SOURCE_SENSOR,
    LOGGER,
    DOMAIN,
    EDS_TODAY,
    EDS_TOMORROW,
    EDS_TOMORROW_VALID,
)
from .models import (
    ApplianceCalculations,
    ApplianceCalculationsCoordinator,
)
from .price_calc import Calculator


@dataclass
class PriceCalcData:
    """Class holding data of price calc."""

    calcs: ApplianceCalculations
    updated: ApplianceCalculationsCoordinator


class PriceCalcUpdateCoordinator(DataUpdateCoordinator[PriceCalcData]):
    """Update coordinator for price calc."""

    config_entry = ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.config_entry = entry
        self.listeners = []
        self.price_entity_id = hass.states.get(entry.data[CONF_SOURCE_SENSOR])

        if self.price_entity_id.attributes[EDS_TOMORROW_VALID]:
            self.prices = (
                self.price_entity_id.attributes[EDS_TODAY]
                + self.price_entity_id.attributes[EDS_TOMORROW]
            )
        else:
            self.prices = self.price_entity_id.attributes[EDS_TODAY]
        self.calc = Calculator(appliance_file=entry.data[CONF_FILE_PATH])

        self.listeners.append(
            async_track_state_change(
                self.hass,
                [entry.data[CONF_SOURCE_SENSOR]],
                self.update_calculations,
            )
        )
        self.listeners.append(
            async_track_time_change(self.hass, self.time_update, second=[0, 20, 40])
        )

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_FILE_PATH]}",
            update_interval=None,
            update_method=None,
        )

    @callback
    async def update_calculations(self, entity_id, old_state, new_state):
        if (
            old_state.attributes[EDS_TOMORROW_VALID] is False
            and new_state.attributes[EDS_TOMORROW_VALID] is True
        ):
            LOGGER.debug("'Energi Data Service' has data available for tomorrow")
            calculator = self.calc
            new_electricity_prices = (
                new_state.attributes[EDS_TODAY] + new_state.attributes[EDS_TOMORROW]
            )
            new_calculations = calculator.calculate_prices(new_electricity_prices)
            new_prices = price_now(
                new_calculations.prices_by_price,
                now(),
                new_calculations.latest_start_time,
                new_calculations.energy_use_resolution_in_seconds
            )
            self.async_set_updated_data(
                PriceCalcData(calcs=new_calculations, updated=new_prices)
            )

    @callback
    async def time_update(self, datetime):
        LOGGER.debug("--- Time update ---")

        new_data = price_now(
            self.data.calcs.prices_by_price, datetime, self.data.calcs.latest_start_time, self.data.calcs.energy_use_resolution_in_seconds
        )

        self.async_set_updated_data(
            PriceCalcData(calcs=self.data.calcs, updated=new_data)
        )


def price_now(
    data_price: dict, now: datetime, last_start_time: datetime, resolution: int
) -> ApplianceCalculationsCoordinator:
    """Return current data."""
    if resolution > 60:
        current_time = as_local(now).replace(second=0, microsecond=0, minute=0, tzinfo=None)
    else:
        current_time = as_local(now).replace(second=0, microsecond=0, tzinfo=None)
    current_price = data_price[current_time]

    for time in data_price.keys():
        if time >= current_time:
            next_low_price = data_price[time]
            next_lowest_price_dt = time
            break

    hourly_prices = []
    hours_until_last_start = (
        int((last_start_time - current_time).total_seconds()) // 3600
    )

    for delay in range(hours_until_last_start):
        hourly_prices.append({delay: data_price[current_time + timedelta(hours=delay)]})
    delay_hours = min(hourly_prices, key=lambda x: list(x.values())[0])
    delay_hours = list(delay_hours.keys())[0]
    delay_hours_price = data_price[(current_time + timedelta(hours=delay_hours))]

    diff_now_and_next_lowest = abs(current_price - next_low_price)
    diff_now_and_delay = abs(current_price - delay_hours_price)

    resp = {
        "current_time": current_time,
        "current_price": current_price,
        "next_lowest_price_dt": next_lowest_price_dt,
        "next_low_price": next_low_price,
        "diff_now_and_next_lowest": diff_now_and_next_lowest,
        "delay_hours": delay_hours,
        "delay_hours_price": delay_hours_price,
        "diff_now_and_delay": diff_now_and_delay
    }

    return ApplianceCalculationsCoordinator.parse_obj(resp)
