"""Shared helpers for the Android Management API integration."""

from __future__ import annotations

import re
from typing import Any

# Google protobuf Duration: seconds with optional fraction, ending in "s".
# screenTimeout must be strictly greater than 0.
_POSITIVE_DURATION_RE = re.compile(r"^(\d+(?:\.\d+)?)s$")

SCREEN_TIMEOUT_MODE_ENFORCED = "SCREEN_TIMEOUT_ENFORCED"
SCREEN_TIMEOUT_MODE_USER_CHOICE = "SCREEN_TIMEOUT_USER_CHOICE"
DEFAULT_SCREEN_TIMEOUT = "220s"


def parse_positive_duration(value: str) -> str:
    """Validate a Duration string that must be greater than 0 seconds.

    Raises:
        ValueError: If the value is not a positive duration ending with 's'.
    """
    text = value.strip()
    match = _POSITIVE_DURATION_RE.fullmatch(text)
    if match is None or float(match.group(1)) <= 0:
        raise ValueError(
            "duration must be greater than 0 and end with 's' (e.g. 220s, 60s)"
        )
    return text


def build_screen_timeout_settings(
    mode: str | None,
    timeout: str | None,
    *,
    default_timeout: str = DEFAULT_SCREEN_TIMEOUT,
) -> dict[str, Any]:
    """Build screenTimeoutSettings honoring Android Management API rules.

    - USER_CHOICE: mode only; screenTimeout must not be set.
    - ENFORCED (or timeout provided without USER_CHOICE): include a positive
      screenTimeout (defaulting when mode is ENFORCED).
    """
    if mode == SCREEN_TIMEOUT_MODE_USER_CHOICE:
        return {"screenTimeoutMode": mode}

    settings: dict[str, Any] = {}
    if mode:
        settings["screenTimeoutMode"] = mode

    raw = timeout
    if not raw and mode == SCREEN_TIMEOUT_MODE_ENFORCED:
        raw = default_timeout
    if raw:
        settings["screenTimeout"] = parse_positive_duration(raw)
        # API requires ENFORCED whenever screenTimeout is set.
        settings.setdefault("screenTimeoutMode", SCREEN_TIMEOUT_MODE_ENFORCED)
    return settings
