"""Models for price_calc."""

from datetime import datetime

from pydantic import BaseModel


class ApplianceData(BaseModel):
    """Class representing appliance data."""

    appliance_type: str
    mode: str
    duration_minutes: int
    energy_use_resolution_in_seconds: int
    measurement_method: str
    energy_usage: list


class ApplianceCalculations(BaseModel):
    """Class representing calculations of appliance."""

    prices: dict
    lowest_price: float
    lowest_price_dt: datetime
    highest_price: float
    highest_price_dt: datetime
    price_difference: float
