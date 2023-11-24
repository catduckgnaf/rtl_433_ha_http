"""Configuration flow for Rtl433."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PORT, CONF_HOST
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import (
    Rtl433ApiClient,
    Rtl433ApiClientAuthenticationError,
    Rtl433ApiClientCommunicationError,
    Rtl433ApiClientError,
)
from .const import DOMAIN, LOGGER

class Rtl433FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Rtl433."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    host=user_input[CONF_HOST],
                    port=user_input[CONF_PORT],
                )
            except Rtl433ApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except Rtl433ApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except Rtl433ApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="host",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default="192.168.0.100",
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(
                        CONF_PORT,
                        default=9443,
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.INT
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(self, host: str, port: str) -> None:
        """Validate credentials."""
        client = Rtl433ApiClient(
            host=host,
            port=port,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
