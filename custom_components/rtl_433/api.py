"""rtl_433 http ws API Client."""
from __future__ import annotations

import asyncio
import json
import aiohttp
import async_timeout
import websocket
import socket
from time import sleep


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
        host: str,
        port: int,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._host = host
        self._port = port
        self._session = session

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get", url="http://192.168.250.26:9443/ws"
        )

    async def async_set_title(self, value: str) -> any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="http://192.168.250.26:9443/ws",
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