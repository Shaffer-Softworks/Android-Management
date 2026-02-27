# Changelog

All notable changes to the Android Management API integration for Home Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.5]: https://github.com/Shaffer-Softworks/Android-Management/releases/tag/v0.1.5
[0.1.1]: https://github.com/Shaffer-Softworks/Android-Management/releases/tag/v0.1.1
[0.1.0]: https://github.com/Shaffer-Softworks/Android-Management/releases/tag/v0.1.0
