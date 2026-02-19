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
SERVICE_CLEAR_APP_DATA = "clear_app_data"
SERVICE_START_LOST_MODE = "start_lost_mode"
SERVICE_STOP_LOST_MODE = "stop_lost_mode"
SERVICE_PATCH_DEVICE = "patch_device"
SERVICE_WIPE = "wipe"
SERVICE_ADD_ESIM = "add_esim"
SERVICE_REMOVE_ESIM = "remove_esim"
SERVICE_REQUEST_DEVICE_INFO = "request_device_info"
SERVICE_ISSUE_COMMAND = "issue_command"
SERVICE_RESET_PASSWORD = "reset_password"

ATTR_DEVICE_ID = "device_id"
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

ATTR_PACKAGE_NAMES = "package_names"
ATTR_LOST_MESSAGE = "lost_message"
ATTR_LOST_PHONE_NUMBER = "lost_phone_number"
ATTR_LOST_EMAIL = "lost_email"
ATTR_LOST_STREET_ADDRESS = "lost_street_address"
ATTR_LOST_ORGANIZATION = "lost_organization"
ATTR_STATE = "state"
ATTR_DISABLED_REASON = "disabled_reason"
ATTR_WIPE_REASON = "wipe_reason"
ATTR_WIPE_DATA_FLAGS = "wipe_data_flags"
ATTR_ACTIVATION_CODE = "activation_code"
ATTR_ACTIVATION_STATE = "activation_state"
ATTR_ICC_ID = "icc_id"
ATTR_DEVICE_INFO_TYPE = "device_info_type"
ATTR_COMMAND_TYPE = "command_type"
ATTR_COMMAND_PARAMS = "command_params"
ATTR_NEW_PASSWORD = "new_password"
ATTR_RESET_PASSWORD_FLAGS = "reset_password_flags"

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

CLEAR_APP_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_PACKAGE_NAMES): vol.Any(cv.ensure_list(cv.string), cv.string),
    }
)

START_LOST_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_LOST_MESSAGE): cv.string,
        vol.Optional(ATTR_LOST_PHONE_NUMBER): cv.string,
        vol.Optional(ATTR_LOST_EMAIL): cv.string,
        vol.Optional(ATTR_LOST_STREET_ADDRESS): cv.string,
        vol.Optional(ATTR_LOST_ORGANIZATION): cv.string,
    }
)

STOP_LOST_MODE_SCHEMA = vol.Schema({vol.Required(ATTR_DEVICE_ID): cv.string})

PATCH_DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_STATE): vol.In(["ACTIVE", "DISABLED"]),
        vol.Optional(ATTR_POLICY_ID): cv.string,
        vol.Optional(ATTR_DISABLED_REASON): cv.string,
    }
)

WIPE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_WIPE_REASON): cv.string,
        vol.Optional(ATTR_WIPE_DATA_FLAGS): vol.Any(
            cv.ensure_list(cv.string),
            vol.All(cv.string, lambda x: [f.strip() for f in x.split(",") if f.strip()]),
        ),
    }
)

ADD_ESIM_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_ACTIVATION_CODE): cv.string,
        vol.Optional(ATTR_ACTIVATION_STATE, default="ACTIVATED"): vol.In(
            ["ACTIVATION_STATE_UNSPECIFIED", "ACTIVATED", "NOT_ACTIVATED"]
        ),
    }
)

REMOVE_ESIM_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_ICC_ID): cv.string,
    }
)

REQUEST_DEVICE_INFO_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_DEVICE_INFO_TYPE, default="EID"): vol.In(
            ["DEVICE_INFO_UNSPECIFIED", "EID"]
        ),
    }
)

ISSUE_COMMAND_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Required(ATTR_COMMAND_TYPE): cv.string,
        vol.Optional(ATTR_COMMAND_PARAMS, default={}): vol.Any(dict, cv.string),
    }
)

