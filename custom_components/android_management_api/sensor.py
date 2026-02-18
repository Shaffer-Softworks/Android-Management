"""Sensor platform for Android Management API."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AndroidManagementConfigEntry
from .const import DOMAIN
from .coordinator import AndroidManagementCoordinator


@dataclass(frozen=True, kw_only=True)
class AndroidManagementSensorDescription(SensorEntityDescription):
    """Describe an Android Management sensor."""

    value_fn: Callable[[dict[str, Any]], str | None]


def _nested_get(data: dict[str, Any], *keys: str) -> Any:
    """Safely traverse nested dicts."""
    for k in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(k)
        if data is None:
            return None
    return data


SENSOR_DESCRIPTIONS: tuple[AndroidManagementSensorDescription, ...] = (
    AndroidManagementSensorDescription(
        key="state",
        translation_key="device_state",
        name="State",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("state"),
    ),
    AndroidManagementSensorDescription(
        key="management_mode",
        translation_key="management_mode",
        name="Management Mode",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("managementMode"),
    ),
    AndroidManagementSensorDescription(
        key="ownership",
        translation_key="ownership",
        name="Ownership",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("ownership"),
    ),
    AndroidManagementSensorDescription(
        key="policy_name",
        translation_key="policy_name",
        name="Policy Name",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("appliedPolicyName", "").rsplit("/", 1)[-1]
        if d.get("appliedPolicyName")
        else None,
    ),
    AndroidManagementSensorDescription(
        key="api_level",
        translation_key="api_level",
        name="API Level",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: str(d.get("apiLevel")) if d.get("apiLevel") else None,
    ),
    AndroidManagementSensorDescription(
        key="enrollment_time",
        translation_key="enrollment_time",
        name="Enrollment Time",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("enrollmentTime"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AndroidManagementConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    coordinator = entry.runtime_data

    entities: list[AndroidManagementSensor] = []
    for device_id, device_data in coordinator.data.items():
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                AndroidManagementSensor(coordinator, device_id, description)
            )

    async_add_entities(entities)


class AndroidManagementSensor(
    CoordinatorEntity[AndroidManagementCoordinator], SensorEntity
):
    """Representation of an Android Management sensor."""

    entity_description: AndroidManagementSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AndroidManagementCoordinator,
        device_id: str,
        description: AndroidManagementSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this sensor."""
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
    def native_value(self) -> str | None:
        """Return the sensor value."""
        device_data = self.coordinator.data.get(self._device_id, {})
        return self.entity_description.value_fn(device_data)
