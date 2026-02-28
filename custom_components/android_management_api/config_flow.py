"""Config flow for Android Management API integration."""

from __future__ import annotations

import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import AndroidManagementAPIClient
from .const import (
    AUTH_METHOD_FILE,
    AUTH_METHOD_JSON,
    CONF_AUTH_METHOD,
    CONF_CLEAR_APP_DATA_PACKAGES,
    CONF_DEFAULT_POLICY_ID,
    CONF_ENTERPRISE_NAME,
    CONF_FILE_PATH,
    CONF_SCAN_INTERVAL,
    CONF_SERVICE_ACCOUNT_JSON,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# ── Helpers ──────────────────────────────────────────────────────────────────

def _select(options: list[str]) -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN)
    )


def _text(multiline: bool = False) -> TextSelector:
    return TextSelector(
        TextSelectorConfig(
            type=TextSelectorType.TEXT, multiline=multiline
        )
    )


def _number(min_val: float, max_val: float, step: float = 1) -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(min=min_val, max=max_val, step=step, mode=NumberSelectorMode.BOX)
    )


_bool = BooleanSelector()


def _schema_with_suggestions(
    schema_dict: dict, current: dict[str, Any]
) -> vol.Schema:
    """Build a vol.Schema with suggested_value descriptions from current options."""
    result = {}
    for key, selector in schema_dict.items():
        if isinstance(key, (vol.Optional, vol.Required)):
            name = key.schema
            suggested = current.get(name)
            if suggested is not None:
                new_key = vol.Optional(
                    name,
                    description={"suggested_value": suggested},
                )
            else:
                new_key = key
            result[new_key] = selector
        else:
            result[key] = selector
    return vol.Schema(result)


# ── Config flow schemas ──────────────────────────────────────────────────────

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENTERPRISE_NAME): _text(),
        vol.Required(CONF_AUTH_METHOD, default=AUTH_METHOD_JSON): SelectSelector(
            SelectSelectorConfig(
                options=[
                    {"value": AUTH_METHOD_JSON, "label": "Paste JSON key contents"},
                    {"value": AUTH_METHOD_FILE, "label": "Provide file path on disk"},
                ],
                mode=SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)

STEP_JSON_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERVICE_ACCOUNT_JSON): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT, multiline=True)
        ),
    }
)

STEP_FILE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_FILE_PATH): _text(),
    }
)


# ── Options flow schemas (raw dicts, wrapped with suggestions at runtime) ────

KIOSK_APP_SCHEMA = {
    vol.Optional("package_name", default=""): _text(),
    vol.Optional("install_type", default="KIOSK"): _select([
        "KIOSK", "FORCE_INSTALLED", "PREINSTALLED",
        "AVAILABLE", "REQUIRED_FOR_SETUP", "BLOCKED",
    ]),
    vol.Optional("auto_update_mode", default="AUTO_UPDATE_HIGH_PRIORITY"): _select([
        "AUTO_UPDATE_HIGH_PRIORITY", "AUTO_UPDATE_POSTPONED", "AUTO_UPDATE_DEFAULT",
    ]),
    vol.Optional("lock_task_allowed", default=True): _bool,
    vol.Optional("default_permission_policy", default="GRANT"): _select([
        "GRANT", "PROMPT", "DENY",
    ]),
    vol.Optional("additional_packages", default=""): _text(multiline=True),
}

KIOSK_UI_SCHEMA = {
    vol.Optional("power_button_actions", default="POWER_BUTTON_BLOCKED"): _select([
        "POWER_BUTTON_BLOCKED", "POWER_BUTTON_AVAILABLE",
    ]),
    vol.Optional("system_navigation", default="NAVIGATION_DISABLED"): _select([
        "NAVIGATION_DISABLED", "NAVIGATION_ENABLED", "HOME_BUTTON_ONLY",
    ]),
    vol.Optional("device_settings", default="SETTINGS_ACCESS_BLOCKED"): _select([
        "SETTINGS_ACCESS_BLOCKED", "SETTINGS_ACCESS_ALLOWED",
    ]),
    vol.Optional("kiosk_status_bar", default="NOTIFICATIONS_AND_SYSTEM_INFO_DISABLED"): _select([
        "NOTIFICATIONS_AND_SYSTEM_INFO_DISABLED",
        "NOTIFICATIONS_AND_SYSTEM_INFO_ENABLED",
        "SYSTEM_INFO_ONLY",
    ]),
    vol.Optional("system_error_warnings", default="ERROR_AND_WARNINGS_MUTED"): _select([
        "ERROR_AND_WARNINGS_MUTED", "ERROR_AND_WARNINGS_ENABLED",
    ]),
}

DISPLAY_SCHEMA = {
    vol.Optional("screen_brightness_mode", default="BRIGHTNESS_FIXED"): _select([
        "BRIGHTNESS_FIXED", "BRIGHTNESS_USER_CHOICE", "BRIGHTNESS_AUTOMATIC",
    ]),
    vol.Optional("screen_brightness", default=180): _number(0, 255),
    vol.Optional("screen_timeout_mode", default="SCREEN_TIMEOUT_ENFORCED"): _select([
        "SCREEN_TIMEOUT_ENFORCED", "SCREEN_TIMEOUT_USER_CHOICE",
    ]),
    vol.Optional("screen_timeout", default="220s"): _text(),
}

