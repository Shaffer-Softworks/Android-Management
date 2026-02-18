"""Device tracker platform for Android Management API."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AndroidManagementConfigEntry
from .const import DOMAIN
from .coordinator import AndroidManagementCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AndroidManagementConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up device tracker entities from a config entry."""
    coordinator = entry.runtime_data

    async_add_entities(
        AndroidManagementTracker(coordinator, device_id)
        for device_id in coordinator.data
    )


class AndroidManagementTracker(
    CoordinatorEntity[AndroidManagementCoordinator], TrackerEntity
):
    """Representation of an Android managed device as a tracker entity."""

    _attr_has_entity_name = True
    _attr_name = "Status"

    def __init__(
        self,
        coordinator: AndroidManagementCoordinator,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_tracker"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_data = self.coordinator.data.get(self._device_id, {})
        hw_info = device_data.get("hardwareInfo", {})
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=hw_info.get("model", self._device_id),
            manufacturer=hw_info.get("manufacturer"),
            model=hw_info.get("model"),
            serial_number=hw_info.get("serialNumber"),
        )

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS

    @property
    def is_connected(self) -> bool:
        """Return true if the device state is ACTIVE."""
        device_data = self.coordinator.data.get(self._device_id, {})
        return device_data.get("state") == "ACTIVE"

    @property
    def location_name(self) -> str | None:
        """Map state to home/not_home."""
        return "home" if self.is_connected else "not_home"
