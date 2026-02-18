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
    # --- Top-level fields ---
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
        key="applied_policy_version",
        translation_key="applied_policy_version",
        name="Applied Policy Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: str(d.get("appliedPolicyVersion"))
        if d.get("appliedPolicyVersion")
        else None,
    ),
    AndroidManagementSensorDescription(
        key="policy_compliant",
        translation_key="policy_compliant",
        name="Policy Compliant",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: str(d.get("policyCompliant"))
        if d.get("policyCompliant") is not None
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
    AndroidManagementSensorDescription(
        key="last_policy_sync_time",
        translation_key="last_policy_sync_time",
        name="Last Policy Sync",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("lastPolicySyncTime"),
    ),
    AndroidManagementSensorDescription(
        key="last_status_report_time",
        translation_key="last_status_report_time",
        name="Last Status Report",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("lastStatusReportTime"),
    ),
    # --- Software info ---
    AndroidManagementSensorDescription(
        key="android_version",
        translation_key="android_version",
        name="Android Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "softwareInfo", "androidVersion"),
    ),
    AndroidManagementSensorDescription(
        key="security_patch_level",
        translation_key="security_patch_level",
        name="Security Patch Level",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "softwareInfo", "securityPatchLevel"),
    ),
    AndroidManagementSensorDescription(
        key="android_build_number",
        translation_key="android_build_number",
        name="Build Number",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "softwareInfo", "androidBuildNumber"),
    ),
    AndroidManagementSensorDescription(
        key="device_kernel_version",
        translation_key="device_kernel_version",
        name="Kernel Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "softwareInfo", "deviceKernelVersion"),
    ),
    AndroidManagementSensorDescription(
        key="bootloader_version",
        translation_key="bootloader_version",
        name="Bootloader Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "softwareInfo", "bootloaderVersion"),
    ),
    AndroidManagementSensorDescription(
        key="device_policy_version",
        translation_key="device_policy_version",
        name="Device Policy Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(
            d, "softwareInfo", "androidDevicePolicyVersionName"
        ),
    ),
    AndroidManagementSensorDescription(
        key="primary_language",
        translation_key="primary_language",
        name="Primary Language",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "softwareInfo", "primaryLanguageCode"),
    ),
    AndroidManagementSensorDescription(
        key="system_update_status",
        translation_key="system_update_status",
        name="System Update Status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(
            d, "softwareInfo", "systemUpdateInfo", "updateStatus"
        ),
    ),
    # --- Hardware info ---
    AndroidManagementSensorDescription(
        key="brand",
        translation_key="brand",
        name="Brand",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "hardwareInfo", "brand"),
    ),
    AndroidManagementSensorDescription(
        key="hardware",
        translation_key="hardware",
        name="Hardware",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "hardwareInfo", "hardware"),
    ),
    AndroidManagementSensorDescription(
        key="baseband_version",
        translation_key="baseband_version",
        name="Baseband Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "hardwareInfo", "deviceBasebandVersion"),
    ),
    # --- Network info ---
    AndroidManagementSensorDescription(
        key="imei",
        translation_key="imei",
        name="IMEI",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "networkInfo", "imei"),
    ),
    AndroidManagementSensorDescription(
        key="wifi_mac_address",
        translation_key="wifi_mac_address",
        name="WiFi MAC Address",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "networkInfo", "wifiMacAddress"),
    ),
    AndroidManagementSensorDescription(
        key="network_operator",
        translation_key="network_operator",
        name="Network Operator",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "networkInfo", "networkOperatorName"),
    ),
    # --- Security posture ---
    AndroidManagementSensorDescription(
        key="security_posture",
        translation_key="security_posture",
        name="Security Posture",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: _nested_get(d, "securityPosture", "devicePosture"),
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