SECURITY_SCHEMA = {
    vol.Optional("developer_settings", default="DEVELOPER_SETTINGS_ALLOWED"): _select([
        "DEVELOPER_SETTINGS_ALLOWED", "DEVELOPER_SETTINGS_DISABLED",
    ]),
    vol.Optional("keyguard_disabled", default=True): _bool,
    vol.Optional("camera_disabled", default=False): _bool,
    vol.Optional("screen_capture_disabled", default=False): _bool,
    vol.Optional("location_mode", default="LOCATION_USER_CHOICE"): _select([
        "LOCATION_USER_CHOICE", "LOCATION_ENFORCED", "LOCATION_DISABLED",
        "HIGH_ACCURACY", "SENSORS_ONLY", "BATTERY_SAVING", "OFF",
    ]),
    vol.Optional("untrusted_apps_policy", default="DISALLOW_INSTALL"): _select([
        "DISALLOW_INSTALL",
        "ALLOW_INSTALL_IN_PERSONAL_PROFILE_ONLY",
        "ALLOW_INSTALL_DEVICE_WIDE",
    ]),
    vol.Optional("google_play_protect", default="VERIFY_APPS_ENFORCED"): _select([
        "VERIFY_APPS_ENFORCED", "VERIFY_APPS_USER_CHOICE",
    ]),
    vol.Optional("ensure_verify_apps_enabled", default=True): _bool,
}

NETWORK_SCHEMA = {
    vol.Optional("wifi_config_disabled", default=False): _bool,
    vol.Optional("bluetooth_disabled", default=False): _bool,
    vol.Optional("bluetooth_config_disabled", default=False): _bool,
    vol.Optional("vpn_config_disabled", default=False): _bool,
    vol.Optional("tethering_config_disabled", default=False): _bool,
    vol.Optional("data_roaming_disabled", default=False): _bool,
    vol.Optional("mobile_networks_config_disabled", default=False): _bool,
    vol.Optional("cell_broadcasts_config_disabled", default=False): _bool,
    vol.Optional("network_reset_disabled", default=False): _bool,
}

RESTRICTIONS_SCHEMA = {
    vol.Optional("factory_reset_disabled", default=False): _bool,
    vol.Optional("install_apps_disabled", default=False): _bool,
    vol.Optional("uninstall_apps_disabled", default=False): _bool,
    vol.Optional("mount_physical_media_disabled", default=False): _bool,
    vol.Optional("usb_file_transfer_disabled", default=False): _bool,
    vol.Optional("adjust_volume_disabled", default=False): _bool,
    vol.Optional("unmute_microphone_disabled", default=False): _bool,
    vol.Optional("outgoing_calls_disabled", default=False): _bool,
    vol.Optional("sms_disabled", default=False): _bool,
    vol.Optional("add_user_disabled", default=False): _bool,
    vol.Optional("modify_accounts_disabled", default=False): _bool,
    vol.Optional("set_user_icon_disabled", default=False): _bool,
    vol.Optional("set_wallpaper_disabled", default=False): _bool,
    vol.Optional("share_location_disabled", default=False): _bool,
    vol.Optional("credentials_config_disabled", default=False): _bool,
}

SYSTEM_SCHEMA = {
    vol.Optional("app_auto_update_policy", default="ALWAYS"): _select([
        "ALWAYS", "NEVER", "WIFI_ONLY", "CHOICE_TO_THE_USER",
    ]),
    vol.Optional("system_update_type", default="AUTOMATIC"): _select([
        "AUTOMATIC", "WINDOWED", "POSTPONE",
    ]),
    vol.Optional("play_store_mode", default="WHITELIST"): _select([
        "WHITELIST", "BLACKLIST",
    ]),
    vol.Optional("status_bar_disabled", default=True): _bool,
    vol.Optional("auto_time_required", default=False): _bool,
    vol.Optional("skip_first_use_hints_enabled", default=True): _bool,
    vol.Optional("maximum_time_to_lock", default=0): _number(0, 3600000),
    vol.Optional("stay_on_plugged_modes"): SelectSelector(
        SelectSelectorConfig(
            options=[
                "BATTERY_PLUGGED_AC",
                "BATTERY_PLUGGED_USB",
                "BATTERY_PLUGGED_WIRELESS",
            ],
            multiple=True,
            mode=SelectSelectorMode.DROPDOWN,
        )
    ),
    vol.Optional("long_support_message", default=""): _text(multiline=True),
    vol.Optional("short_support_message", default=""): _text(),
}

DEVICE_REPORTING_SCHEMA = {
    vol.Optional("software_info_enabled", default=True): _bool,
    vol.Optional("network_info_enabled", default=True): _bool,
    vol.Optional("memory_info_enabled", default=True): _bool,
    vol.Optional("display_info_enabled", default=True): _bool,
}

APPLY_POLICY_SCHEMA = {
    vol.Required("policy_id", default="policy1"): _text(),
}


# ── Mapping from option keys → Android Management API JSON keys ──────────────

