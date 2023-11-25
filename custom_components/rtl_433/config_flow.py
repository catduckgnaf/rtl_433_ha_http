"""config flow for rtl_433."""
from datetime import timedelta
import websocket

from homeassistant import config_entries, core
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import Rtl433ApiClient, Rtl433ApiClientAuthenticationError, Rtl433ApiClientCommunicationError, Rtl433ApiClientError
from .const import DOMAIN, LOGGER
from homeassistant.helpers import vol

# Define Rtl433DataUpdateCoordinator class
class Rtl433DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: core.HomeAssistant, client: Rtl433ApiClient, ws_url: str) -> None:
        """Initialize."""
        self.client = client
        self.ws_url = ws_url
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=60),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # Connect to rtl_433's HTTP WebSocket API
            ws = websocket.WebSocket()
            ws.connect(self.ws_url)

            # Process each JSON event
            for event in self.ws_events(ws):
                self.handle_event(event)

        except Rtl433ApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(f"Authentication error: {exception}") from exception
        except Rtl433ApiClientCommunicationError as exception:
            raise UpdateFailed(f"Communication error: {exception}") from exception
        except Rtl433ApiClientError as exception:
            raise UpdateFailed(f"API error: {exception}") from exception

    def ws_events(self, ws):
        """Generate function via websocket"""
        self.logger.info(f'Connected to {self.ws_url}')

        while True:
            yield ws.recv()

# Config flow for Rtl433
class Rtl433FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Rtl433."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=self.user_schema()
            )

        # Assuming you have a function to validate user input
        errors = await self._validate_user_input(user_input)

        if not errors:
            return self.async_create_entry(
                title="Rtl433",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=self.user_schema(), errors=errors
        )


    async def _validate_user_input(self, user_input):
        """Validate user input."""
        # Implement your validation logic here
        errors = []
        return errors

    def user_schema(self):
        """Return the data schema for user input."""
        return {
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT): int,
        }