RESET_PASSWORD_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): cv.string,
        vol.Optional(ATTR_NEW_PASSWORD): cv.string,
        vol.Optional(ATTR_RESET_PASSWORD_FLAGS): vol.Any(
            cv.ensure_list(cv.string),
            vol.All(cv.string, lambda x: [f.strip() for f in x.split(",") if f.strip()]),
        ),
    }
)


def _resolve_device_name(
    coordinator: AndroidManagementCoordinator, device_id: str
) -> str | None:
    """Resolve device_id to full API resource name."""
    if "/" in device_id and device_id.startswith("enterprises/"):
        return device_id
    device_data = coordinator.data.get(device_id, {})
    return device_data.get("name")


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

    def _require_device(device_id: str) -> tuple[AndroidManagementCoordinator, str]:
        coordinator = _get_coordinator(hass)
        device_name = _resolve_device_name(coordinator, device_id)
        if not device_name:
            raise ValueError(f"Device not found: {device_id}")
        return coordinator, device_name

    async def handle_clear_app_data(call: ServiceCall) -> None:
        """Handle clear_app_data service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        pkgs_raw = call.data[ATTR_PACKAGE_NAMES]
        pkgs = (
            [p.strip() for p in pkgs_raw.replace(",", "\n").splitlines() if p.strip()]
            if isinstance(pkgs_raw, str)
            else list(pkgs_raw)
        )
        if not pkgs:
            _LOGGER.error("At least one package name is required")
            return
        await coordinator.client.async_issue_command(
            hass, device_name, "CLEAR_APP_DATA",
            clearAppsDataParams={"packageNames": pkgs}
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Clear app data command sent for device %s", device_name)

    async def handle_start_lost_mode(call: ServiceCall) -> None:
        """Handle start_lost_mode service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        params: dict[str, Any] = {}
        if msg := call.data.get(ATTR_LOST_MESSAGE):
            params["lostMessage"] = {"defaultMessage": msg, "localizedMessages": {}}
        if phone := call.data.get(ATTR_LOST_PHONE_NUMBER):
            params["lostPhoneNumber"] = {"defaultMessage": phone, "localizedMessages": {}}
        if email := call.data.get(ATTR_LOST_EMAIL):
            params["lostEmailAddress"] = email
        if addr := call.data.get(ATTR_LOST_STREET_ADDRESS):
            params["lostStreetAddress"] = {"defaultMessage": addr, "localizedMessages": {}}
        if org := call.data.get(ATTR_LOST_ORGANIZATION):
            params["lostOrganization"] = {"defaultMessage": org, "localizedMessages": {}}
        if not params:
            _LOGGER.error("At least one of lost_message, lost_phone_number, lost_email, lost_street_address, lost_organization is required")
            return
        await coordinator.client.async_issue_command(
            hass, device_name, "START_LOST_MODE",
            startLostModeParams=params
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Start lost mode command sent for device %s", device_name)

    async def handle_stop_lost_mode(call: ServiceCall) -> None:
        """Handle stop_lost_mode service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        await coordinator.client.async_issue_command(
            hass, device_name, "STOP_LOST_MODE",
            stopLostModeParams={}
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Stop lost mode command sent for device %s", device_name)

    async def handle_patch_device(call: ServiceCall) -> None:
        """Handle patch_device service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        state = call.data.get(ATTR_STATE)
        policy_id = call.data.get(ATTR_POLICY_ID)
        reason = call.data.get(ATTR_DISABLED_REASON)
        if not any([state, policy_id, reason]):
            _LOGGER.error("At least one of state, policy_id, or disabled_reason is required")
            return
        policy_name: str | None = None
        if policy_id:
            policy_name = f"{coordinator.client.enterprise_name}/policies/{policy_id}"
        disabled_reason: dict[str, Any] | None = None
        if reason:
            disabled_reason = {"defaultMessage": reason, "localizedMessages": {}}
        await coordinator.client.async_patch_device(
            hass, device_name,
            state=state,
            policy_name=policy_name,
            disabled_reason=disabled_reason
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Device %s patched successfully", device_name)

    async def handle_wipe(call: ServiceCall) -> None:
        """Handle wipe service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        params: dict[str, Any] = {}
        if reason := call.data.get(ATTR_WIPE_REASON):
            params["wipeReason"] = {"defaultMessage": reason, "localizedMessages": {}}
        if flags := call.data.get(ATTR_WIPE_DATA_FLAGS):
            if isinstance(flags, str):
                flags = [f.strip() for f in flags.split(",") if f.strip()]
            params["wipeDataFlags"] = flags
        await coordinator.client.async_issue_command(
            hass, device_name, "WIPE",
            wipeParams=params if params else {}
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Wipe command sent for device %s", device_name)

    async def handle_add_esim(call: ServiceCall) -> None:
        """Handle add_esim service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        await coordinator.client.async_issue_command(
            hass, device_name, "ADD_ESIM",
            addEsimParams={
                "activationCode": call.data[ATTR_ACTIVATION_CODE],
                "activationState": call.data.get(ATTR_ACTIVATION_STATE, "ACTIVATED"),
            }
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Add eSIM command sent for device %s", device_name)

    async def handle_remove_esim(call: ServiceCall) -> None:
        """Handle remove_esim service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        await coordinator.client.async_issue_command(
            hass, device_name, "REMOVE_ESIM",
            removeEsimParams={"iccId": call.data[ATTR_ICC_ID]}
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Remove eSIM command sent for device %s", device_name)

    async def handle_request_device_info(call: ServiceCall) -> None:
        """Handle request_device_info service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        await coordinator.client.async_issue_command(
            hass, device_name, "REQUEST_DEVICE_INFO",
            requestDeviceInfoParams={
                "deviceInfo": call.data.get(ATTR_DEVICE_INFO_TYPE, "EID"),
            }
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Request device info command sent for device %s", device_name)

    async def handle_issue_command(call: ServiceCall) -> None:
        """Handle issue_command service call."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        params = call.data.get(ATTR_COMMAND_PARAMS, {})
        if isinstance(params, str):
            params = json.loads(params) if params else {}
        await coordinator.client.async_issue_command(
            hass, device_name, call.data[ATTR_COMMAND_TYPE], **params
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Command %s sent for device %s", call.data[ATTR_COMMAND_TYPE], device_name)

    async def handle_reset_password(call: ServiceCall) -> None:
        """Handle reset_password service call (enhanced with newPassword and flags)."""
        coordinator, device_name = _require_device(call.data[ATTR_DEVICE_ID])
        extra: dict[str, Any] = {}
        if pwd := call.data.get(ATTR_NEW_PASSWORD):
            extra["newPassword"] = pwd
        if flags := call.data.get(ATTR_RESET_PASSWORD_FLAGS):
            if isinstance(flags, str):
                flags = [f.strip() for f in flags.split(",") if f.strip()]
            extra["resetPasswordFlags"] = flags
        await coordinator.client.async_issue_command(
            hass, device_name, "RESET_PASSWORD", **extra
        )
        await coordinator.async_request_refresh()
        _LOGGER.info("Reset password command sent for device %s", device_name)

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
    hass.services.async_register(
        DOMAIN, SERVICE_CLEAR_APP_DATA, handle_clear_app_data, schema=CLEAR_APP_DATA_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_START_LOST_MODE, handle_start_lost_mode, schema=START_LOST_MODE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_LOST_MODE, handle_stop_lost_mode, schema=STOP_LOST_MODE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_PATCH_DEVICE, handle_patch_device, schema=PATCH_DEVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_WIPE, handle_wipe, schema=WIPE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_ESIM, handle_add_esim, schema=ADD_ESIM_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_REMOVE_ESIM, handle_remove_esim, schema=REMOVE_ESIM_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REQUEST_DEVICE_INFO,
        handle_request_device_info,
        schema=REQUEST_DEVICE_INFO_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ISSUE_COMMAND, handle_issue_command, schema=ISSUE_COMMAND_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_PASSWORD, handle_reset_password, schema=RESET_PASSWORD_SCHEMA
    )
