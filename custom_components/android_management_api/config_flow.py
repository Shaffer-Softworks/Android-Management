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
    CONF_ENTERPRISE_NAME,
    CONF_FILE_PATH,
    CONF_SERVICE_ACCOUNT_JSON,
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


def build_policy_from_options(opts: dict[str, Any]) -> dict[str, Any]:
    """Construct a full Android Management API policy dict from stored options."""
    policy: dict[str, Any] = {}

    # ── Application ──
    pkg = opts.get("package_name")
    if pkg:
        app_policy: dict[str, Any] = {"packageName": pkg}
        if opts.get("install_type"):
            app_policy["installType"] = opts["install_type"]
        if opts.get("auto_update_mode"):
            app_policy["autoUpdateMode"] = opts["auto_update_mode"]
        if "lock_task_allowed" in opts:
            app_policy["lockTaskAllowed"] = opts["lock_task_allowed"]
        if opts.get("default_permission_policy"):
            app_policy["defaultPermissionPolicy"] = opts["default_permission_policy"]
        policy["applications"] = [app_policy]

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

class AndroidManagementOptionsFlow(OptionsFlow):
    """Options flow with a menu for every Android Management policy category."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._options: dict[str, Any] = dict(config_entry.options)

    # ── Menu ─────────────────────────────────────────────────────────────

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "kiosk_app",
                "kiosk_ui",
                "display",
                "security",
                "network",
                "restrictions",
                "system",
                "apply_policy",
            ],
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
