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

After setup, click **Configure** on the integration card to manage policies via a menu-driven UI:

- **Kiosk App** — Primary app (including `CUSTOM` install type), application roles, signing key cert SHA-256, additional force-installed apps.
- **Kiosk UI** — Power button, navigation, device settings, status bar, error warnings.
- **Display** — Brightness mode/level, screen timeout mode/duration.
- **Security & Privacy** — Developer settings, keyguard, camera, screen capture, location, app verification, autofill, enterprise display name visibility, app functions, private space, wipe data flags.
- **Network & Connectivity** — Wi-Fi, Bluetooth, VPN, tethering, private DNS, Bluetooth sharing, user-initiated eSIM add, plus optional JSON for APN / preferential network / Wi-Fi roaming / default apps.
- **Device Restrictions** — Factory reset, app install/uninstall, USB, volume, calls, SMS, accounts, and more.
- **System** — Auto-update policy, system updates, Play Store mode, support messages, and more.
- **General** — Scan interval, default policy for enrollment QR code, package names for Clear app data button.
- **Enterprise** — Identity (display name, primary color, logo), Notifications, Terms & Conditions, Sign-in (contact info is managed in Google Admin console).
- **Device Reporting** — Software, network, memory, display, application reports, and default application info reporting.
- **Apply Policy** — Push all settings to the enterprise with a single click.

The Options flow fetches the **live policy and enterprise** so fields always show what's currently active.

## Entities Created

**Per managed device:**
- **Sensors** — State, management/policy, software & network info, memory, non-compliance, enrollment token data, device trust, EID, telephony, application report count, signing cert SHA-256, default application info
- **Buttons** — Reboot, Lock, Reset Password, Factory Reset (delete), Wipe (`WIPE`), Unenroll, Relinquish Ownership, Clear app data, Start/Stop Lost Mode, Request Device Info

**Per enterprise:**
- **Image** — Enrollment QR Code (generates a fresh 24-hour enrollment token on demand; uses default policy from options)

## Services

- `android_management_api.set_policy` — Create or update a policy by ID with an optional raw JSON body.
- `android_management_api.set_kiosk_policy` — Structured kiosk fields (including optional `application_roles` and `signing_key_cert_sha256`).
- `android_management_api.modify_policy_applications` / `remove_policy_applications` — Partial application list updates.
- `android_management_api.create_enrollment_token` — Create an enrollment token (policy_id, one_time_only, additional_data, allow_personal_usage; fires an event with the token data).
- Device-level: `clear_app_data`, `start_lost_mode`, `stop_lost_mode`, `patch_device`, `wipe`, `add_esim`, `remove_esim`, `request_device_info`, `issue_command`, `reset_password`.
- Enterprise/API: `list_policies`, `list_enrollment_tokens`, `delete_enrollment_token`, `get_operation`, `get_enterprise`, `patch_enterprise`, `create_web_token`, `refresh`.

<!-- {% endif %} -->

<!-- {% if installed %} -->
# Android Management API Integration

**Features:**
- Full integration with Google's [Android Management API](https://developers.google.com/android/management)
- Two-step config flow with service account authentication (paste JSON or provide file path)
- **Options flow** with **General**, **Enterprise**, and policy categories (including 2025–2026 fields: application roles, autofill, private DNS, eSIM controls, reporting toggles, advanced JSON) — fetches live policy and enterprise to pre-populate fields
- **Multi-app kiosk support** — configure a primary kiosk app plus additional force-installed apps
- **DataUpdateCoordinator** with configurable scan interval (default 60 s)
- Per-device **sensors**: state/policy, software & network, memory, non-compliance, enrollment token data, device trust, EID, telephony, application reports / signing cert SHA-256, default application info
- Per-device **buttons**: Reboot, Lock, Reset Password, Factory Reset (delete), Wipe (`WIPE`), Unenroll, Relinquish Ownership, Clear app data, Start/Stop Lost Mode, Request Device Info
- Enterprise-level **enrollment QR code** image entity (24-hour token on demand; default policy from options)
- **Services**: `set_policy`, `set_kiosk_policy`, `modify_policy_applications`, `remove_policy_applications`, `create_enrollment_token`; device-level and enterprise services as listed above; `refresh` to force a device-list poll
<!-- {% endif %} -->
