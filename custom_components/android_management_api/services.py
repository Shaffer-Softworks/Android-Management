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
SERVICE_CREATE_ENROLLMENT_TOKEN = "create_enrollment_token"

ATTR_POLICY_ID = "policy_id"
ATTR_POLICY_BODY = "policy_body"
ATTR_POLICY_NAME = "policy_name"
ATTR_DURATION = "duration"

SET_POLICY_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_POLICY_ID): cv.string,
        vol.Optional(ATTR_POLICY_BODY): cv.string,
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
        SERVICE_CREATE_ENROLLMENT_TOKEN,
        handle_create_enrollment_token,
        schema=CREATE_ENROLLMENT_TOKEN_SCHEMA,
    )