BOOL_FIELD_MAP: dict[str, str] = {
    "keyguard_disabled": "keyguardDisabled",
    "status_bar_disabled": "statusBarDisabled",
    "camera_disabled": "cameraDisabled",
    "screen_capture_disabled": "screenCaptureDisabled",
    "bluetooth_disabled": "bluetoothDisabled",
    "bluetooth_config_disabled": "bluetoothConfigDisabled",
    "wifi_config_disabled": "wifiConfigDisabled",
    "vpn_config_disabled": "vpnConfigDisabled",
    "network_reset_disabled": "networkResetDisabled",
    "factory_reset_disabled": "factoryResetDisabled",
    "add_user_disabled": "addUserDisabled",
    "adjust_volume_disabled": "adjustVolumeDisabled",
    "mount_physical_media_disabled": "mountPhysicalMediaDisabled",
    "usb_file_transfer_disabled": "usbFileTransferDisabled",
    "unmute_microphone_disabled": "unmuteMicrophoneDisabled",
    "outgoing_calls_disabled": "outgoingCallsDisabled",
    "sms_disabled": "smsDisabled",
    "data_roaming_disabled": "dataRoamingDisabled",
    "tethering_config_disabled": "tetheringConfigDisabled",
    "cell_broadcasts_config_disabled": "cellBroadcastsConfigDisabled",
    "credentials_config_disabled": "credentialsConfigDisabled",
    "mobile_networks_config_disabled": "mobileNetworksConfigDisabled",
    "install_apps_disabled": "installAppsDisabled",
    "uninstall_apps_disabled": "uninstallAppsDisabled",
    "modify_accounts_disabled": "modifyAccountsDisabled",
    "set_user_icon_disabled": "setUserIconDisabled",
    "set_wallpaper_disabled": "setWallpaperDisabled",
    "share_location_disabled": "shareLocationDisabled",
    "skip_first_use_hints_enabled": "skipFirstUseHintsEnabled",
    "ensure_verify_apps_enabled": "ensureVerifyAppsEnabled",
    "auto_time_required": "autoTimeRequired",
}

STRING_FIELD_MAP: dict[str, str] = {
    "app_auto_update_policy": "appAutoUpdatePolicy",
    "location_mode": "locationMode",
    "play_store_mode": "playStoreMode",
}


def parse_policy_to_options(policy: dict[str, Any]) -> dict[str, Any]:
    """Reverse-map a live Android Management API policy dict into option keys."""
    opts: dict[str, Any] = {}

    # ── Applications ──
    apps = policy.get("applications")
    if apps and isinstance(apps, list) and len(apps) > 0:
        # Find the primary kiosk app (KIOSK install type or first app)
        primary = None
        additional: list[str] = []
        for app in apps:
            if app.get("installType") == "KIOSK" and primary is None:
                primary = app
            elif primary is None and app is apps[0]:
                primary = app
            else:
                pkg = app.get("packageName", "")
                if pkg:
                    additional.append(pkg)

        if primary:
            if primary.get("packageName"):
                opts["package_name"] = primary["packageName"]
            if primary.get("installType"):
                opts["install_type"] = primary["installType"]
            if primary.get("autoUpdateMode"):
                opts["auto_update_mode"] = primary["autoUpdateMode"]
            if "lockTaskAllowed" in primary:
                opts["lock_task_allowed"] = primary["lockTaskAllowed"]
            if primary.get("defaultPermissionPolicy"):
                opts["default_permission_policy"] = primary["defaultPermissionPolicy"]

        if additional:
            opts["additional_packages"] = "\n".join(additional)

    # ── Kiosk customization ──
    kiosk = policy.get("kioskCustomization", {})
    for api_key, opt_key in (
        ("powerButtonActions", "power_button_actions"),
        ("systemNavigation", "system_navigation"),
        ("deviceSettings", "device_settings"),
        ("statusBar", "kiosk_status_bar"),
        ("systemErrorWarnings", "system_error_warnings"),
    ):
        if kiosk.get(api_key):
            opts[opt_key] = kiosk[api_key]

    # ── Display settings ──
    display = policy.get("displaySettings", {})
    brightness = display.get("screenBrightnessSettings", {})
    if brightness.get("screenBrightnessMode"):
        opts["screen_brightness_mode"] = brightness["screenBrightnessMode"]
    if "screenBrightness" in brightness:
        opts["screen_brightness"] = brightness["screenBrightness"]
    timeout = display.get("screenTimeoutSettings", {})
    if timeout.get("screenTimeoutMode"):
        opts["screen_timeout_mode"] = timeout["screenTimeoutMode"]
    if timeout.get("screenTimeout"):
        opts["screen_timeout"] = timeout["screenTimeout"]

    # ── Advanced security ──
    security = policy.get("advancedSecurityOverrides", {})
    if security.get("developerSettings"):
        opts["developer_settings"] = security["developerSettings"]
    if security.get("untrustedAppsPolicy"):
        opts["untrusted_apps_policy"] = security["untrustedAppsPolicy"]
    if security.get("googlePlayProtectVerifyApps"):
        opts["google_play_protect"] = security["googlePlayProtectVerifyApps"]

    # ── Boolean fields (reverse map) ──
    for opt_key, api_key in BOOL_FIELD_MAP.items():
        if api_key in policy:
            opts[opt_key] = policy[api_key]

    # ── String/enum fields (reverse map) ──
    for opt_key, api_key in STRING_FIELD_MAP.items():
        if policy.get(api_key):
            opts[opt_key] = policy[api_key]

    # ── Maximum time to lock ──
    if policy.get("maximumTimeToLock"):
        try:
            opts["maximum_time_to_lock"] = int(policy["maximumTimeToLock"])
        except (ValueError, TypeError):
            pass

    # ── Stay on plugged modes ──
    if policy.get("stayOnPluggedModes"):
        opts["stay_on_plugged_modes"] = policy["stayOnPluggedModes"]

    # ── System update ──
    sys_update = policy.get("systemUpdate", {})
    if sys_update.get("type"):
        opts["system_update_type"] = sys_update["type"]

    # ── Support messages ──
    long_msg = policy.get("longSupportMessage", {})
    if long_msg.get("defaultMessage"):
        opts["long_support_message"] = long_msg["defaultMessage"]
    short_msg = policy.get("shortSupportMessage", {})
    if short_msg.get("defaultMessage"):
        opts["short_support_message"] = short_msg["defaultMessage"]

    # ── Device reporting (nested under statusReportingSettings) ──
    reporting = policy.get("statusReportingSettings", {})
    if "softwareInfoEnabled" in reporting:
        opts["software_info_enabled"] = reporting["softwareInfoEnabled"]
    if "networkInfoEnabled" in reporting:
        opts["network_info_enabled"] = reporting["networkInfoEnabled"]
    if "memoryInfoEnabled" in reporting:
        opts["memory_info_enabled"] = reporting["memoryInfoEnabled"]
    if "displayInfoEnabled" in reporting:
        opts["display_info_enabled"] = reporting["displayInfoEnabled"]

    return opts


