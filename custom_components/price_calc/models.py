"""Models for price_calc."""

from datetime import datetime

from pydantic import BaseModel


class ApplianceData(BaseModel):
    """Class representing appliance data."""

    appliance_type: str
    appliance_manufactor: str
    appliance_model: str
    appliance_mode: str
    measure_method: str
    duration_in_minutes: int
    energy_use_resolution_in_seconds: int
    energy_usage: list


class ApplianceCalculations(BaseModel):
    """Class representing calculations of appliance."""

    prices_by_price: dict
    lowest_price: float
    lowest_price_dt: datetime
    highest_price: float
    highest_price_dt: datetime
    price_difference: float
    latest_start_time: datetime
    energy_use_resolution_in_seconds: int


class ApplianceCalculationsCoordinator(BaseModel):
    """Class representing calculations of appliance during runtime."""

    current_time: datetime
    current_price: float
    next_lowest_price_dt: datetime
    next_low_price: float
    diff_now_and_next_lowest: float
    delay_hours: int
    delay_hours_price: float
    diff_now_and_delay: float
