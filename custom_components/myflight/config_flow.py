"""Config flow for myFlight."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MyFlightApi, MyFlightApiError
from .const import (
    CONF_AIRPORT,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_TRACK_REGISTRATION,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_USERNAME): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=3600)
        ),
        vol.Optional(CONF_AIRPORT, default=""): str,
        vol.Optional(CONF_TRACK_REGISTRATION, default=""): str,
    }
)


def _normalize_url(url: str) -> str:
    value = url.strip().rstrip("/")
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("invalid_url")
    return value


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    url = _normalize_url(data[CONF_URL])
    username = (data.get(CONF_USERNAME) or "").strip()
    if not username:
        raise ValueError("invalid_username")
    airport = (data.get(CONF_AIRPORT) or "").strip().upper()
    track = (data.get(CONF_TRACK_REGISTRATION) or "").strip().upper()
    api = MyFlightApi(
        url,
        data[CONF_API_KEY],
        username,
        airport=airport or None,
        track_registration=track or None,
    )
    session = async_get_clientsession(hass)
    await api.async_get_status(session)
    return {
        CONF_URL: url,
        CONF_USERNAME: username,
        CONF_AIRPORT: airport,
        CONF_TRACK_REGISTRATION: track,
    }


class MyFlightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for myFlight."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                normalized = await _validate_input(self.hass, user_input)
            except ValueError as err:
                key = str(err)
                if key == "invalid_url":
                    errors[CONF_URL] = "invalid_url"
                elif key == "invalid_username":
                    errors[CONF_USERNAME] = "invalid_username"
                else:
                    errors["base"] = "cannot_connect"
            except MyFlightApiError as err:
                message = str(err)
                if "Invalid API key" in message:
                    errors[CONF_API_KEY] = "invalid_api_key"
                elif "Unknown user" in message:
                    errors[CONF_USERNAME] = "unknown_user"
                else:
                    errors["base"] = "cannot_connect"
            else:
                unique = f"{normalized[CONF_URL]}|{normalized[CONF_USERNAME]}"
                await self.async_set_unique_id(unique)
                self._abort_if_unique_id_configured()
                title = f"myFlight ({normalized[CONF_USERNAME]})"
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_URL: normalized[CONF_URL],
                        CONF_API_KEY: user_input[CONF_API_KEY],
                        CONF_USERNAME: normalized[CONF_USERNAME],
                        CONF_SCAN_INTERVAL: user_input.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                        CONF_AIRPORT: normalized[CONF_AIRPORT],
                        CONF_TRACK_REGISTRATION: normalized[CONF_TRACK_REGISTRATION],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return MyFlightOptionsFlow()


class MyFlightOptionsFlow(config_entries.OptionsFlow):
    """Airport, tracker ID, and poll interval after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        current = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            airport = (user_input.get(CONF_AIRPORT) or "").strip().upper()
            track = (user_input.get(CONF_TRACK_REGISTRATION) or "").strip().upper()
            return self.async_create_entry(
                title="",
                data={
                    CONF_AIRPORT: airport,
                    CONF_TRACK_REGISTRATION: track,
                    CONF_SCAN_INTERVAL: user_input.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                },
            )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=3600)
                    ),
                    vol.Optional(
                        CONF_AIRPORT, default=current.get(CONF_AIRPORT, "")
                    ): str,
                    vol.Optional(
                        CONF_TRACK_REGISTRATION,
                        default=current.get(CONF_TRACK_REGISTRATION, ""),
                    ): str,
                }
            ),
        )
