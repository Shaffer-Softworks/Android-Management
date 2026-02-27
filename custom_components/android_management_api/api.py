"""Google Android Management API client wrapper."""

from __future__ import annotations

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

    async def async_get_enterprise(self, hass) -> dict[str, Any]:
        """Get the enterprise resource (display name, logo, contact, signin, etc.)."""
        return await hass.async_add_executor_job(self._get_enterprise)

    def _get_enterprise(self) -> dict[str, Any]:
        """Get enterprise (synchronous)."""
        return (
            self._service.enterprises()
            .get(name=self._enterprise_name)
            .execute()
        )

    async def async_patch_enterprise(
        self,
        hass,
        body: dict[str, Any],
        update_mask: str | None = None,
    ) -> dict[str, Any]:
        """Update enterprise (partial patch). update_mask is comma-separated field names."""
        return await hass.async_add_executor_job(
            self._patch_enterprise, body, update_mask
        )

    def _patch_enterprise(
        self,
        body: dict[str, Any],
        update_mask: str | None = None,
    ) -> dict[str, Any]:
        """Patch enterprise (synchronous)."""
        kwargs: dict[str, Any] = {"name": self._enterprise_name, "body": body}
        if update_mask:
            kwargs["updateMask"] = update_mask
        return self._service.enterprises().patch(**kwargs).execute()

    async def async_create_web_token(
        self,
        hass,
        parent_frame_url: str | None = None,
        enabled_features: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a web token for the embeddable managed Google Play iframe."""
        return await hass.async_add_executor_job(
            self._create_web_token, parent_frame_url, enabled_features
        )

    def _create_web_token(
        self,
        parent_frame_url: str | None = None,
        enabled_features: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create web token (synchronous). parent_frame_url is required for iframe hosting."""
        body: dict[str, Any] = {}
        if parent_frame_url:
            body["parentFrameUrl"] = parent_frame_url
        if enabled_features:
            body["enabledFeatures"] = enabled_features
        return (
            self._service.enterprises()
            .webTokens()
            .create(parent=self._enterprise_name, body=body)
            .execute()
        )

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

    async def async_patch_device(
        self,
        hass,
        device_name: str,
        state: str | None = None,
        policy_name: str | None = None,
        disabled_reason: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Patch a device (state, policy, disabled reason)."""
        return await hass.async_add_executor_job(
            self._patch_device, device_name, state, policy_name, disabled_reason
        )

    def _patch_device(
        self,
        device_name: str,
        state: str | None = None,
        policy_name: str | None = None,
        disabled_reason: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Patch a device (synchronous)."""
        body: dict[str, Any] = {}
        if state is not None:
            body["state"] = state
        if policy_name is not None:
            body["policyName"] = policy_name
        if disabled_reason is not None:
            body["disabledReason"] = disabled_reason
        return (
            self._service.enterprises()
            .devices()
            .patch(name=device_name, body=body, updateMask=",".join(body.keys()))
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

    async def async_list_policies(self, hass) -> list[dict[str, Any]]:
        """List all policies for the enterprise."""
        return await hass.async_add_executor_job(self._list_policies)

    def _list_policies(self) -> list[dict[str, Any]]:
        """List all policies (synchronous)."""
        policies: list[dict[str, Any]] = []
        request = (
            self._service.enterprises()
            .policies()
            .list(parent=self._enterprise_name)
        )
        while request is not None:
            response = request.execute()
            if "policies" in response:
                policies.extend(response["policies"])
            request = (
                self._service.enterprises()
                .policies()
                .list_next(previous_request=request, previous_response=response)
            )
        return policies

    async def async_list_enrollment_tokens(self, hass) -> list[dict[str, Any]]:
        """List active enrollment tokens for the enterprise."""
        return await hass.async_add_executor_job(self._list_enrollment_tokens)

    def _list_enrollment_tokens(self) -> list[dict[str, Any]]:
        """List enrollment tokens (synchronous)."""
        tokens: list[dict[str, Any]] = []
        request = (
            self._service.enterprises()
            .enrollmentTokens()
            .list(parent=self._enterprise_name)
        )
        while request is not None:
            response = request.execute()
            if "enrollmentTokens" in response:
                tokens.extend(response["enrollmentTokens"])
            request = (
                self._service.enterprises()
                .enrollmentTokens()
                .list_next(previous_request=request, previous_response=response)
            )
        return tokens

    async def async_delete_enrollment_token(
        self, hass, token_name: str
    ) -> dict[str, Any]:
        """Delete an enrollment token by full resource name."""
        return await hass.async_add_executor_job(
            self._delete_enrollment_token, token_name
        )

    def _delete_enrollment_token(self, token_name: str) -> dict[str, Any]:
        """Delete an enrollment token (synchronous)."""
        return (
            self._service.enterprises()
            .enrollmentTokens()
            .delete(name=token_name)
            .execute()
        )

    async def async_get_operation(
        self, hass, operation_name: str
    ) -> dict[str, Any]:
        """Get status of a device operation (e.g. command)."""
        return await hass.async_add_executor_job(
            self._get_operation, operation_name
        )

    def _get_operation(self, operation_name: str) -> dict[str, Any]:
        """Get operation (synchronous)."""
        return (
            self._service.enterprises()
            .devices()
            .operations()
            .get(name=operation_name)
            .execute()
        )

    async def async_create_enrollment_token(
        self,
        hass,
        policy_name: str | None = None,
        policy_id: str | None = None,
        duration: str = DEFAULT_TOKEN_DURATION,
        one_time_only: bool = False,
        additional_data: str | None = None,
        allow_personal_usage: str | None = None,
    ) -> dict[str, Any]:
        """Create an enrollment token."""
        return await hass.async_add_executor_job(
            self._create_enrollment_token,
            policy_name,
            policy_id,
            duration,
            one_time_only,
            additional_data,
            allow_personal_usage,
        )

    def _create_enrollment_token(
        self,
        policy_name: str | None = None,
        policy_id: str | None = None,
        duration: str = DEFAULT_TOKEN_DURATION,
        one_time_only: bool = False,
        additional_data: str | None = None,
        allow_personal_usage: str | None = None,
    ) -> dict[str, Any]:
        """Create an enrollment token (synchronous)."""
        body: dict[str, Any] = {"duration": duration}
        if policy_name:
            body["policyName"] = policy_name
        elif policy_id:
            body["policyName"] = f"{self._enterprise_name}/policies/{policy_id}"
        if one_time_only:
            body["oneTimeOnly"] = True
        if additional_data is not None and additional_data != "":
            if len(additional_data) > 1024:
                raise ValueError("additionalData must be 1024 characters or less")
            body["additionalData"] = additional_data
        if allow_personal_usage is not None:
            body["allowPersonalUsage"] = allow_personal_usage
        return (
            self._service.enterprises()
            .enrollmentTokens()
            .create(parent=self._enterprise_name, body=body)
            .execute()
        )
