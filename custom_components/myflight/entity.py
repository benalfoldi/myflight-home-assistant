"""Shared entity helpers."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MyFlightCoordinator


class MyFlightEntity(CoordinatorEntity[MyFlightCoordinator]):
    """Base entity for myFlight."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MyFlightCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        profile = (coordinator.data or {}).get("profile") or {}
        name = profile.get("display_name") or profile.get("username") or "myFlight"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"myFlight ({name})",
            manufacturer="myFlight",
            model="Home dashboard",
            configuration_url=None,
        )

    @property
    def _status(self) -> dict:
        return self.coordinator.data or {}
