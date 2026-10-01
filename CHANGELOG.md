# Changelog

All notable changes to the Android Management API integration for Home Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **Screen timeout validation**: Reject non-positive / malformed `screen_timeout` values in the Display options step and `set_kiosk_policy` service before calling the API. Remove incorrect `0s (never)` hint text — the Android Management API requires a duration greater than 0. When timeout mode is `SCREEN_TIMEOUT_USER_CHOICE`, omit `screenTimeout` from the policy body as required by Google.

## [1.0.0] - 2026-07-17

### Added

- **Policy Options** for 2025–2026 Android Management API fields: application roles, `CUSTOM` install type + signing key cert, autofill, enterprise display name visibility, app functions, private space, wipe data flags, private DNS, Bluetooth sharing, user-initiated eSIM add, application/default-app reporting toggles, and optional JSON for APN / preferential network / Wi-Fi roaming / default application settings.
- **Services** `modify_policy_applications` and `remove_policy_applications` (partial application list updates without a full policy patch).
- **Buttons**: Wipe (`WIPE` command), Start/Stop Lost Mode, Request Device Info (EID).
- **Sensors**: EID, Telephony Info, Application Report Count, Signing Cert SHA-256, Default Application Info.
- `set_kiosk_policy` optional `application_roles` and `signing_key_cert_sha256`.

### Changed

- Dependencies: `google-api-python-client==2.198.0`, `google-auth==2.56.0`.
- `request_device_info` now sends `deviceInfo` as the API enum string (not a list).

### Fixed

- Request device info command parameter shape aligned with the Android Management API.

## [0.1.6] - 2026-02-27

### Added

- **Refresh service** (`android_management_api.refresh`): Manually refresh the device list from the API (Developer Tools → Services).
- **Refresh on Configure**: Device list is refetched when you open the integration’s Configure screen.
- **API retry**: All API requests retry up to 3 times on transient SSL or network errors (e.g. record layer failure, timeout). Retry messages log at DEBUG so successful retries don’t clutter the log.

### Fixed

- **Enterprise contact**: Contact info cannot be updated via the Android Management API (Google returns 400). The integration no longer sends `contactInfo` in enterprise patch requests. The Enterprise contact step has been removed from the options menu; manage contact details in the Google Admin console.
- **Device list not updating**: Coordinator now keeps a permanent listener so periodic refresh is always scheduled. Stale devices (no longer returned by the API) are removed from the device and entity registries on startup and when the coordinator updates. New devices get sensors and buttons without reloading the integration.
- **UnboundLocalError** in sensor/button platform sync when updating the device list (fixed by using `set.intersection_update()` instead of `&=` in closure).

### Changed

- Scan interval is coerced to `int` when creating the coordinator.
- Service descriptions updated to note that contact info must be managed in Google Admin console.

---

## [0.1.5] - 2026-02-27

### Added

- **General options** (Configure → General): Scan interval (API polling, seconds), default policy ID for enrollment QR code, optional package names for the Clear app data button (one per line or comma-separated).
- **Enterprise options** (Configure → Enterprise): Identity (display name, primary color, logo URL + SHA-256 hash), Notifications (Pub/Sub topic, enabled types), Contact (email, DPO, EU rep), Terms & Conditions, Sign-in (URL, token tag, allow personal usage). Apply step pushes enterprise settings to the API.
- **New sensors**: Enrollment Token Data, Device Trust (when reported by API).
- **Clear app data button**: Per-device button that clears app data for packages configured in General options.
- **Enrollment token options**: `create_enrollment_token` and QR code support `policy_id`, `one_time_only`, `additional_data`, `allow_personal_usage`.
- **New services**: `list_policies`, `list_enrollment_tokens`, `delete_enrollment_token`, `get_operation`, `get_enterprise`, `patch_enterprise`, `create_web_token`.
- **Entity registry cleanup**: On setup/reload, any legacy device_tracker entities for this integration are automatically removed from the entity registry.

### Removed

- **Device tracker platform**: The Android Management API does not provide device location/GPS; the device tracker only reflected management state (ACTIVE = home). The platform has been removed. Existing device_tracker entities are removed from the registry when the integration is reloaded.

### Fixed

- **Entity registry API**: Use `registry.entities.get_entries_for_config_entry_id()` for compatibility with current Home Assistant versions when removing legacy device_tracker entities.

---

## [0.1.1] - 2026-02-18

### Added

- **Device reporting**
  - Device Reporting policy category in Options flow: enable software info, network info, memory info, and display info to populate additional sensors.
  - New sensors (when enabled in policy): Total RAM (MB), Total Internal Storage (MB), Total External Storage (MB), Non-Compliance Count, Non-Compliance Details, Display Count.
  - **Relinquish Ownership** button — per-device command to relinquish device ownership.

### Fixed

- **Translations** — Entity translation keys updated to comply with hassfest validation (removed invalid `domain__key` format).

---

## [0.1.0] - 2026-02-18

### Added

- **Integration**
  - Config flow setup with Enterprise Name and authentication (paste JSON key or file path).
  - Options flow for policy configuration with 8 categories; fetches live policy from the enterprise when opened.

- **Platforms**
  - **Sensor** — Per-device diagnostics: State, Management Mode, Ownership, Policy Name, API Level, Enrollment Time, plus Android version, kernel version, bootloader version, device policy version, baseband version, and applied policy version.
  - **Button** — Per-device commands: Reboot, Lock, Reset Password, Factory Reset, Unenroll.
  - **Device tracker** — Per-device online/offline based on device state (`ACTIVE` → home, others → not_home).
  - **Image** — Enterprise-level enrollment QR code generated on demand (24-hour token).

- **Policy management**
  - Full Options flow UI for kiosk policies: Kiosk App, Kiosk UI, Display, Security & Privacy, Network & Connectivity, Device Restrictions, System, and Apply Policy.
  - Multi-app kiosk support: primary kiosk app plus additional force-installed apps (one per line).
  - Service `android_management_api.set_policy` — create/update policy with raw JSON.
  - Service `android_management_api.set_kiosk_policy` — create/update kiosk policy with structured fields (package, display, security, etc.).
  - Service `android_management_api.create_enrollment_token` — programmatic enrollment token creation; fires `android_management_api_enrollment_token_created` event.

- **Device inventory**
  - All managed devices discovered and represented as Home Assistant devices with manufacturer, model, and serial number.

- **Dependencies**
  - `google-api-python-client==2.159.0`, `google-auth==2.37.0`, `qrcode==8.0`.

- **Compatibility**
  - Home Assistant 2024.4.0 or newer.
  - HACS 1.34.0 or newer (when installed via HACS).

[0.1.6]: https://github.com/Shaffer-Softworks/Android-Management/releases/tag/v0.1.6
[0.1.5]: https://github.com/Shaffer-Softworks/Android-Management/releases/tag/v0.1.5
[0.1.1]: https://github.com/Shaffer-Softworks/Android-Management/releases/tag/v0.1.1
[0.1.0]: https://github.com/Shaffer-Softworks/Android-Management/releases/tag/v0.1.0