def build_policy_from_options(opts: dict[str, Any]) -> dict[str, Any]:
    """Construct a full Android Management API policy dict from stored options."""
    policy: dict[str, Any] = {}

    # ── Applications ──
    app_list: list[dict[str, Any]] = []
    pkg = opts.get("package_name")
    if pkg:
        primary: dict[str, Any] = {"packageName": pkg}
        if opts.get("install_type"):
            primary["installType"] = opts["install_type"]
        if opts.get("auto_update_mode"):
            primary["autoUpdateMode"] = opts["auto_update_mode"]
        if "lock_task_allowed" in opts:
            primary["lockTaskAllowed"] = opts["lock_task_allowed"]
        if opts.get("default_permission_policy"):
            primary["defaultPermissionPolicy"] = opts["default_permission_policy"]
        app_list.append(primary)

    extra_raw = opts.get("additional_packages", "")
    if extra_raw:
        for line in extra_raw.splitlines():
            extra_pkg = line.strip()
            if extra_pkg:
                app_list.append({
                    "packageName": extra_pkg,
                    "installType": "FORCE_INSTALLED",
                    "defaultPermissionPolicy": "GRANT",
                    "autoUpdateMode": "AUTO_UPDATE_HIGH_PRIORITY",
                })

    if app_list:
        policy["applications"] = app_list

    # ── Kiosk customization ──
    kiosk: dict[str, Any] = {}
    for opt_key, api_key in (
        ("power_button_actions", "powerButtonActions"),
        ("system_navigation", "systemNavigation"),
        ("device_settings", "deviceSettings"),
        ("kiosk_status_bar", "statusBar"),
        ("system_error_warnings", "systemErrorWarnings"),
    ):
        if opts.get(opt_key):
            kiosk[api_key] = opts[opt_key]
    if kiosk:
        policy["kioskCustomization"] = kiosk

    # ── Display settings ──
    brightness: dict[str, Any] = {}
    if opts.get("screen_brightness_mode"):
        brightness["screenBrightnessMode"] = opts["screen_brightness_mode"]
    if "screen_brightness" in opts:
        brightness["screenBrightness"] = int(opts["screen_brightness"])
    timeout: dict[str, Any] = {}
    if opts.get("screen_timeout_mode"):
        timeout["screenTimeoutMode"] = opts["screen_timeout_mode"]
    if opts.get("screen_timeout"):
        timeout["screenTimeout"] = opts["screen_timeout"]
    display: dict[str, Any] = {}
    if brightness:
        display["screenBrightnessSettings"] = brightness
    if timeout:
        display["screenTimeoutSettings"] = timeout
    if display:
        policy["displaySettings"] = display

    # ── Advanced security ──
    security: dict[str, Any] = {}
    if opts.get("developer_settings"):
        security["developerSettings"] = opts["developer_settings"]
    if opts.get("untrusted_apps_policy"):
        security["untrustedAppsPolicy"] = opts["untrusted_apps_policy"]
    if opts.get("google_play_protect"):
        security["googlePlayProtectVerifyApps"] = opts["google_play_protect"]
    if security:
        policy["advancedSecurityOverrides"] = security

    # ── Boolean fields ──
    for opt_key, api_key in BOOL_FIELD_MAP.items():
        if opt_key in opts:
            policy[api_key] = opts[opt_key]

    # ── String/enum fields ──
    for opt_key, api_key in STRING_FIELD_MAP.items():
        if opts.get(opt_key):
            policy[api_key] = opts[opt_key]

    # ── Maximum time to lock ──
    max_lock = opts.get("maximum_time_to_lock")
    if max_lock and int(max_lock) > 0:
        policy["maximumTimeToLock"] = str(int(max_lock))

    # ── Stay on plugged modes ──
    plugged = opts.get("stay_on_plugged_modes")
    if plugged:
        policy["stayOnPluggedModes"] = plugged

    # ── System update ──
    if opts.get("system_update_type"):
        policy["systemUpdate"] = {"type": opts["system_update_type"]}

    # ── Support messages ──
    if opts.get("long_support_message"):
        policy["longSupportMessage"] = {
            "defaultMessage": opts["long_support_message"]
        }
    if opts.get("short_support_message"):
        policy["shortSupportMessage"] = {
            "defaultMessage": opts["short_support_message"]
        }

    # ── Device reporting (nested under statusReportingSettings) ──
    reporting: dict[str, Any] = {}
    if "software_info_enabled" in opts:
        reporting["softwareInfoEnabled"] = opts["software_info_enabled"]
    if "network_info_enabled" in opts:
        reporting["networkInfoEnabled"] = opts["network_info_enabled"]
    if "memory_info_enabled" in opts:
        reporting["memoryInfoEnabled"] = opts["memory_info_enabled"]
    if "display_info_enabled" in opts:
        reporting["displayInfoEnabled"] = opts["display_info_enabled"]
    if reporting:
        policy["statusReportingSettings"] = reporting

    return policy


