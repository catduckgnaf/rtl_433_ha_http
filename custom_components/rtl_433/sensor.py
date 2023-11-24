"""Sensor platform for rtl_433_ha_http."""
from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import DOMAIN
from .coordinator import Rtl433DataUpdateCoordinator
from .entity import Rtl433Entity

_LOGGER = logging.getLogger(__name__)

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="rtl_433_ha_http",
        name="Integration Sensor",
        icon="mdi:format-quote-close",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        Rtl433Sensor(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class Rtl433Sensor(Rtl433Entity, SensorEntity):
    """rtl_433_ha_http Sensor class."""

    def __init__(
        self,
        coordinator: Rtl433DataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        return self.coordinator.data.get("body")

    async def async_update(self):
        """Update the sensor."""
        try:
            # Fetch new data here, if needed
            # new_data = await self.coordinator.client.async_get_data()
            # Update the native value with the new data
            # self.coordinator.data = new_data
            pass
        except Exception as e:
            _LOGGER.error(f"Error updating sensor: {e}")
