"""Button platform for Android Management API."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import Any, Optional

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
from .const import CONF_CLEAR_APP_DATA_PACKAGES, DOMAIN
from .coordinator import AndroidManagementCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class AndroidManagementButtonDescription(ButtonEntityDescription):
    """Describe an Android Management button."""

    press_fn: Optional[
        Callable[
            [HomeAssistant, AndroidManagementAPIClient, str], Awaitable[Any]
        ]
    ] = None


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


async def _relinquish_ownership(
    hass: HomeAssistant, client: AndroidManagementAPIClient, device_name: str
) -> None:
    await client.async_issue_command(hass, device_name, "RELINQUISH_OWNERSHIP")


async def _clear_app_data(
    hass: HomeAssistant,
    client: AndroidManagementAPIClient,
    device_name: str,
    package_names: list[str],
) -> None:
    """Clear app data for given packages. Caller must supply non-empty list."""
    if not package_names:
        _LOGGER.warning(
            "Clear app data: no package names configured. Set "
            "'Clear app data package names' in integration options (General)."
        )
        return
    await client.async_issue_command(
        hass,
        device_name,
        "CLEAR_APP_DATA",
        clearAppsDataParams={"packageNames": package_names},
    )


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
    AndroidManagementButtonDescription(
        key="relinquish_ownership",
        name="Relinquish Ownership",
        icon="mdi:account-off",
        entity_category=EntityCategory.CONFIG,
        press_fn=_relinquish_ownership,
    ),
    AndroidManagementButtonDescription(
        key="clear_app_data",
        name="Clear app data",
        icon="mdi:delete-sweep",
        entity_category=EntityCategory.CONFIG,
        press_fn=None,  # Handled in entity using options
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
                AndroidManagementButton(
                    coordinator, device_id, description, entry
                )
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
        entry: AndroidManagementConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._entry = entry
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
        desc = self.entity_description
        if desc.key == "clear_app_data":
            raw = self._entry.options.get(CONF_CLEAR_APP_DATA_PACKAGES, "")
            packages = [
                p.strip()
                for p in raw.replace(",", "\n").splitlines()
                if p.strip()
            ]
            await _clear_app_data(
                self.hass,
                self.coordinator.client,
                self._full_device_name,
                packages,
            )
        elif desc.press_fn is not None:
            await desc.press_fn(
                self.hass,
                self.coordinator.client,
                self._full_device_name,
            )
        await self.coordinator.async_request_refresh()
