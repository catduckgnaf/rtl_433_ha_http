"""DataUpdateCoordinator for rtl_433_ha_http."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    Rtl433ApiClient,
    Rtl433ApiClientAuthenticationError,
    Rtl433ApiClientError,
)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class Rtl433DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: Rtl433ApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=60),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_data()
        except Rtl433ApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except Rtl433ApiClientError as exception:
            raise UpdateFailed(exception) from exception