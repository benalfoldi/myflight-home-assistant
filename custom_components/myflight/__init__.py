"""myFlight Home Assistant integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import MyFlightApi
from .const import (
    CONF_AIRPORT,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_TRACK_REGISTRATION,
    CONF_USERNAME,
    DOMAIN,
    SERVICE_REFRESH,
)
from .coordinator import MyFlightCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.DEVICE_TRACKER,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = MyFlightApi(
        entry.data[CONF_URL],
        entry.data[CONF_API_KEY],
        entry.data[CONF_USERNAME],
        airport=entry.data.get(CONF_AIRPORT),
        track_registration=entry.data.get(CONF_TRACK_REGISTRATION),
    )
    coordinator = MyFlightCoordinator(
        hass,
        api,
        entry.data.get(CONF_SCAN_INTERVAL, 60),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _handle_refresh(call: Any) -> None:
        await coordinator.async_request_refresh()

    if not hass.services.has_service(DOMAIN, SERVICE_REFRESH):
        hass.services.async_register(DOMAIN, SERVICE_REFRESH, _handle_refresh)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
