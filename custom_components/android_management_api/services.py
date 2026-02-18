"""Service definitions for Android Management API."""

from __future__ import annotations

import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import AndroidManagementCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_POLICY = "set_policy"
SERVICE_SET_KIOSK_POLICY = "set_kiosk_policy"
SERVICE_CREATE_ENROLLMENT_TOKEN = "create_enrollment_token"

ATTR_POLICY_ID = "policy_id"
ATTR_POLICY_BODY = "policy_body"
ATTR_POLICY_NAME = "policy_name"
ATTR_DURATION = "duration"

ATTR_PACKAGE_NAME = "package_name"
ATTR_ADDITIONAL_PACKAGES = "additional_packages"
ATTR_INSTALL_TYPE = "install_type"
ATTR_AUTO_UPDATE_MODE = "auto_update_mode"
ATTR_LOCK_TASK_ALLOWED = "lock_task_allowed"
ATTR_DEFAULT_PERMISSION_POLICY = "default_permission_policy"
ATTR_POWER_BUTTON_ACTIONS = "power_button_actions"
ATTR_SYSTEM_NAVIGATION = "system_navigation"
ATTR_DEVICE_SETTINGS = "device_settings"
ATTR_STATUS_BAR_KIOSK = "status_bar"
ATTR_SCREEN_BRIGHTNESS_MODE = "screen_brightness_mode"
ATTR_SCREEN_BRIGHTNESS = "screen_brightness"
ATTR_SCREEN_TIMEOUT_MODE = "screen_timeout_mode"
ATTR_SCREEN_TIMEOUT = "screen_timeout"
ATTR_DEVELOPER_SETTINGS = "developer_settings"
ATTR_APP_AUTO_UPDATE_POLICY = "app_auto_update_policy"
ATTR_KEYGUARD_DISABLED = "keyguard_disabled"
ATTR_STATUS_BAR_DISABLED = "status_bar_disabled"

SET_POLICY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_POLICY_ID): cv.string,
        vol.Optional(ATTR_POLICY_BODY): cv.string,
    }
)

SET_KIOSK_POLICY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_POLICY_ID): cv.string,
        vol.Required(ATTR_PACKAGE_NAME): cv.string,
        vol.Optional(ATTR_ADDITIONAL_PACKAGES): cv.string,
        vol.Optional(ATTR_INSTALL_TYPE, default="KIOSK"): cv.string,
        vol.Optional(ATTR_AUTO_UPDATE_MODE, default="AUTO_UPDATE_HIGH_PRIORITY"): cv.string,
        vol.Optional(ATTR_LOCK_TASK_ALLOWED, default=True): cv.boolean,
        vol.Optional(ATTR_DEFAULT_PERMISSION_POLICY, default="GRANT"): cv.string,
        vol.Optional(ATTR_POWER_BUTTON_ACTIONS, default="POWER_BUTTON_BLOCKED"): cv.string,
        vol.Optional(ATTR_SYSTEM_NAVIGATION, default="NAVIGATION_DISABLED"): cv.string,
        vol.Optional(ATTR_DEVICE_SETTINGS, default="SETTINGS_ACCESS_BLOCKED"): cv.string,
        vol.Optional(ATTR_STATUS_BAR_KIOSK, default="NOTIFICATIONS_AND_SYSTEM_INFO_DISABLED"): cv.string,
        vol.Optional(ATTR_SCREEN_BRIGHTNESS_MODE, default="BRIGHTNESS_FIXED"): cv.string,
        vol.Optional(ATTR_SCREEN_BRIGHTNESS, default=180): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=255)
        ),
        vol.Optional(ATTR_SCREEN_TIMEOUT_MODE, default="SCREEN_TIMEOUT_ENFORCED"): cv.string,
        vol.Optional(ATTR_SCREEN_TIMEOUT, default="220s"): cv.string,
        vol.Optional(ATTR_DEVELOPER_SETTINGS, default="DEVELOPER_SETTINGS_ALLOWED"): cv.string,
        vol.Optional(ATTR_APP_AUTO_UPDATE_POLICY, default="ALWAYS"): cv.string,
        vol.Optional(ATTR_KEYGUARD_DISABLED, default=True): cv.boolean,
        vol.Optional(ATTR_STATUS_BAR_DISABLED, default=True): cv.boolean,
    }
)

CREATE_ENROLLMENT_TOKEN_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_POLICY_NAME): cv.string,
        vol.Optional(ATTR_DURATION, default="86400s"): cv.string,
    }
)


def _get_coordinator(hass: HomeAssistant) -> AndroidManagementCoordinator:
    """Get the first available coordinator from loaded config entries."""
    for entry in hass.config_entries.async_entries(DOMAIN):
        if hasattr(entry, "runtime_data") and entry.runtime_data is not None:
            return entry.runtime_data
    raise ValueError("No Android Management API config entry found")


