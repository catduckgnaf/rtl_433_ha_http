"""rtl_433 Home Assistant http API Integration."""

from __future__ import annotations

import aiohttp
import async_timeout
import asyncio
import socket
import json
import websocket

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .api import (
    Rtl433ApiClient,
    Rtl433ApiClientAuthenticationError,
    Rtl433ApiClientCommunicationError,
    Rtl433ApiClientError,
)
from .const import CONF_HOST, CONF_PORT, DOMAIN, LOGGER

class Rtl433DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ConfigEntry

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


# Usage example in your setup_entry method
class Rtl433FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Rtl433."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        # ... (your existing code)

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator = Rtl433DataUpdateCoordinator(
            hass=hass,
            client=Rtl433ApiClient(
                host=entry.data[CONF_HOST],
                port=entry.data[CONF_PORT],
                session=async_get_clientsession(hass),
            ),
            http_host=entry.data[CONF_HOST],  # Adjust as needed
            http_port=entry.data[CONF_PORT],  # Adjust as needed
        )

        # ... (your existing code)


class Rtl433ApiClientError(Exception):
    """Base exception for RTL_433 API Client errors."""


class Rtl433ApiClientCommunicationError(Rtl433ApiClientError):
    """Exception to indicate a communication error."""

class Rtl433ApiClientAuthenticationError(Rtl433ApiClientError):
    """Exception to indicate an authentication error."""

class Rtl433ApiClient:
    """rtl_433 http ws API Client."""

    def __init__(
        self,
        host: str,
        port: int,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._port = port
        self._session = session

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get", url=f"http://{self._host}:{self._port}/ws"
        )

    async def async_set_title(self, value: str) -> any:
        """Set title data in the API."""
        return await self._api_wrapper(
            method="patch",
            url=f"http://{self._host}:{self._port}/ws",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> any:
        """Wrap API requests."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    # Uncomment if needed in the future
                    # raise Rtl433ApiClientAuthenticationError("Invalid credentials")
                    response.raise_for_status()
                return await response.json()

        except KeyError:
            # Ignore unknown message data and continue
            pass

        except ValueError as e:
            # Warn on decoding errors
            self.logger.warning(f'Event format not recognized: {e}')

