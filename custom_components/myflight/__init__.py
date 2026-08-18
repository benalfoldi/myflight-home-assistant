"""myFlight Home Assistant integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.typing import ConfigType

from .api import MyFlightApi
from .const import (
    CONF_AIRPORT,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_TRACK_REGISTRATION,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SERVICE_REFRESH,
    SERVICE_SET_AIRPORT,
    SERVICE_SET_TRACK,
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


def _conf(entry: ConfigEntry) -> dict[str, Any]:
    return {**entry.data, **entry.options}


def _build_api(entry: ConfigEntry) -> MyFlightApi:
    conf = _conf(entry)
    return MyFlightApi(
        conf[CONF_URL],
        conf[CONF_API_KEY],
        conf[CONF_USERNAME],
        airport=conf.get(CONF_AIRPORT),
        track_registration=conf.get(CONF_TRACK_REGISTRATION),
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = _build_api(entry)
    coordinator = MyFlightCoordinator(
        hass,
        api,
        int(_conf(entry).get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    _register_services(hass)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _entry_for_entity(hass: HomeAssistant, entity_id: str | None) -> ConfigEntry | None:
    if entity_id:
        registry = er.async_get(hass)
        rec = registry.async_get(entity_id)
        if rec and rec.unique_id:
            for entry_id in hass.data.get(DOMAIN, {}):
                if rec.unique_id.startswith(entry_id):
                    return hass.config_entries.async_get_entry(entry_id)
    entries = hass.config_entries.async_entries(DOMAIN)
    return entries[0] if len(entries) == 1 else None


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_REFRESH):
        return

    async def _handle_refresh(call: ServiceCall) -> None:
        entry = _entry_for_entity(hass, call.data.get("entity_id"))
        targets = [entry] if entry else list(hass.config_entries.async_entries(DOMAIN))
        for item in targets:
            if not item:
                continue
            stored = hass.data.get(DOMAIN, {}).get(item.entry_id)
            if stored:
                await stored["coordinator"].async_request_refresh()

    async def _handle_set_track(call: ServiceCall) -> None:
        entry = _entry_for_entity(hass, call.data.get("entity_id"))
        if entry is None:
            return
        registration = (call.data.get("registration") or "").strip().upper()
        options = {**entry.options, CONF_TRACK_REGISTRATION: registration}
        hass.config_entries.async_update_entry(entry, options=options)

    async def _handle_set_airport(call: ServiceCall) -> None:
        entry = _entry_for_entity(hass, call.data.get("entity_id"))
        if entry is None:
            return
        airport = (call.data.get("airport") or "").strip().upper()
        options = {**entry.options, CONF_AIRPORT: airport}
        hass.config_entries.async_update_entry(entry, options=options)

    hass.services.async_register(DOMAIN, SERVICE_REFRESH, _handle_refresh)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_TRACK,
        _handle_set_track,
        schema=vol.Schema(
            {
                vol.Optional("entity_id"): cv.string,
                vol.Required("registration"): cv.string,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_AIRPORT,
        _handle_set_airport,
        schema=vol.Schema(
            {
                vol.Optional("entity_id"): cv.string,
                vol.Required("airport"): cv.string,
            }
        ),
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
