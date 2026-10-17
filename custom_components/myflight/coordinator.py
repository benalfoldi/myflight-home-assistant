"""Data update coordinator for myFlight."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MyFlightApi, MyFlightApiError, client_session
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
_PARTIAL_RETRY_S = 8.0


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
        self._partial_retry: asyncio.Task[None] | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        session = client_session(self.hass)
        try:
            data = await self.api.async_get_status(session)
        except MyFlightApiError as err:
            if self.data:
                _LOGGER.warning(
                    "myFlight update failed, keeping last snapshot: %s", err
                )
                return self.data
            raise UpdateFailed(str(err)) from err
        if data.get("live_loading"):
            self._schedule_partial_retry()
        return data

    def _schedule_partial_retry(self) -> None:
        if self._partial_retry and not self._partial_retry.done():
            return

        async def _retry() -> None:
            await asyncio.sleep(_PARTIAL_RETRY_S)
            await self.async_request_refresh()

        self._partial_retry = self.hass.async_create_task(_retry())
