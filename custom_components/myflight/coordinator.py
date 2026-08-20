"""Data update coordinator for myFlight."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MyFlightApi, MyFlightApiError, client_session
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MyFlightCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll /api/ha/status on a fixed interval."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: MyFlightApi,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        session = client_session(self.hass)
        try:
            return await self.api.async_get_status(session)
        except MyFlightApiError as err:
            if self.data:
                _LOGGER.warning(
                    "myFlight update failed, keeping last snapshot: %s", err
                )
                return self.data
            raise UpdateFailed(str(err)) from err
