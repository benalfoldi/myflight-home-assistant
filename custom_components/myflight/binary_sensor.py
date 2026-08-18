"""Binary sensors for myFlight."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MyFlightCoordinator
from .entity import MyFlightEntity


class MyFlightBinarySensor(MyFlightEntity, BinarySensorEntity):
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
    def is_on(self) -> bool:
        return bool(self._status.get(self._field))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MyFlightCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            MyFlightBinarySensor(
                coordinator,
                entry.entry_id,
                "has_roster_changes",
                "has_roster_changes",
                "mdi:bell-alert",
            ),
            MyFlightBinarySensor(
                coordinator,
                entry.entry_id,
                "has_partner_flight",
                "has_partner_flight",
                "mdi:airplane",
            ),
        ]
    )
