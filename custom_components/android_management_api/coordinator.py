"""DataUpdateCoordinator for Android Management API."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AndroidManagementAPIClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AndroidManagementCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinator that polls the Android Management API for device data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AndroidManagementAPIClient,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch device list from the API and key by device ID."""
        try:
            devices = await self.client.async_list_devices(self.hass)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Android Management API: {err}") from err

        result: dict[str, dict[str, Any]] = {}
        for device in devices:
            name: str = device.get("name", "")
            device_id = name.rsplit("/", 1)[-1] if "/" in name else name
            result[device_id] = device
        return result

    def get_device_id(self, device_name: str) -> str:
        """Extract the device ID (last path segment) from a full resource name."""
        return device_name.rsplit("/", 1)[-1] if "/" in device_name else device_name
