"""Price calculation based on appliance data and energy prices."""

import json
from dataclasses import dataclass
from datetime import datetime as dt, timedelta as td
from typing import List

import numpy as np

from .models import ApplianceData, ApplianceCalculations

from .const import LOGGER

SECONDS_PER_HOUR = 60 * 60
EXAMPLLE_PRICES = [
    1.264,
    1.221,
    1.243,
    1.234,
    1.256,
    1.298,
    1.599,
    1.682,
    1.664,
    1.358,
    1.041,
    0.919,
    0.665,
    0.439,
    0.391,
    0.415,
    0.601,
    1.426,
    1.604,
    1.784,
    1.774,
    1.41,
    1.394,
    1.333,
    1.242,
    1.191,
    1.212,
    1.195,
    1.216,
    1.25,
    1.369,
    1.369,
    1.361,
    1.295,
    1.034,
    0.937,
    0.909,
    0.866,
    0.837,
    0.837,
    0.855,
    1.64,
    1.682,
    1.72,
    1.76,
    1.393,
    1.372,
    1.349,
]


@dataclass
class Calculator:
    """Handling all the calculations."""

    appliance_file: str

    def calculate_prices(self, electricity_prices: List[float]):
        """Calculate prices for running appliance."""

        self.electricity_prices = electricity_prices

        with open(self.appliance_file, encoding="utf8") as file:
            data = json.load(file)
            appliance_data = ApplianceData.parse_obj(data)

        # create a numpy array of energy use
        energy_usage_array = np.array(appliance_data.energy_usage)
        energy_usage_length = len(energy_usage_array)

        # create a numpy array of electricity prices
        energy_price_array = np.array(self.electricity_prices)

        # convert energy prices array to a resolution matching energy usage
        energy_price_array = np.repeat(
            energy_price_array,
            (SECONDS_PER_HOUR / appliance_data.energy_use_resolution_in_seconds),
        )

        # create windows of energy prices of length matching duration of appliance
        energy_price_windows = np.lib.stride_tricks.sliding_window_view(
            energy_price_array, energy_usage_length
        )

        # calculate price for each point in the windows
        calculated_prices = energy_price_windows * energy_usage_array

        # sum the prices for each row in the windows
        summed_prices = calculated_prices.sum(axis=1)

        # create dict with datetime as key and price as value
        summed_prices_dict_dt = {}
        for idx, price in enumerate(summed_prices):
            summed_prices_dict_dt[
                self.idx_to_dt(idx, appliance_data.energy_use_resolution_in_seconds)
            ] = price

        summed_prices_dict_price = dict(
            sorted(summed_prices_dict_dt.items(), key=lambda item: item[1])
        )

        # calculate attributes
        lowest_price = np.min(summed_prices)
        lowest_price_dt = self.idx_to_dt(
            np.argmin(summed_prices), appliance_data.energy_use_resolution_in_seconds
        )

        highest_price = np.max(summed_prices)
        highest_price_dt = self.idx_to_dt(
            np.argmax(summed_prices), appliance_data.energy_use_resolution_in_seconds
        )

        price_diff = highest_price - lowest_price

        latest_start_time = self.idx_to_dt(
            len(summed_prices) - 1, appliance_data.energy_use_resolution_in_seconds
        )

        # return above calculations as a dict
        results = {
            "prices_by_price": summed_prices_dict_price,
            "lowest_price": lowest_price,
            "lowest_price_dt": lowest_price_dt,
            "highest_price": highest_price,
            "highest_price_dt": highest_price_dt,
            "price_difference": price_diff,
            "latest_start_time": latest_start_time,
            "energy_use_resolution_in_seconds": appliance_data.energy_use_resolution_in_seconds
        }

        result_model = ApplianceCalculations.parse_obj(results)
        LOGGER.debug("---  ---  Calculations was made  ---  ---")
        return result_model

    def idx_to_dt(self, idx: int, energy_use_resolution_in_seconds: int):
        """Converts index of array to a datetime."""
        idx = int(idx)
        start_of_day = dt.today().replace(hour=0, minute=0, second=0, microsecond=0)
        return start_of_day + td(seconds=(idx * energy_use_resolution_in_seconds))


if __name__ == "__main__":
    inf = Calculator("data/electrolux/eeq47200l.json").calculate_prices(EXAMPLLE_PRICES)
    print(inf)
