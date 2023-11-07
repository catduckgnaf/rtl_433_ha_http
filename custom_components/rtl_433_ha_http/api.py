"""rtl_433 http ws API Client."""
from __future__ import annotations

import asyncio
import websocket
import json
from time import sleep
import websocket-client
import aiohttp
import async_timeout


class Rtl433ApiClientError(Exception):
    """Exception to indicate a general API error."""


class Rtl433ApiClientCommunicationError(
    Rtl433ApiClientError
):
    """Exception to indicate a communication error."""


# class rtl433ApiClientAuthenticationError(
  #  Rtl433ApiClientError
#):
#    """Exception to indicate an authentication error."""


class Rtl433ApiClient:
    """rtl_433 http ws API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get", url="https://jsonplaceholder.typicode.com/posts/1"
        )

    async def async_set_title(self, value: str) -> any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
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
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
              #      raise Rtl433ApiClientAuthenticationError(
                        "Invalid credentials",
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            raise Rtl433ApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise Rtl433ApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise Rtl433ApiClientError(
                "Something really wrong happened!"
            ) from exception
