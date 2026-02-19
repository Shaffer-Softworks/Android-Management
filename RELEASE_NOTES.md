# Release notes

Use the section below when creating a new [GitHub Release](https://github.com/Shaffer-Softworks/Android-Management/releases). Copy the block for the version you are releasing.

---

## v0.1.0 (2026-02-18)

Initial release of the **Android Management API** custom component for Home Assistant. Manage Android enterprise devices directly from Home Assistant using [Google's Android Management API](https://developers.google.com/android/management).

### Platforms

| Platform | Description |
|----------|-------------|
| **Sensor** | Per-device diagnostics: State, Management Mode, Ownership, Policy Name, API Level, Enrollment Time, and additional version/device info. |
| **Button** | Per-device commands: Reboot, Lock, Reset Password, Factory Reset, Unenroll. |
| **Device tracker** | Per-device online/offline based on device state. |
| **Image** | Enrollment QR code generated on demand (24-hour token). |

### Features

- **Full device inventory** — Managed devices appear as Home Assistant devices with manufacturer, model, and serial number.
- **Device commands** — Reboot, lock, reset password, factory reset, and unenroll from the UI.
- **Online/offline tracking** — Device tracker maps `ACTIVE` to home and other states to not_home.
- **Enrollment QR code** — Fresh 24-hour enrollment token rendered as a QR code image.
- **Kiosk policy UI** — Options flow with 8 categories (Kiosk App, Kiosk UI, Display, Security, Network, Restrictions, System, Apply). Fetches live policy so fields reflect current enterprise settings.
- **Multi-app kiosk** — Primary kiosk app plus additional force-installed apps.
- **Services** — `set_policy`, `set_kiosk_policy`, and `create_enrollment_token` for automations and scripts.
- **Authentication** — Paste service account JSON or provide a file path.

### Requirements

- Home Assistant 2024.4.0+
- Google Cloud project with Android Management API enabled
- Service account with a JSON key and an existing enterprise

### Installation

- **HACS**: Add `https://github.com/Shaffer-Softworks/Android-Management` as a custom repository, then install the integration.
- **Manual**: Download the [latest release](https://github.com/Shaffer-Softworks/Android-Management/releases) zip and place `android_management_api` in `custom_components`. Restart Home Assistant.

See the [README](https://github.com/Shaffer-Softworks/Android-Management#readme) and [Wiki](https://github.com/Shaffer-Softworks/Android-Management/wiki) for setup and configuration.
