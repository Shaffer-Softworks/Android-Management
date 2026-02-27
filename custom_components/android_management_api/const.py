"""Constants for the Android Management API integration."""

from homeassistant.const import Platform

DOMAIN = "android_management_api"

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BUTTON,
    Platform.IMAGE,
]

OAUTH_SCOPE = "https://www.googleapis.com/auth/androidmanagement"
APP_NAME = "Home Assistant Android Management"

DEFAULT_SCAN_INTERVAL = 60
DEFAULT_TOKEN_DURATION = "86400s"
DEFAULT_POLICY_ID = "policy1"

CONF_ENTERPRISE_NAME = "enterprise_name"
CONF_SERVICE_ACCOUNT_JSON = "service_account_json"
CONF_AUTH_METHOD = "auth_method"
CONF_FILE_PATH = "file_path"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DEFAULT_POLICY_ID = "default_policy_id"
CONF_CLEAR_APP_DATA_PACKAGES = "clear_app_data_package_names"

AUTH_METHOD_JSON = "json"
AUTH_METHOD_FILE = "file"

ALLOW_PERSONAL_USAGE_VALUES = ("PERSONAL_USAGE_ALLOWED", "PERSONAL_USAGE_DISALLOWED")
