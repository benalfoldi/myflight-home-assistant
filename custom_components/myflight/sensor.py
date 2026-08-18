"""Sensor platform for myFlight."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import MyFlightCoordinator
from .entity import MyFlightEntity

# Keep attribute keys lean enough for HA's state machine.
_STATUS_ATTR_KEYS = (
    "version",
    "last_updated",
    "profile",
    "next_duty",
    "roster_changes",
    "roster_changes_count",
    "partner_accounts",
    "partner_flight",
    "mission",
    "flight_track",
    "live_fleet",
    "airport_stats",
    "next_duty_date",
    "airborne_count",
    "partner_status",
    "has_roster_changes",
    "has_partner_flight",
)


class MyFlightStatusSensor(MyFlightEntity, SensorEntity):
    """Master sensor; Lovelace cards read attributes."""

    def __init__(self, coordinator: MyFlightCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_translation_key = "status"
        self._attr_unique_id = f"{entry_id}_status"
        self._attr_icon = "mdi:airplane"
        self.entity_id = "sensor.myflight_status"

    @property
    def native_value(self) -> StateType:
        value = self._status.get("state") or "idle"
        return str(value)[:255]

    @property
    def extra_state_attributes(self) -> dict:
        data = self._status
        return {key: data.get(key) for key in _STATUS_ATTR_KEYS}


class MyFlightTextSensor(MyFlightEntity, SensorEntity):
    def __init__(
        self,
        coordinator: MyFlightCoordinator,
        entry_id: str,
        field: str,
        translation_key: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._field = field
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{entry_id}_{field}"
        self._attr_icon = icon

    @property
    def native_value(self) -> StateType:
        value = self._status.get(self._field)
        if value is None:
            return None
        return str(value)[:255]


class MyFlightCountSensor(MyFlightEntity, SensorEntity):
    def __init__(
        self,
        coordinator: MyFlightCoordinator,
        entry_id: str,
        field: str,
        translation_key: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._field = field
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{entry_id}_{field}"
        self._attr_icon = icon

    @property
    def native_value(self) -> StateType:
        value = self._status.get(self._field)
        if value is None:
            nested = (self._status.get("live_fleet") or {}).get("airborne")
            if self._field == "airborne_count" and nested is not None:
                return int(nested)
            return 0
        return int(value)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MyFlightCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            MyFlightStatusSensor(coordinator, entry.entry_id),
            MyFlightTextSensor(
                coordinator, entry.entry_id, "next_duty_date", "next_duty_date", "mdi:calendar"
            ),
            MyFlightCountSensor(
                coordinator,
                entry.entry_id,
                "roster_changes_count",
                "roster_changes_count",
                "mdi:bell-alert",
            ),
            MyFlightCountSensor(
                coordinator, entry.entry_id, "airborne_count", "airborne_count", "mdi:airplane"
            ),
            MyFlightTextSensor(
                coordinator,
                entry.entry_id,
                "partner_status",
                "partner_status",
                "mdi:account-heart",
            ),
        ]
    )
