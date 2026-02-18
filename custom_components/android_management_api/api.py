"""Google Android Management API client wrapper."""

from __future__ import annotations

import json
import logging
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from .const import DEFAULT_TOKEN_DURATION, OAUTH_SCOPE

_LOGGER = logging.getLogger(__name__)

SCOPES = [OAUTH_SCOPE]


class AndroidManagementAPIClient:
    """Wrapper around the Google Android Management API v1."""

    def __init__(
        self,
        enterprise_name: str,
        credentials_dict: dict[str, Any] | None = None,
        credentials_file: str | None = None,
    ) -> None:
        self._enterprise_name = enterprise_name
        self._credentials_dict = credentials_dict
        self._credentials_file = credentials_file
        self._service = self._build_service()

    def _build_service(self):
        """Build the androidmanagement API service client."""
        if self._credentials_dict:
            creds = service_account.Credentials.from_service_account_info(
                self._credentials_dict, scopes=SCOPES
            )
        elif self._credentials_file:
            creds = service_account.Credentials.from_service_account_file(
                self._credentials_file, scopes=SCOPES
            )
        else:
            raise ValueError("No credentials provided")

        return build(
            "androidmanagement",
            "v1",
            credentials=creds,
            cache_discovery=False,
        )

    @property
    def enterprise_name(self) -> str:
        """Return the enterprise name."""
        return self._enterprise_name

    async def async_list_devices(self, hass) -> list[dict[str, Any]]:
        """List all devices for the enterprise."""
        return await hass.async_add_executor_job(self._list_devices)

    def _list_devices(self) -> list[dict[str, Any]]:
        """List all devices (synchronous)."""
        devices: list[dict[str, Any]] = []
        request = (
            self._service.enterprises()
            .devices()
            .list(parent=self._enterprise_name)
        )
        while request is not None:
            response = request.execute()
            if "devices" in response:
                devices.extend(response["devices"])
            request = (
                self._service.enterprises()
                .devices()
                .list_next(previous_request=request, previous_response=response)
            )
        return devices

    async def async_get_device(
        self, hass, device_name: str
    ) -> dict[str, Any]:
        """Get a single device by full resource name."""
        return await hass.async_add_executor_job(self._get_device, device_name)

    def _get_device(self, device_name: str) -> dict[str, Any]:
        """Get a single device (synchronous)."""
        return (
            self._service.enterprises()
            .devices()
            .get(name=device_name)
            .execute()
        )

    async def async_issue_command(
        self, hass, device_name: str, command_type: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Issue a command to a device."""
        return await hass.async_add_executor_job(
            self._issue_command, device_name, command_type, kwargs
        )

    def _issue_command(
        self, device_name: str, command_type: str, extra: dict[str, Any]
    ) -> dict[str, Any]:
        """Issue a command (synchronous)."""
        body: dict[str, Any] = {"type": command_type, **extra}
        return (
            self._service.enterprises()
            .devices()
            .issueCommand(name=device_name, body=body)
            .execute()
        )

    async def async_delete_device(
        self,
        hass,
        device_name: str,
        wipe_data_flags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Delete (unenroll/wipe) a device."""
        return await hass.async_add_executor_job(
            self._delete_device, device_name, wipe_data_flags
        )

    def _delete_device(
        self, device_name: str, wipe_data_flags: list[str] | None = None
    ) -> dict[str, Any]:
        """Delete a device (synchronous)."""
        kwargs: dict[str, Any] = {"name": device_name}
        if wipe_data_flags:
            kwargs["wipeDataFlags"] = wipe_data_flags
        return (
            self._service.enterprises().devices().delete(**kwargs).execute()
        )

    async def async_set_policy(
        self, hass, policy_id: str, policy_body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create or update a policy."""
        return await hass.async_add_executor_job(
            self._set_policy, policy_id, policy_body
        )

    def _set_policy(
        self, policy_id: str, policy_body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Set a policy (synchronous)."""
        name = f"{self._enterprise_name}/policies/{policy_id}"
        body = policy_body or {}
        return (
            self._service.enterprises()
            .policies()
            .patch(name=name, body=body)
            .execute()
        )

    async def async_get_policy(
        self, hass, policy_id: str
    ) -> dict[str, Any]:
        """Get a policy by ID."""
        return await hass.async_add_executor_job(self._get_policy, policy_id)

    def _get_policy(self, policy_id: str) -> dict[str, Any]:
        """Get a policy (synchronous)."""
        name = f"{self._enterprise_name}/policies/{policy_id}"
        return (
            self._service.enterprises().policies().get(name=name).execute()
        )

    async def async_create_enrollment_token(
        self,
        hass,
        policy_name: str | None = None,
        duration: str = DEFAULT_TOKEN_DURATION,
    ) -> dict[str, Any]:
        """Create an enrollment token."""
        return await hass.async_add_executor_job(
            self._create_enrollment_token, policy_name, duration
        )

    def _create_enrollment_token(
        self, policy_name: str | None = None, duration: str = DEFAULT_TOKEN_DURATION
    ) -> dict[str, Any]:
        """Create an enrollment token (synchronous)."""
        body: dict[str, Any] = {"duration": duration}
        if policy_name:
            body["policyName"] = policy_name
        return (
            self._service.enterprises()
            .enrollmentTokens()
            .create(parent=self._enterprise_name, body=body)
            .execute()
        )
