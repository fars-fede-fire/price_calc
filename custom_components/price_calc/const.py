"""Constants for Price calculator."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Price calculator"
DOMAIN = "price_calc"

CONF_HISTORY_SENSOR = "history_sensor"
CONF_SOURCE_SENSOR = "source_sensor"
CONF_START_TIME = "start_time"
CONF_END_TIME = "end_time"
CONF_MODE = 'mode'
CONF_MEASURE_METHOD = 'measure_method'
CONF_TYPE = 'type'
CONF_MODEL = "model"
CONF_MANUFACTOR = 'manufactor'
CONF_FILE_SELECTOR = 'file_selector'
CONF_ADD_PRICE_DATA = 'add_price_data'

EDS_TODAY = "today"
EDS_TOMORROW = "tomorrow"
EDS_TOMORROW_VALID = "tomorrow_valid"
