"""HTTP client for the myFlight Home Assistant status API."""

from __future__ import annotations

from typing import Any

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_PUSH_PATH, API_STATUS_PATH


class MyFlightApiError(Exception):
    """Raised when the myFlight API returns an error."""


class MyFlightApi:
    """Thin wrapper around GET /api/ha/status."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        username: str,
        *,
        airport: str | None = None,
        track_registration: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._username = username
        self._airport = (airport or "").strip().upper() or None
        self._track_registration = (track_registration or "").strip().upper() or None

    def _params(self) -> dict[str, str]:
        params = {"username": self._username}
        if self._airport:
            params["airport"] = self._airport
        if self._track_registration:
            params["track_registration"] = self._track_registration
        return params

    async def async_get_status(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        url = f"{self._base_url}{API_STATUS_PATH}"
        headers = {"X-API-Key": self._api_key}
        try:
            async with session.get(
                url,
                headers=headers,
                params=self._params(),
                timeout=aiohttp.ClientTimeout(total=45),
            ) as response:
                if response.status == 403:
                    raise MyFlightApiError("Invalid API key")
                if response.status == 404:
                    raise MyFlightApiError("Unknown user")
                if response.status == 503:
                    raise MyFlightApiError("HA API not configured")
                if response.status >= 400:
                    body = await response.text()
                    raise MyFlightApiError(f"HTTP {response.status}: {body[:200]}")
                return await response.json()
        except TimeoutError as err:
            raise MyFlightApiError(str(err) or "Request timed out") from err
        except aiohttp.ClientError as err:
            raise MyFlightApiError(str(err)) from err

    async def async_push_webhook(self, session: aiohttp.ClientSession) -> None:
        url = f"{self._base_url}{API_PUSH_PATH}"
        headers = {"X-API-Key": self._api_key}
        async with session.post(
            url,
            headers=headers,
            params=self._params(),
            timeout=aiohttp.ClientTimeout(total=45),
        ) as response:
            if response.status >= 400:
                body = await response.text()
                raise MyFlightApiError(
                    f"Push failed HTTP {response.status}: {body[:200]}"
                )


def client_session(hass) -> aiohttp.ClientSession:
    """Return Home Assistant's shared aiohttp session."""
    return async_get_clientsession(hass)
