"""Binary sensor platform for rtl_433_ha_http."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDevice,
    BinarySensorEntityDescription,
)
from homeassistant.const import DEVICE_CLASS_CONNECTIVITY

from .const import DOMAIN
from .coordinator import Rtl433UpdateCoordinator
from .entity import Rtl433Entity

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="rtl_433_ha_http",
        name="Integration For RTL_433",
        device_class=DEVICE_CLASS_CONNECTIVITY,
    ),
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        Rtl433BinarySensor(coordinator, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )

class Rtl433BinarySensor(Rtl433Entity, BinarySensorDevice):
    """rtl_433_ha_http binary_sensor class."""

    def __init__(
        self,
        coordinator: Rtl433UpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        # Modify this condition according to your actual data
        return self.coordinator.data.get("title", "") == "foo"
