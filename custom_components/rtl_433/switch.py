"""Switch platform for rtl_433_ha_http."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from .const import DOMAIN
from .coordinator import Rtl433DataUpdateCoordinator
from .entity import Rtl433Entity
import logging
import logging

ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="rtl_433_ha_http",
        name="Integration Switch",
        icon="mdi:format-quote-close",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        Rtl433Switch(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class Rtl433Switch(Rtl433Entity, SwitchEntity):
    """rtl_433_ha_http switch class."""

    def __init__(
        self,
        coordinator: Rtl433DataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.coordinator.data.get("title", "") == "bar"

    _LOGGER = logging.getLogger(__name__)


    async def async_turn_on(self, **kwargs: any) -> None:
        """Turn on the switch."""
        try:
            await self.coordinator.api.async_set_title("bar")
            await self.coordinator.async_request_refresh()
        except Exception as e:
            logging.error(f"Error turning on the switch: {e}")

    async def async_turn_off(self, **kwargs: any) -> None:
        """Turn off the switch."""
        try:
            await self.coordinator.api.async_set_title("foo")
            await self.coordinator.async_request_refresh()
        except Exception as e:
            logging.error(f"Error turning off the switch: {e}")
            self._LOGGER.error(f"Error turning off the switch: {e}")
