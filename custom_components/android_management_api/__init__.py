"""The Android Management API integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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

    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    coordinator = AndroidManagementCoordinator(hass, client, scan_interval=scan_interval)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Remove any legacy device_tracker entities (platform was removed)
    registry = er.async_get(hass)
    for entity_entry in registry.entities.get_entries_for_config_entry_id(entry.entry_id):
        if entity_entry.entity_id.startswith("device_tracker."):
            registry.async_remove(entity_entry.entity_id)
            _LOGGER.debug("Removed legacy device_tracker entity: %s", entity_entry.entity_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_services(hass)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AndroidManagementConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
