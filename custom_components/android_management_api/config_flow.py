"""Config flow for Android Management API integration."""

from __future__ import annotations

import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
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

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENTERPRISE_NAME): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
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
        vol.Required(CONF_FILE_PATH): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
    }
)


class AndroidManagementConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Android Management API."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._enterprise_name: str | None = None
        self._auth_method: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step -- enterprise name and auth method choice."""
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
        """Handle step for pasting JSON key content."""
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
        """Handle step for providing a file path."""
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
        """Validate credentials by calling list_devices."""
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