# ═════════════════════════════════════════════════════════════════════════════
#  Config Flow
# ═════════════════════════════════════════════════════════════════════════════

class AndroidManagementConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Android Management API."""

    VERSION = 1

    def __init__(self) -> None:
        self._enterprise_name: str | None = None
        self._auth_method: str | None = None

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return AndroidManagementOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA)

        self._enterprise_name = user_input[CONF_ENTERPRISE_NAME]
        self._auth_method = user_input[CONF_AUTH_METHOD]

        if self._auth_method == AUTH_METHOD_JSON:
            return await self.async_step_credentials_json()
        return await self.async_step_credentials_file()

    async def async_step_credentials_json(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                creds_dict = json.loads(user_input[CONF_SERVICE_ACCOUNT_JSON])
            except (json.JSONDecodeError, TypeError):
                errors["base"] = "invalid_json"
            else:
                error = await self._validate_credentials(
                    credentials_dict=creds_dict
                )
                if error:
                    errors["base"] = error
                else:
                    await self.async_set_unique_id(self._enterprise_name)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=self._enterprise_name,
                        data={
                            CONF_ENTERPRISE_NAME: self._enterprise_name,
                            CONF_AUTH_METHOD: AUTH_METHOD_JSON,
                            CONF_SERVICE_ACCOUNT_JSON: creds_dict,
                        },
                    )

        return self.async_show_form(
            step_id="credentials_json",
            data_schema=STEP_JSON_SCHEMA,
            errors=errors,
        )

    async def async_step_credentials_file(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            file_path = user_input[CONF_FILE_PATH]
            error = await self._validate_credentials(credentials_file=file_path)
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(self._enterprise_name)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=self._enterprise_name,
                    data={
                        CONF_ENTERPRISE_NAME: self._enterprise_name,
                        CONF_AUTH_METHOD: AUTH_METHOD_FILE,
                        CONF_FILE_PATH: file_path,
                    },
                )

        return self.async_show_form(
            step_id="credentials_file",
            data_schema=STEP_FILE_SCHEMA,
            errors=errors,
        )

    async def _validate_credentials(
        self,
        credentials_dict: dict[str, Any] | None = None,
        credentials_file: str | None = None,
    ) -> str | None:
        try:
            client = await self.hass.async_add_executor_job(
                lambda: AndroidManagementAPIClient(
                    enterprise_name=self._enterprise_name,
                    credentials_dict=credentials_dict,
                    credentials_file=credentials_file,
                )
            )
            await client.async_list_devices(self.hass)
        except FileNotFoundError:
            return "file_not_found"
        except Exception:
            _LOGGER.exception("Failed to validate Android Management credentials")
            return "cannot_connect"
        return None


# ═════════════════════════════════════════════════════════════════════════════
#  Options Flow
# ═════════════════════════════════════════════════════════════════════════════

GENERAL_OPTIONS_SCHEMA = {
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): _number(
        30, 600
    ),
    vol.Optional(CONF_DEFAULT_POLICY_ID, default=""): _text(),
    vol.Optional(CONF_CLEAR_APP_DATA_PACKAGES, default=""): _text(multiline=True),
}

# ── Enterprise options (Identity, Notifications, Contact, Terms, Sign-in) ───

ENTERPRISE_IDENTITY_SCHEMA = {
    vol.Optional("enterprise_display_name", default=""): _text(),
    vol.Optional("enterprise_primary_color"): NumberSelector(
        NumberSelectorConfig(
            min=0, max=16777215, step=1, mode=NumberSelectorMode.BOX
        )
    ),
    vol.Optional("enterprise_logo_url", default=""): _text(),
    vol.Optional("enterprise_logo_sha256_hash", default=""): _text(),
}

NOTIFICATION_TYPES = [
    "ENROLLMENT",
    "COMPLIANCE_REPORT",
    "STATUS_REPORT",
    "COMMAND",
    "USAGE_LOGS",
    "ENTERPRISE_UPGRADE",
]

ENTERPRISE_NOTIFICATIONS_SCHEMA = {
    vol.Optional("enterprise_pubsub_topic", default=""): _text(),
    vol.Optional("enterprise_enabled_notification_types", default=[]): SelectSelector(
        SelectSelectorConfig(
            options=[{"value": t, "label": t} for t in NOTIFICATION_TYPES],
            multiple=True,
            mode=SelectSelectorMode.DROPDOWN,
        )
    ),
}

ENTERPRISE_CONTACT_SCHEMA = {
    vol.Optional("enterprise_contact_email", default=""): _text(),
    vol.Optional("enterprise_dpo_name", default=""): _text(),
    vol.Optional("enterprise_dpo_email", default=""): _text(),
    vol.Optional("enterprise_dpo_phone", default=""): _text(),
    vol.Optional("enterprise_eu_rep_name", default=""): _text(),
    vol.Optional("enterprise_eu_rep_email", default=""): _text(),
    vol.Optional("enterprise_eu_rep_phone", default=""): _text(),
}

ENTERPRISE_TERMS_SCHEMA = {
    vol.Optional("enterprise_terms_header", default=""): _text(),
    vol.Optional("enterprise_terms_content", default=""): _text(multiline=True),
}

ENTERPRISE_SIGNIN_SCHEMA = {
    vol.Optional("enterprise_signin_url", default=""): _text(),
    vol.Optional(
        "enterprise_signin_allow_personal_usage", default="PERSONAL_USAGE_ALLOWED"
    ): _select(["PERSONAL_USAGE_ALLOWED", "PERSONAL_USAGE_DISALLOWED"]),
    vol.Optional("enterprise_signin_token_tag", default=""): _text(),
    vol.Optional(
        "enterprise_signin_default_status",
        default="SIGNIN_DETAIL_IS_NOT_DEFAULT",
    ): _select([
        "SIGNIN_DETAIL_DEFAULT_STATUS_UNSPECIFIED",
        "SIGNIN_DETAIL_IS_DEFAULT",
        "SIGNIN_DETAIL_IS_NOT_DEFAULT",
    ]),
}


def _build_enterprise_patch_body(options: dict[str, Any]) -> dict[str, Any]:
    """Build enterprise patch body from options (Identity, Notifications, Contact, Terms, Sign-in)."""
    body: dict[str, Any] = {}

    # Identity
    if options.get("enterprise_display_name") not in (None, ""):
        body["enterpriseDisplayName"] = (options.get("enterprise_display_name") or "").strip()
    if "enterprise_primary_color" in options and options["enterprise_primary_color"] is not None:
        body["primaryColor"] = int(options["enterprise_primary_color"])
    logo_url = (options.get("enterprise_logo_url") or "").strip()
    logo_hash = (options.get("enterprise_logo_sha256_hash") or "").strip()
    if logo_url or logo_hash:
        body["logo"] = {k: v for k, v in (
            ("url", logo_url or None),
            ("sha256Hash", logo_hash or None),
        ) if v}

    # Notifications
    pubsub = (options.get("enterprise_pubsub_topic") or "").strip()
    if pubsub:
        body["pubsubTopic"] = pubsub
    types_ = options.get("enterprise_enabled_notification_types")
    if isinstance(types_, list) and types_:
        body["enabledNotificationTypes"] = types_

    # Contact info is not included: the Android Management API returns 400 with
    # "Contact info cannot be updated for your enterprise via Android Management API.
    # Please manage your enterprise's contact info via Google Admin console."
    # The contact step remains in the flow for display/consistency only.

    # Terms (one term: header + content)
    terms_header = (options.get("enterprise_terms_header") or "").strip()
    terms_content = (options.get("enterprise_terms_content") or "").strip()
    if terms_header or terms_content:
        body["termsAndConditions"] = [
            {
                "header": {"defaultMessage": terms_header, "localizedMessages": {}},
                "content": {"defaultMessage": terms_content, "localizedMessages": {}},
            }
        ]

    # Sign-in (one signin detail)
    signin_url = (options.get("enterprise_signin_url") or "").strip()
    if signin_url:
        detail: dict[str, Any] = {
            "signinUrl": signin_url,
            "allowPersonalUsage": options.get(
                "enterprise_signin_allow_personal_usage", "PERSONAL_USAGE_ALLOWED"
            ),
        }
        tag = (options.get("enterprise_signin_token_tag") or "").strip()
        if tag:
            detail["tokenTag"] = tag
        status = options.get("enterprise_signin_default_status")
        if status and status != "SIGNIN_DETAIL_DEFAULT_STATUS_UNSPECIFIED":
            detail["defaultStatus"] = status
        body["signinDetails"] = [detail]

    return body


class AndroidManagementOptionsFlow(OptionsFlow):
    """Options flow with a menu for every Android Management policy category."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._options = dict(config_entry.options)
        self._options.setdefault(
            CONF_SCAN_INTERVAL,
            config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        self._options.setdefault(
            CONF_DEFAULT_POLICY_ID,
            config_entry.data.get(CONF_DEFAULT_POLICY_ID, "")
            or config_entry.options.get(CONF_DEFAULT_POLICY_ID, ""),
        )
        self._options.setdefault(
            CONF_CLEAR_APP_DATA_PACKAGES,
            config_entry.options.get(CONF_CLEAR_APP_DATA_PACKAGES, ""),
        )
        self._policy_fetched = False
        self._enterprise_fetched = False
        for key in (
            "enterprise_display_name", "enterprise_logo_url", "enterprise_logo_sha256_hash",
            "enterprise_pubsub_topic", "enterprise_contact_email", "enterprise_dpo_name",
            "enterprise_dpo_email", "enterprise_dpo_phone", "enterprise_eu_rep_name",
            "enterprise_eu_rep_email", "enterprise_eu_rep_phone", "enterprise_terms_header",
            "enterprise_terms_content", "enterprise_signin_url", "enterprise_signin_token_tag",
        ):
            self._options.setdefault(key, "")
        self._options.setdefault("enterprise_enabled_notification_types", [])
        self._options.setdefault("enterprise_signin_allow_personal_usage", "PERSONAL_USAGE_ALLOWED")
        self._options.setdefault("enterprise_signin_default_status", "SIGNIN_DETAIL_IS_NOT_DEFAULT")

    # ── Menu ─────────────────────────────────────────────────────────────

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        # Refetch device list when user opens the integration (Configure)
        if (
            hasattr(self.config_entry, "runtime_data")
            and self.config_entry.runtime_data is not None
        ):
            await self.config_entry.runtime_data.async_request_refresh()
        if not self._policy_fetched:
            self._policy_fetched = True
            await self._fetch_live_policy()

        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "general",
                "enterprise",
                "kiosk_app",
                "kiosk_ui",
                "display",
                "security",
                "network",
                "restrictions",
                "system",
                "device_reporting",
                "apply_policy",
            ],
        )

    async def async_step_general(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Integration-wide options: scan interval, default policy for enrollment."""
        if user_input is not None:
            self._options[CONF_SCAN_INTERVAL] = int(
                user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            )
            self._options[CONF_DEFAULT_POLICY_ID] = (
                user_input.get(CONF_DEFAULT_POLICY_ID) or ""
            ).strip()
            self._options[CONF_CLEAR_APP_DATA_PACKAGES] = (
                user_input.get(CONF_CLEAR_APP_DATA_PACKAGES) or ""
            ).strip()
            return self.async_create_entry(title="", data=self._options)

        return self.async_show_form(
            step_id="general",
            data_schema=_schema_with_suggestions(
                GENERAL_OPTIONS_SCHEMA, self._options
            ),
        )

    async def _fetch_live_policy(self) -> None:
        """Fetch the current policy from the API and seed options with live values."""
        policy_id = self._options.get("policy_id", "policy1")
        try:
            coordinator = self.config_entry.runtime_data
            policy_data = await coordinator.client.async_get_policy(
                self.hass, policy_id
            )
            live_opts = parse_policy_to_options(policy_data)
            # Live values are the base; locally saved options override them
            merged = {**live_opts, **self._options}
            # Preserve the policy_id
            merged["policy_id"] = policy_id
            self._options = merged
            _LOGGER.debug(
                "Fetched live policy '%s' with %d fields", policy_id, len(live_opts)
            )
        except Exception:
            _LOGGER.debug(
                "Could not fetch live policy '%s'; using saved options only",
                policy_id,
            )

    async def _fetch_live_enterprise(self) -> None:
        """Fetch current enterprise from API and seed enterprise options."""
        try:
            coordinator = self.config_entry.runtime_data
            ent = await coordinator.client.async_get_enterprise(self.hass)
            self._options["enterprise_display_name"] = ent.get("enterpriseDisplayName") or ""
            self._options["enterprise_primary_color"] = ent.get("primaryColor")
            logo = ent.get("logo") or {}
            self._options["enterprise_logo_url"] = logo.get("url") or ""
            self._options["enterprise_logo_sha256_hash"] = logo.get("sha256Hash") or ""
            self._options["enterprise_pubsub_topic"] = ent.get("pubsubTopic") or ""
            self._options["enterprise_enabled_notification_types"] = ent.get(
                "enabledNotificationTypes", []
            )
            contact = ent.get("contactInfo") or {}
            self._options["enterprise_contact_email"] = contact.get("contactEmail") or ""
            self._options["enterprise_dpo_name"] = contact.get("dataProtectionOfficerName") or ""
            self._options["enterprise_dpo_email"] = contact.get("dataProtectionOfficerEmail") or ""
            self._options["enterprise_dpo_phone"] = contact.get("dataProtectionOfficerPhone") or ""
            self._options["enterprise_eu_rep_name"] = contact.get("euRepresentativeName") or ""
            self._options["enterprise_eu_rep_email"] = contact.get("euRepresentativeEmail") or ""
            self._options["enterprise_eu_rep_phone"] = contact.get("euRepresentativePhone") or ""
            terms = ent.get("termsAndConditions") or []
            if terms:
                t = terms[0]
                self._options["enterprise_terms_header"] = (t.get("header") or {}).get("defaultMessage") or ""
                self._options["enterprise_terms_content"] = (t.get("content") or {}).get("defaultMessage") or ""
            else:
                self._options.setdefault("enterprise_terms_header", "")
                self._options.setdefault("enterprise_terms_content", "")
            signin = ent.get("signinDetails") or []
            if signin:
                s = signin[0]
                self._options["enterprise_signin_url"] = s.get("signinUrl") or ""
                self._options["enterprise_signin_allow_personal_usage"] = s.get("allowPersonalUsage", "PERSONAL_USAGE_ALLOWED")
                self._options["enterprise_signin_token_tag"] = s.get("tokenTag") or ""
                self._options["enterprise_signin_default_status"] = s.get("defaultStatus", "SIGNIN_DETAIL_IS_NOT_DEFAULT")
            else:
                self._options.setdefault("enterprise_signin_url", "")
                self._options.setdefault("enterprise_signin_allow_personal_usage", "PERSONAL_USAGE_ALLOWED")
                self._options.setdefault("enterprise_signin_token_tag", "")
                self._options.setdefault("enterprise_signin_default_status", "SIGNIN_DETAIL_IS_NOT_DEFAULT")
            _LOGGER.debug("Fetched live enterprise; seeded options")
        except Exception:
            _LOGGER.debug("Could not fetch live enterprise; using saved options only")

    # ── Enterprise ────────────────────────────────────────────────────────

    async def async_step_enterprise(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Enterprise sub-menu: Identity, Notifications, Contact, Terms, Sign-in, Apply."""
        if not self._enterprise_fetched:
            self._enterprise_fetched = True
            await self._fetch_live_enterprise()
        return self.async_show_menu(
            step_id="enterprise",
            menu_options=[
                "enterprise_identity",
                "enterprise_notifications",
                "enterprise_terms",
                "enterprise_signin",
                "apply_enterprise",
            ],
        )

    async def async_step_enterprise_identity(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_enterprise()
        return self.async_show_form(
            step_id="enterprise_identity",
            data_schema=_schema_with_suggestions(
                ENTERPRISE_IDENTITY_SCHEMA, self._options
            ),
        )

    async def async_step_enterprise_notifications(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_enterprise()
        return self.async_show_form(
            step_id="enterprise_notifications",
            data_schema=_schema_with_suggestions(
                ENTERPRISE_NOTIFICATIONS_SCHEMA, self._options
            ),
        )

    async def async_step_enterprise_contact(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_enterprise()
        return self.async_show_form(
            step_id="enterprise_contact",
            data_schema=_schema_with_suggestions(
                ENTERPRISE_CONTACT_SCHEMA, self._options
            ),
        )

    async def async_step_enterprise_terms(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_enterprise()
        return self.async_show_form(
            step_id="enterprise_terms",
            data_schema=_schema_with_suggestions(
                ENTERPRISE_TERMS_SCHEMA, self._options
            ),
        )

    async def async_step_enterprise_signin(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_enterprise()
        return self.async_show_form(
            step_id="enterprise_signin",
            data_schema=_schema_with_suggestions(
                ENTERPRISE_SIGNIN_SCHEMA, self._options
            ),
        )

    async def async_step_apply_enterprise(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            body = _build_enterprise_patch_body(self._options)
            if not body:
                errors["base"] = "enterprise_empty"
            else:
                try:
                    coordinator = self.config_entry.runtime_data
                    await coordinator.client.async_patch_enterprise(
                        self.hass, body=body
                    )
                except Exception:
                    _LOGGER.exception("Failed to apply enterprise settings")
                    errors["base"] = "apply_enterprise_failed"
                else:
                    return self.async_create_entry(title="", data=self._options)
        schema = vol.Schema({})
        return self.async_show_form(
            step_id="apply_enterprise",
            data_schema=schema,
            errors=errors,
        )

    # ── Kiosk App ────────────────────────────────────────────────────────

    async def async_step_kiosk_app(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="kiosk_app",
            data_schema=_schema_with_suggestions(KIOSK_APP_SCHEMA, self._options),
        )

    # ── Kiosk UI ─────────────────────────────────────────────────────────

    async def async_step_kiosk_ui(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="kiosk_ui",
            data_schema=_schema_with_suggestions(KIOSK_UI_SCHEMA, self._options),
        )

    # ── Display ──────────────────────────────────────────────────────────

    async def async_step_display(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="display",
            data_schema=_schema_with_suggestions(DISPLAY_SCHEMA, self._options),
        )

    # ── Security ─────────────────────────────────────────────────────────

    async def async_step_security(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="security",
            data_schema=_schema_with_suggestions(SECURITY_SCHEMA, self._options),
        )

    # ── Network ──────────────────────────────────────────────────────────

    async def async_step_network(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="network",
            data_schema=_schema_with_suggestions(NETWORK_SCHEMA, self._options),
        )

    # ── Restrictions ─────────────────────────────────────────────────────

    async def async_step_restrictions(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="restrictions",
            data_schema=_schema_with_suggestions(RESTRICTIONS_SCHEMA, self._options),
        )

    # ── Device Reporting ─────────────────────────────────────────────────

    async def async_step_device_reporting(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="device_reporting",
            data_schema=_schema_with_suggestions(
                DEVICE_REPORTING_SCHEMA, self._options
            ),
        )

    # ── System ───────────────────────────────────────────────────────────

    async def async_step_system(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="system",
            data_schema=_schema_with_suggestions(SYSTEM_SCHEMA, self._options),
        )

    # ── Apply Policy ─────────────────────────────────────────────────────

    async def async_step_apply_policy(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            policy_id = user_input["policy_id"]
            self._options["policy_id"] = policy_id
            policy = build_policy_from_options(self._options)

            try:
                coordinator = self.config_entry.runtime_data
                await coordinator.client.async_set_policy(
                    self.hass, policy_id, policy
                )
            except Exception:
                _LOGGER.exception("Failed to apply policy '%s'", policy_id)
                errors["base"] = "apply_failed"
            else:
                return self.async_create_entry(title="", data=self._options)

        return self.async_show_form(
            step_id="apply_policy",
            data_schema=_schema_with_suggestions(APPLY_POLICY_SCHEMA, self._options),
            errors=errors,
        )
