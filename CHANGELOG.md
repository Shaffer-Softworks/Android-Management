# Changelog

All notable changes to the Android Management API integration for Home Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/Shaffer-Softworks/Android-Management/releases/tag/v0.1.0
