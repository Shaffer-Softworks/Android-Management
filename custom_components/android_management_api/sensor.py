"""Sensor platform for Android Management API."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

_LOGGER = logging.getLogger(__name__)

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
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


def _device_eid(data: dict[str, Any]) -> str | None:
    """Extract EID from hardwareInfo.euiccChipInfo (object or list)."""
    info = _nested_get(data, "hardwareInfo", "euiccChipInfo")
    if isinstance(info, list):
        for item in info:
            if isinstance(item, dict) and item.get("eid"):
                return item["eid"]
        return None
    if isinstance(info, dict):
        return info.get("eid")
    return None


def _telephony_summary(data: dict[str, Any]) -> str | None:
    """Condense networkInfo.telephonyInfos for a sensor state."""
    infos = _nested_get(data, "networkInfo", "telephonyInfos")
    if not isinstance(infos, list) or not infos:
        return None
    parts: list[str] = []
    for info in infos:
        if not isinstance(info, dict):
            continue
        bits = [
            str(info[k])
            for k in ("carrierName", "phoneNumber", "iccId", "activationState")
            if info.get(k)
        ]
        if bits:
            parts.append("/".join(bits))
    return "; ".join(parts) if parts else str(infos)


def _signing_cert_sha256(data: dict[str, Any]) -> str | None:
    """Prefer SHA-256 signing cert from the first application report."""
    reports = data.get("applicationReports")
    if not isinstance(reports, list) or not reports:
        return None
    first = reports[0]
    if not isinstance(first, dict):
        return None
    for key in (
        "signingKeyCertFingerprintSha256",
        "signerInfo",
    ):
        val = first.get(key)
        if isinstance(val, str) and val:
            return val
        if isinstance(val, list) and val:
            item = val[0]
            if isinstance(item, dict):
                sha = item.get("signingKeyCertFingerprintSha256") or item.get(
                    "sha256"
                )
                if sha:
                    return str(sha)
            elif isinstance(item, str):
                return item
    # Legacy SHA-1 field as last resort
    legacy = first.get("signingKeyCertFingerprints") or first.get(
        "signingKeyCertificateFingerprints"
    )
    if isinstance(legacy, list) and legacy:
        return str(legacy[0])
    return None


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
    # --- Memory info (requires memoryInfoEnabled in policy) ---
    AndroidManagementSensorDescription(
        key="total_ram_mb",
        translation_key="total_ram_mb",
        name="Total RAM (MB)",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            str(int(_nested_get(d, "memoryInfo", "totalRam") or 0) // (1024 * 1024))
            if _nested_get(d, "memoryInfo", "totalRam")
            else None
        ),
    ),
    AndroidManagementSensorDescription(
        key="total_internal_storage_mb",
        translation_key="total_internal_storage_mb",
        name="Total Internal Storage (MB)",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            str(int(_nested_get(d, "memoryInfo", "totalInternalStorage") or 0) // (1024 * 1024))
            if _nested_get(d, "memoryInfo", "totalInternalStorage")
            else None
        ),
    ),
    AndroidManagementSensorDescription(
        key="total_external_storage_mb",
        translation_key="total_external_storage_mb",
        name="Total External Storage (MB)",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            str(int(_nested_get(d, "memoryInfo", "totalExternalStorage") or 0) // (1024 * 1024))
            if _nested_get(d, "memoryInfo", "totalExternalStorage")
            else None
        ),
    ),
    # --- Non-compliance ---
    AndroidManagementSensorDescription(
        key="non_compliance_count",
        translation_key="non_compliance_count",
        name="Non-Compliance Count",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: str(len(d.get("nonComplianceDetails", [])))
        if d.get("nonComplianceDetails")
        else "0",
    ),
    AndroidManagementSensorDescription(
        key="non_compliance_details",
        translation_key="non_compliance_details",
        name="Non-Compliance Details",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            str(d.get("nonComplianceDetails"))
            if d.get("nonComplianceDetails")
            else None
        ),
    ),
    # --- Display info (requires displayInfoEnabled in policy) ---
    AndroidManagementSensorDescription(
        key="display_count",
        translation_key="display_count",
        name="Display Count",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: str(len(d.get("displays", [])))
        if d.get("displays") is not None
        else None,
    ),
    # --- Enrollment token data (set via additionalData when creating token) ---
    AndroidManagementSensorDescription(
        key="enrollment_token_data",
        translation_key="enrollment_token_data",
        name="Enrollment Token Data",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("enrollmentTokenData"),
    ),
    # --- Device trust (when available from API) ---
    AndroidManagementSensorDescription(
        key="device_trust_signal",
        translation_key="device_trust_signal",
        name="Device Trust",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            str(d.get("deviceTrustSignal"))
            if d.get("deviceTrustSignal") is not None
            else None
        ),
    ),
    # --- eSIM / telephony / application reporting ---
    AndroidManagementSensorDescription(
        key="eid",
        translation_key="eid",
        name="EID",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_device_eid,
    ),
    AndroidManagementSensorDescription(
        key="telephony_info",
        translation_key="telephony_info",
        name="Telephony Info",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_telephony_summary,
    ),
    AndroidManagementSensorDescription(
        key="application_report_count",
        translation_key="application_report_count",
        name="Application Report Count",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            str(len(d.get("applicationReports", [])))
            if d.get("applicationReports") is not None
            else None
        ),
    ),
    AndroidManagementSensorDescription(
        key="signing_cert_sha256",
        translation_key="signing_cert_sha256",
        name="Signing Cert SHA-256",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_signing_cert_sha256,
    ),
    AndroidManagementSensorDescription(
        key="default_application_info",
        translation_key="default_application_info",
        name="Default Application Info",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: (
            str(d.get("defaultApplicationInfo"))
            if d.get("defaultApplicationInfo") is not None
            else None
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AndroidManagementConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    coordinator = entry.runtime_data
    # Track device IDs we've already created entities for (so we can add new ones on coordinator update).
    # Seed from device registry so we know about stale devices (no longer in API) and can remove them on first refresh.
    device_ids_seen: set[str] = set()
    dev_reg = dr.async_get(hass)
    for device in getattr(dev_reg, "_devices", {}).values():
        if entry.entry_id not in device.config_entries:
            continue
        for did in device.identifiers:
            if did[0] == DOMAIN and (
                "/" not in did[1] or not did[1].startswith("enterprises/")
            ):
                device_ids_seen.add(did[1])
                break

    entities: list[AndroidManagementSensor] = []
    for device_id, device_data in coordinator.data.items():
        device_ids_seen.add(device_id)
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                AndroidManagementSensor(coordinator, device_id, description)
            )

    async_add_entities(entities)

    async def _sync_sensor_entities() -> None:
        """Add entities for new devices and remove devices no longer in the API."""
        current_ids = set(coordinator.data)
        # Add entities for new devices
        new_entities: list[AndroidManagementSensor] = []
        for device_id in current_ids:
            if device_id not in device_ids_seen:
                device_ids_seen.add(device_id)
                for description in SENSOR_DESCRIPTIONS:
                    new_entities.append(
                        AndroidManagementSensor(
                            coordinator, device_id, description
                        )
                    )
        if new_entities:
            async_add_entities(new_entities)
        # Remove devices no longer in the API (before we shrink device_ids_seen)
        removed_ids = device_ids_seen - current_ids
        dev_reg = dr.async_get(hass)
        if removed_ids:
            for device_id in removed_ids:
                device = dev_reg.async_get_device(
                    identifiers={(DOMAIN, device_id)}
                )
                if device:
                    _LOGGER.info(
                        "Removing device no longer in API: %s",
                        device_id,
                    )
                    dev_reg.async_remove_device(device.id)
        # Also walk registry if available (handles devices that never made it into device_ids_seen)
        get_entries = getattr(
            dev_reg, "async_entries_for_config_entry", None
        )
        if get_entries:
            try:
                entries = await get_entries(entry.entry_id)
            except TypeError:
                entries = get_entries(entry.entry_id)
            for device in entries or []:
                for did in device.identifiers:
                    if did[0] != DOMAIN:
                        continue
                    device_id = did[1]
                    if "/" in device_id and device_id.startswith("enterprises/"):
                        break
                    if device_id not in current_ids:
                        device = dev_reg.async_get_device(
                            identifiers={(DOMAIN, device_id)}
                        )
                        if device:
                            _LOGGER.info(
                                "Removing device no longer in API: %s",
                                device_id,
                            )
                            dev_reg.async_remove_device(device.id)
                    break
        # Keep device_ids_seen in sync with current API list
        device_ids_seen.intersection_update(current_ids)

    def _on_coordinator_update() -> None:
        hass.async_create_task(_sync_sensor_entities())

    coordinator.async_add_listener(_on_coordinator_update)


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
