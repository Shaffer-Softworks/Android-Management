"""The Android Management API integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .api import AndroidManagementAPIClient
from .const import (
    AUTH_METHOD_FILE,
    AUTH_METHOD_JSON,
    CONF_AUTH_METHOD,
    CONF_DEFAULT_POLICY_ID,
    CONF_ENTERPRISE_NAME,
    CONF_FILE_PATH,
    CONF_SCAN_INTERVAL,
    CONF_SERVICE_ACCOUNT_JSON,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import AndroidManagementCoordinator
from .services import async_register_services

_LOGGER = logging.getLogger(__name__)

type AndroidManagementConfigEntry = ConfigEntry[AndroidManagementCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: AndroidManagementConfigEntry
) -> bool:
    """Set up Android Management API from a config entry."""
    enterprise_name = entry.data[CONF_ENTERPRISE_NAME]
    auth_method = entry.data[CONF_AUTH_METHOD]

    if auth_method == AUTH_METHOD_JSON:
        client = await hass.async_add_executor_job(
            lambda: AndroidManagementAPIClient(
                enterprise_name=enterprise_name,
                credentials_dict=entry.data[CONF_SERVICE_ACCOUNT_JSON],
            )
        )
    else:
        client = await hass.async_add_executor_job(
            lambda: AndroidManagementAPIClient(
                enterprise_name=enterprise_name,
                credentials_file=entry.data[CONF_FILE_PATH],
            )
        )

    scan_interval = int(
        entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
    )
    coordinator = AndroidManagementCoordinator(hass, client, scan_interval=scan_interval)
    # Ensure coordinator always has a listener so it keeps scheduling periodic refresh
    coordinator.async_add_listener(lambda: None)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Remove any legacy device_tracker entities (platform was removed)
    try:
        ent_reg = er.async_get(hass)
        get_entries = getattr(
            ent_reg.entities, "get_entries_for_config_entry_id", None
        )
        if get_entries:
            for entity_entry in get_entries(entry.entry_id):
                if entity_entry.entity_id.startswith("device_tracker."):
                    ent_reg.async_remove(entity_entry.entity_id)
                    _LOGGER.debug(
                        "Removed legacy device_tracker entity: %s",
                        entity_entry.entity_id,
                    )
    except Exception:  # noqa: S110
        pass  # Non-fatal; avoid breaking setup on registry API differences

    # Remove stale devices (and their entities) that are no longer in the API
    current_device_ids = set(coordinator.data.keys())
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    stale_device_ids: list[tuple[str, str]] = []
    for device in dev_reg.devices.get_devices_for_config_entry_id(entry.entry_id):
        for did in device.identifiers:
            if did[0] != DOMAIN:
                continue
            device_id = did[1]
            if "/" in device_id and device_id.startswith("enterprises/"):
                break
            if device_id not in current_device_ids:
                stale_device_ids.append((device.id, device_id))
            break
    for ha_device_id, api_device_id in stale_device_ids:
        # Remove all entity entries for this device first (prevents HA from re-creating the device)
        entity_entries = er.async_entries_for_device(ent_reg, ha_device_id, True)
        for entity_entry in entity_entries:
            ent_reg.async_remove(entity_entry.entity_id)
        dev_reg.async_remove_device(ha_device_id)
        _LOGGER.info(
            "Removed stale device and %s entities no longer in API: %s",
            len(entity_entries),
            api_device_id,
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_services(hass)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AndroidManagementConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
