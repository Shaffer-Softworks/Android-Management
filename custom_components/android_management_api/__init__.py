"""The Android Management API integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import AndroidManagementAPIClient
from .const import (
    AUTH_METHOD_FILE,
    AUTH_METHOD_JSON,
    CONF_AUTH_METHOD,
    CONF_ENTERPRISE_NAME,
    CONF_FILE_PATH,
    CONF_SERVICE_ACCOUNT_JSON,
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

    coordinator = AndroidManagementCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_services(hass)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AndroidManagementConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
