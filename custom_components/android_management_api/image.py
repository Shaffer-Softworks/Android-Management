"""Image platform for Android Management API -- enrollment QR code."""

from __future__ import annotations

from datetime import datetime
import io
import json
import logging
from typing import Any

import qrcode

from homeassistant.components.image import ImageEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AndroidManagementConfigEntry
from .const import (
    CONF_DEFAULT_POLICY_ID,
    CONF_ENTERPRISE_NAME,
    DEFAULT_TOKEN_DURATION,
    DOMAIN,
)
from .coordinator import AndroidManagementCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AndroidManagementConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the enrollment QR code image entity."""
    coordinator = entry.runtime_data
    enterprise_name = entry.data[CONF_ENTERPRISE_NAME]
    default_policy_id = entry.options.get(CONF_DEFAULT_POLICY_ID) or entry.data.get(
        CONF_DEFAULT_POLICY_ID, ""
    )
    async_add_entities(
        [
            EnrollmentQRCodeImage(
                coordinator, enterprise_name, default_policy_id=default_policy_id
            )
        ]
    )


class EnrollmentQRCodeImage(ImageEntity):
    """Image entity that renders an enrollment QR code."""

    _attr_has_entity_name = True
    _attr_name = "Enrollment QR Code"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: AndroidManagementCoordinator,
        enterprise_name: str,
        default_policy_id: str = "",
    ) -> None:
        super().__init__(coordinator.hass)
        self._coordinator = coordinator
        self._enterprise_name = enterprise_name
        self._default_policy_id = (default_policy_id or "").strip()
        self._attr_unique_id = f"{enterprise_name}_enrollment_qr"
        self._qr_bytes: bytes | None = None
        self._attr_image_last_updated = datetime.now()

    @property
    def device_info(self) -> DeviceInfo:
        """Place under an enterprise-level device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._enterprise_name)},
            name=f"Enterprise {self._enterprise_name.rsplit('/', 1)[-1]}",
            manufacturer="Google",
            model="Android Management",
        )

    async def async_image(self) -> bytes | None:
        """Generate a fresh QR code from a new enrollment token."""
        try:
            token_data = await self._coordinator.client.async_create_enrollment_token(
                self._coordinator.hass,
                policy_id=self._default_policy_id or None,
                duration=DEFAULT_TOKEN_DURATION,
            )
            qr_value = token_data.get("qrCode", "")
            if not qr_value:
                _LOGGER.warning("Enrollment token response did not contain a qrCode")
                return None

            self._qr_bytes = await self._coordinator.hass.async_add_executor_job(
                self._render_qr, qr_value
            )
            self._attr_image_last_updated = datetime.now()
            return self._qr_bytes
        except Exception:
            _LOGGER.exception("Failed to generate enrollment QR code")
            return self._qr_bytes

    @staticmethod
    def _render_qr(data: str) -> bytes:
        """Render QR code PNG bytes."""
        img = qrcode.make(data)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    @property
    def content_type(self) -> str:
        """Return the content type of the image."""
        return "image/png"
