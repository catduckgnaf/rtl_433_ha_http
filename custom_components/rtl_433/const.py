"""Constants for rtl_433_ha."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "RTL_433 Home Assistant Integration"
DOMAIN = "rtl_433"
PLATFORMS = ['binary_sensor', 'sensor', 'switch']
CONF_HOST = "192.168.0.100"
CONF_PORT = 9443
