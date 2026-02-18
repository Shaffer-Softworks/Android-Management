"""Button platform for Android Management API."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AndroidManagementConfigEntry
from .api import AndroidManagementAPIClient
from .const import DOMAIN
from .coordinator import AndroidManagementCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class AndroidManagementButtonDescription(ButtonEntityDescription):
    """Describe an Android Management button."""

    press_fn: Callable[
        [HomeAssistant, AndroidManagementAPIClient, str], Awaitable[Any]
    ]


async def _reboot(
    hass: HomeAssistant, client: AndroidManagementAPIClient, device_name: str
) -> None:
    await client.async_issue_command(hass, device_name, "REBOOT")


async def _lock(
    hass: HomeAssistant, client: AndroidManagementAPIClient, device_name: str
) -> None:
    await client.async_issue_command(hass, device_name, "LOCK")


async def _reset_password(
    hass: HomeAssistant, client: AndroidManagementAPIClient, device_name: str
) -> None:
    await client.async_issue_command(hass, device_name, "RESET_PASSWORD")


async def _wipe(
    hass: HomeAssistant, client: AndroidManagementAPIClient, device_name: str
) -> None:
    await client.async_delete_device(
        hass, device_name, wipe_data_flags=["WIPE_EXTERNAL_STORAGE"]
    )


async def _unenroll(
    hass: HomeAssistant, client: AndroidManagementAPIClient, device_name: str
) -> None:
    await client.async_delete_device(hass, device_name)


BUTTON_DESCRIPTIONS: tuple[AndroidManagementButtonDescription, ...] = (
    AndroidManagementButtonDescription(
        key="reboot",
        name="Reboot",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
        press_fn=_reboot,
    ),
    AndroidManagementButtonDescription(
        key="lock",
        name="Lock",
        icon="mdi:lock",
        entity_category=EntityCategory.CONFIG,
        press_fn=_lock,
    ),
    AndroidManagementButtonDescription(
        key="reset_password",
        name="Reset Password",
        icon="mdi:lock-reset",
        entity_category=EntityCategory.CONFIG,
        press_fn=_reset_password,
    ),
    AndroidManagementButtonDescription(
        key="factory_reset",
        name="Factory Reset",
        icon="mdi:cellphone-erase",
        entity_category=EntityCategory.CONFIG,
        press_fn=_wipe,
    ),
    AndroidManagementButtonDescription(
        key="unenroll",
        name="Unenroll",
        icon="mdi:cellphone-remove",
        entity_category=EntityCategory.CONFIG,
        press_fn=_unenroll,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AndroidManagementConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities from a config entry."""
    coordinator = entry.runtime_data

    entities: list[AndroidManagementButton] = []
    for device_id in coordinator.data:
        for description in BUTTON_DESCRIPTIONS:
            entities.append(
                AndroidManagementButton(coordinator, device_id, description)
            )

    async_add_entities(entities)


class AndroidManagementButton(
    CoordinatorEntity[AndroidManagementCoordinator], ButtonEntity
):
    """Representation of an Android Management command button."""

    entity_description: AndroidManagementButtonDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AndroidManagementCoordinator,
        device_id: str,
        description: AndroidManagementButtonDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this button."""
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
    def _full_device_name(self) -> str:
        """Return the full API resource name for this device."""
        device_data = self.coordinator.data.get(self._device_id, {})
        return device_data.get("name", "")

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(
            self.hass, self.coordinator.client, self._full_device_name
        )
        await self.coordinator.async_request_refresh()
