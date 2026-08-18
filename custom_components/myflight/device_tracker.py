"""GPS device trackers for live myFlight positions."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MyFlightCoordinator
from .entity import MyFlightEntity


def _map_fix(block: dict | None) -> tuple[float | None, float | None, dict]:
    data = block or {}
    mapping = data.get("map") or {}
    lat = mapping.get("latitude")
    lon = mapping.get("longitude")
    attrs = {
        "registration": data.get("registration"),
        "altitude_ft": mapping.get("altitude_ft"),
        "heading": mapping.get("heading"),
        "on_ground": mapping.get("on_ground"),
        "ground_speed_kt": mapping.get("ground_speed_kt"),
        "last_known": mapping.get("last_known"),
    }
    try:
        lat_f = float(lat) if lat is not None else None
        lon_f = float(lon) if lon is not None else None
    except (TypeError, ValueError):
        lat_f = lon_f = None
    return lat_f, lon_f, attrs


class MyFlightAircraftTracker(MyFlightEntity, TrackerEntity):
    def __init__(
        self,
        coordinator: MyFlightCoordinator,
        entry_id: str,
        key: str,
        translation_key: str,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._key = key
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{entry_id}_{key}_tracker"
        self._attr_icon = "mdi:airplane"

    @property
    def source_type(self) -> SourceType | str:
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        lat, _, _ = _map_fix(self._status.get(self._key))
        return lat

    @property
    def longitude(self) -> float | None:
        _, lon, _ = _map_fix(self._status.get(self._key))
        return lon

    @property
    def extra_state_attributes(self) -> dict:
        _, _, attrs = _map_fix(self._status.get(self._key))
        return attrs


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MyFlightCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            MyFlightAircraftTracker(
                coordinator, entry.entry_id, "mission", "mission_aircraft"
            ),
            MyFlightAircraftTracker(
                coordinator, entry.entry_id, "partner_flight", "partner_aircraft"
            ),
            MyFlightAircraftTracker(
                coordinator, entry.entry_id, "flight_track", "tracked_aircraft"
            ),
        ]
    )
