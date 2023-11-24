"""config flow for rtl_433."""
from datetime import timedelta
# import aiohttp
# import async_timeout
# import asyncio
import json
import websocket

from homeassistant import config_entries, HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import Rtl433ApiClient, Rtl433ApiClientAuthenticationError, Rtl433ApiClientCommunicationError, Rtl433ApiClientError

from .const import DOMAIN, LOGGER

# Define Rtl433DataUpdateCoordinator class
class Rtl433DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: config_entries.ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: Rtl433ApiClient,
        http_host: str,
        http_port: int,
    ) -> None:
        """Initialize."""
        self.client = client
        self.http_host = http_host
        self.http_port = http_port
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
            for event in self.ws_events():
                # Process each JSON event
                self.handle_event(event)

        except Rtl433ApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(f"Authentication error: {exception}") from exception
        except Rtl433ApiClientCommunicationError as exception:
            raise UpdateFailed(f"Communication error: {exception}") from exception
        except Rtl433ApiClientError as exception:
            raise UpdateFailed(f"API error: {exception}") from exception

    def ws_events(self):
        """Generator function to yield JSON events from rtl_433's WebSocket API."""
        url = f'ws://{self.http_host}:{self.http_port}/ws'
        ws = websocket.WebSocket()
        ws.connect(url)

        # You will receive JSON events, one per message.
        self.logger.info(f'Connected to {url}')

        while True:
            yield ws.recv()

    def handle_event(self, line):
        """Handle each JSON event."""
        try:
            # Decode the message as JSON
            data = json.loads(line)

            # Change for your custom handling below, this is a simple example
            label = data["model"]
            if "channel" in data:
                label += ".CH" + str(data["channel"])
            elif "id" in data:
                label += ".ID" + str(data["id"])

            # E.g. match `model` and `id` to a descriptive name.
            if data["model"] == "LaCrosse-TX" and data["id"] == 123:
                label = "Living Room"

            if "battery_ok" in data:
                if data["battery_ok"] == 0:
                    self.logger.warning(label + ' Battery empty!')

            if "temperature_C" in data:
                self.logger.info(label + ' Temperature ' + str(data["temperature_C"]))

            if "humidity" in data:
                self.logger.info(label + ' Humidity ' + str(data["humidity"]))

        except KeyError:
            # Ignore unknown message data and continue
            pass

        except ValueError as e:
            # Warn on decoding errors
            self.logger.warning(f'Event format not recognized: {e}')

# Import Rtl433ApiClient if it's in a different file

# config_flow.py
class Rtl433FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Rtl433."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""

        self.hass.data.setdefault(DOMAIN, {})
        self.hass.data[DOMAIN][self.entry.entry_id] = coordinator = Rtl433DataUpdateCoordinator(
            hass=self.hass,
            client=Rtl433ApiClient(  # Import this or define it
                host=self.entry.data[CONF_HOST],
                port=self.entry.data[CONF_PORT],
                session=async_get_clientsession(self.hass),
            ),

        )
