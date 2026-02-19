<!-- {% if not installed %} -->

## Installation

1. Add <https://github.com/Shaffer-Softworks/Android-Management> to your [HACS](https://hacs.xyz/) custom repositories.
1. Choose `Integration` from the category selection.
1. Click install.
1. Return to the Integrations page within HACS then click the `+ Explore & download repositories` button.
1. Search for `Android Management API`, select it, then click `Download this repository with HACS`.
1. Restart Home Assistant to load the integration.
1. Visit the Wiki for information regarding:
    - [Initial Setup](https://github.com/Shaffer-Softworks/Android-Management/wiki#initial-setup)
    - [Post-setup Advice](https://github.com/Shaffer-Softworks/Android-Management/wiki#post-setup-advice)
    - [Debug Logging](https://github.com/Shaffer-Softworks/Android-Management/wiki#debug-logging)

## Prerequisites

- A **Google Cloud project** with the [Android Management API](https://developers.google.com/android/management) enabled.
- A **service account** with appropriate permissions and a downloaded JSON key file.
- An **enterprise** already created via the Android Management API (you will need the enterprise resource name, e.g. `enterprises/LC00t1kz5a`).

## Configuration

1. In Home Assistant navigate to `Configuration` -> `Devices & Services` -> `Integrations`.
1. Click the `+ Add Integration` button.
1. Search for `Android Management API`.
1. If you cannot find `Android Management API` in the list then be sure to clear your browser cache and/or perform a hard-refresh of the page.
1. Enter your **Enterprise Name** (e.g. `enterprises/LC00t1kz5a`).
1. Choose your **authentication method**:
    - **Paste JSON key contents** — paste the full contents of your service account JSON key file.
    - **Provide file path on disk** — enter the absolute path to your service account JSON key file on the Home Assistant host.
1. Click `Submit`. The integration will validate your credentials by calling the API.

## Options Flow (Policy Configuration)

After setup, click **Configure** on the integration card to manage kiosk policies via a menu-driven UI:

- **Kiosk App** — Primary kiosk app + additional force-installed apps (one per line).
- **Kiosk UI** — Power button, navigation, device settings, status bar, error warnings.
- **Display** — Brightness mode/level, screen timeout mode/duration.
- **Security & Privacy** — Developer settings, keyguard, camera, screen capture, location, app verification.
- **Network & Connectivity** — Wi-Fi, Bluetooth, VPN, tethering, data roaming, mobile networks, and more.
- **Device Restrictions** — Factory reset, app install/uninstall, USB, volume, calls, SMS, accounts, and more.
- **System** — Auto-update policy, system updates, Play Store mode, support messages, and more.
- **Device Reporting** — Control which diagnostic data devices report (software info, network info, memory info, display info). Enables sensors that may show "Unknown" when disabled.
- **Apply Policy** — Push all settings to the enterprise with a single click.

The Options flow fetches the **live policy** from the enterprise so fields always show what's currently active.

## Entities Created

**Per managed device:**
- **Sensors** — State, Management Mode, Ownership, Policy Name, API Level, Enrollment Time, software info (Android version, build, kernel), network info (IMEI, WiFi MAC), memory info, non-compliance details, display count
- **Buttons** — Reboot, Lock, Reset Password, Factory Reset, Unenroll, Relinquish Ownership
- **Device Tracker** — Online (`home`) / Offline (`not_home`) based on device state

**Per enterprise:**
- **Image** — Enrollment QR Code (generates a fresh 24-hour enrollment token on demand)

## Services

- `android_management_api.set_policy` — Create or update a policy by ID with an optional raw JSON body.
- `android_management_api.set_kiosk_policy` — Create or update a kiosk policy with structured fields (primary app + additional apps, display, security, kiosk UI, and more).
- `android_management_api.create_enrollment_token` — Create an enrollment token (fires an event with the token data).
- Device-level services: `clear_app_data`, `start_lost_mode`, `stop_lost_mode`, `patch_device`, `wipe`, `add_esim`, `remove_esim`, `request_device_info`, `issue_command`, `reset_password`.

<!-- {% endif %} -->

<!-- {% if installed %} -->
# Android Management API Integration

**Features:**
- Full integration with Google's [Android Management API](https://developers.google.com/android/management)
- Two-step config flow with service account authentication (paste JSON or provide file path)
- **Options flow** with 9 categories: Kiosk App, Kiosk UI, Display, Security & Privacy, Network & Connectivity, Device Restrictions, System, **Device Reporting** (diagnostic data), Apply Policy — fetches the live policy to pre-populate fields
- **Multi-app kiosk support** — configure a primary kiosk app plus additional force-installed apps
- **DataUpdateCoordinator** polling device list every 60 seconds
- Per-device **sensors**: State, Management Mode, Ownership, Policy Name, API Level, Enrollment Time, software info (Android version, build, kernel), network info (IMEI, WiFi MAC), memory info, non-compliance details, display count
- Per-device **buttons**: Reboot, Lock, Reset Password, Factory Reset (wipe), Unenroll, Relinquish Ownership
- Per-device **device tracker**: maps `ACTIVE` state to online, all others to offline
- Enterprise-level **enrollment QR code** image entity (generates a 24-hour token on demand)
- **Services**: `set_policy`, `set_kiosk_policy`, `create_enrollment_token`; device-level: `clear_app_data`, `start_lost_mode`, `stop_lost_mode`, `patch_device`, `wipe`, `add_esim`, `remove_esim`, `request_device_info`, `issue_command`, `reset_password`
<!-- {% endif %} -->