async def async_register_services(hass: HomeAssistant) -> None:
    """Register integration services."""

    if hass.services.has_service(DOMAIN, SERVICE_SET_POLICY):
        return

    async def handle_set_policy(call: ServiceCall) -> None:
        """Handle the set_policy service call."""
        coordinator = _get_coordinator(hass)
        policy_id: str = call.data[ATTR_POLICY_ID]
        policy_body_str: str | None = call.data.get(ATTR_POLICY_BODY)

        policy_body: dict[str, Any] | None = None
        if policy_body_str:
            try:
                policy_body = json.loads(policy_body_str)
            except json.JSONDecodeError:
                _LOGGER.error("Invalid JSON in policy_body")
                return

        await coordinator.client.async_set_policy(hass, policy_id, policy_body)
        _LOGGER.info("Policy '%s' updated successfully", policy_id)

    async def handle_set_kiosk_policy(call: ServiceCall) -> None:
        """Handle the set_kiosk_policy service call."""
        coordinator = _get_coordinator(hass)
        policy_id: str = call.data[ATTR_POLICY_ID]

        app_list: list[dict[str, Any]] = [
            {
                "packageName": call.data[ATTR_PACKAGE_NAME],
                "installType": call.data.get(ATTR_INSTALL_TYPE, "KIOSK"),
                "defaultPermissionPolicy": call.data.get(
                    ATTR_DEFAULT_PERMISSION_POLICY, "GRANT"
                ),
                "lockTaskAllowed": call.data.get(ATTR_LOCK_TASK_ALLOWED, True),
                "autoUpdateMode": call.data.get(
                    ATTR_AUTO_UPDATE_MODE, "AUTO_UPDATE_HIGH_PRIORITY"
                ),
            }
        ]
        extra_raw: str | None = call.data.get(ATTR_ADDITIONAL_PACKAGES)
        if extra_raw:
            for line in extra_raw.replace(",", "\n").splitlines():
                extra_pkg = line.strip()
                if extra_pkg:
                    app_list.append({
                        "packageName": extra_pkg,
                        "installType": "FORCE_INSTALLED",
                        "defaultPermissionPolicy": "GRANT",
                        "autoUpdateMode": "AUTO_UPDATE_HIGH_PRIORITY",
                    })

        policy_body: dict[str, Any] = {
            "applications": app_list,
            "kioskCustomization": {
                "powerButtonActions": call.data.get(
                    ATTR_POWER_BUTTON_ACTIONS, "POWER_BUTTON_BLOCKED"
                ),
                "systemNavigation": call.data.get(
                    ATTR_SYSTEM_NAVIGATION, "NAVIGATION_DISABLED"
                ),
                "deviceSettings": call.data.get(
                    ATTR_DEVICE_SETTINGS, "SETTINGS_ACCESS_BLOCKED"
                ),
                "statusBar": call.data.get(
                    ATTR_STATUS_BAR_KIOSK, "NOTIFICATIONS_AND_SYSTEM_INFO_DISABLED"
                ),
            },
            "displaySettings": {
                "screenBrightnessSettings": {
                    "screenBrightnessMode": call.data.get(
                        ATTR_SCREEN_BRIGHTNESS_MODE, "BRIGHTNESS_FIXED"
                    ),
                    "screenBrightness": call.data.get(ATTR_SCREEN_BRIGHTNESS, 180),
                },
                "screenTimeoutSettings": {
                    "screenTimeoutMode": call.data.get(
                        ATTR_SCREEN_TIMEOUT_MODE, "SCREEN_TIMEOUT_ENFORCED"
                    ),
                    "screenTimeout": call.data.get(ATTR_SCREEN_TIMEOUT, "220s"),
                },
            },
            "advancedSecurityOverrides": {
                "developerSettings": call.data.get(
                    ATTR_DEVELOPER_SETTINGS, "DEVELOPER_SETTINGS_ALLOWED"
                ),
            },
            "appAutoUpdatePolicy": call.data.get(ATTR_APP_AUTO_UPDATE_POLICY, "ALWAYS"),
            "keyguardDisabled": call.data.get(ATTR_KEYGUARD_DISABLED, True),
            "statusBarDisabled": call.data.get(ATTR_STATUS_BAR_DISABLED, True),
        }

        await coordinator.client.async_set_policy(hass, policy_id, policy_body)
        _LOGGER.info("Kiosk policy '%s' updated successfully", policy_id)

    async def handle_create_enrollment_token(call: ServiceCall) -> None:
        """Handle the create_enrollment_token service call."""
        coordinator = _get_coordinator(hass)
        policy_name: str | None = call.data.get(ATTR_POLICY_NAME)
        duration: str = call.data.get(ATTR_DURATION, "86400s")

        result = await coordinator.client.async_create_enrollment_token(
            hass, policy_name=policy_name, duration=duration
        )

        hass.bus.async_fire(
            f"{DOMAIN}_enrollment_token_created",
            {
                "token_value": result.get("value", ""),
                "qr_code": result.get("qrCode", ""),
                "name": result.get("name", ""),
                "expiration_timestamp": result.get("expirationTimestamp", ""),
            },
        )
        _LOGGER.info("Enrollment token created: %s", result.get("name", ""))

    hass.services.async_register(
        DOMAIN, SERVICE_SET_POLICY, handle_set_policy, schema=SET_POLICY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_KIOSK_POLICY,
        handle_set_kiosk_policy,
        schema=SET_KIOSK_POLICY_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_ENROLLMENT_TOKEN,
        handle_create_enrollment_token,
        schema=CREATE_ENROLLMENT_TOKEN_SCHEMA,
    )
