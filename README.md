# Android Management API custom component for Home Assistant

<img width="256" height="256" alt="logo" src="https://github.com/user-attachments/assets/90aad15f-02db-4a05-8547-200d7b8729c7" />

[![Validate](https://github.com/Shaffer-Softworks/Android-Management/actions/workflows/validate.yaml/badge.svg)](https://github.com/Shaffer-Softworks/Android-Management/actions/workflows/validate.yaml)
[![CodeQL](https://github.com/Shaffer-Softworks/Android-Management/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Shaffer-Softworks/Android-Management/actions/workflows/github-code-scanning/codeql)

Manage your Android devices directly from Home Assistant using [Google's Android Management API](https://developers.google.com/android/management).

### Why use Android Management (DPC)?

Enrolling devices with Android Management (and the built-in Device Policy Controller, or DPC) gives you centralized control and security:

- **Kiosks and single-purpose devices** — Lock devices to one app (or a small set of apps), hide the status bar and navigation, and control power and display so they stay in kiosk mode for displays, point-of-sale, or signage.
- **Security and compliance** — Enforce policies (e.g. no unknown sources, screen lock, encryption), manage OS and app updates, and restrict USB, camera, or settings as needed for company or compliance requirements.
- **Remote management** — Reboot, lock, reset password, or wipe devices from Home Assistant; put devices in lost mode with a custom message and contact info; or unenroll/relinquish ownership when devices are retired or reassigned.
- **Visibility and control** — See device state, policy, and diagnostics (API level, memory, non-compliance) in Home Assistant; apply or change policies from the integration or automations so devices stay in the right configuration.
- **Unified management from Home Assistant** — Use one place (HA) to manage Android devices alongside the rest of your setup, with sensors, buttons, and services you can use in dashboards and automations.

**This component will set up the following platforms.**

| Platform | Description |
|----------|-------------|
| `sensor` | Per-device diagnostic sensors: State, Management Mode, Ownership, Policy Name, API Level, Enrollment Time, software info (Android version, build, kernel), network info (IMEI, WiFi MAC), memory info, non-compliance details, display count, enrollment token data, device trust signal. |
| `button` | Per-device command buttons: Reboot, Lock, Reset Password, Factory Reset, Unenroll, Relinquish Ownership, Clear app data (uses package names from integration options). |
| `image` | Enterprise-level enrollment QR code generated on demand (uses default policy from integration options). |

### Key Features

- **Full Device Inventory**: All managed devices are automatically discovered and represented as Home Assistant devices with manufacturer, model, and serial number.
- **Device Commands**: Reboot, lock, reset password, factory reset (wipe), unenroll, relinquish ownership, and clear app data with a single button press; plus device-level services for lost mode, eSIM, and more.
- **Enrollment QR Code**: Generate a fresh 24-hour enrollment token and render it as a QR code image (optionally bound to a default policy) — ready to scan on a new device.
- **Kiosk Policy Management**: Full Options flow UI for configuring kiosk policies — app settings, display, security, network, restrictions, and system settings. Fetches the live policy so fields always reflect what's currently set on the enterprise.
- **Multi-App Kiosk Support**: Configure a primary kiosk app plus additional force-installed apps.
- **Policy Management Service**: Use the `set_policy` or `set_kiosk_policy` services to manage policies from automations or scripts.
- **Enrollment Token Service**: Use the `create_enrollment_token` service to programmatically generate enrollment tokens (fires an event with the full token data).
- **Flexible Authentication**: Authenticate with a pasted service account JSON key or a file path on disk.

## Prerequisites

- A **Google Cloud project** with the [Android Management API](https://developers.google.com/android/management) enabled.
- A **service account** with appropriate permissions and a downloaded JSON key file.
- An **enterprise** already created via the Android Management API (you will need the enterprise resource name, e.g. `enterprises/LC00t1kz5a`).

## Installation

### Using HACS

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

### Manually (not recommended)

- Download the [latest release](https://github.com/Shaffer-Softworks/Android-Management/releases) as a **zip file** then extract it and move the `android_management_api` folder into the `custom_components` folder in your Home Assistant installation.
- Restart Home Assistant to load the integration.

**Dependencies**: This integration requires `google-api-python-client==2.159.0`, `google-auth==2.37.0`, and `qrcode==8.0`. When installing via HACS, packages are installed automatically. For manual installation, ensure your Home Assistant environment has these packages available.

## Configuration

1. In Home Assistant navigate to `Configuration` -> `Devices & Services` -> `Integrations`.
1. Click the `+ Add Integration` button.
1. Search for `Android Management API`.
1. If you cannot find `Android Management API` in the list then be sure to clear your browser cache and/or perform a hard-refresh of the page.
1. Enter your **Enterprise Name** (the full resource name, e.g. `enterprises/LC00t1kz5a`).
1. Choose your **authentication method**:
    - **Paste JSON key contents** — paste the full contents of your Google service account JSON key file.
    - **Provide file path on disk** — enter the absolute path to your service account JSON key file on the Home Assistant host.
1. Click `Submit`. The integration will validate your credentials by making a test API call.

## Options Flow (Policy and integration configuration)

After setup, click **Configure** on the integration card to open the options UI. A menu lets you configure **General** and **Enterprise** settings, plus policy categories (Kiosk App, Display, etc.), then push policy changes to the enterprise.

The Options flow **fetches the live policy and enterprise** when opened, so fields reflect what's currently active.

### Categories

| Category | Settings |
|----------|----------|
| **General** | Scan interval (API polling, seconds), default policy ID for enrollment QR code, and optional package names for the Clear app data button (one per line or comma-separated). |
| **Enterprise** | Identity (display name, primary color, logo URL + SHA-256 hash), Notifications (Pub/Sub topic, enabled types), Contact (email, DPO, EU rep), Terms & Conditions, Sign-in (URL, token tag, allow personal usage). |
| **Kiosk App** | Primary kiosk app package, install type, auto-update mode, lock task, permissions, additional force-installed apps (one per line). |
| **Kiosk UI** | Power button, system navigation, device settings access, status bar, system error warnings. |
| **Display** | Screen brightness mode/level (0–255), screen timeout mode/duration. |
| **Security & Privacy** | Developer settings, keyguard, camera, screen capture, location mode, untrusted apps policy, Google Play Protect, app verification. |
| **Network & Connectivity** | Wi-Fi, Bluetooth, Bluetooth config, VPN, tethering, data roaming, mobile networks, cell broadcasts, network reset. |
| **Device Restrictions** | Factory reset, install/uninstall apps, physical media, USB file transfer, volume, microphone, outgoing calls, SMS, add user, modify accounts, user icon, wallpaper, share location, credentials config. |
| **System** | App auto-update policy, system update type, Play Store mode, status bar, auto time, skip first-use hints, max time to lock, stay on while plugged (AC/USB/Wireless), long/short support messages. |
| **Device Reporting** | Control which diagnostic data devices report (via `statusReportingSettings`): software info (Android version, build, kernel, security patch), network info (IMEI, WiFi MAC, operator), memory info, display info. Enabling these populates sensors that may show "Unknown" when disabled. |
| **Apply Policy** | Enter a policy ID and push all configured policy settings to the enterprise. |

## Entities

### Sensors (per device)

| Entity | Description |
|--------|-------------|
| **State** | Device state: `ACTIVE`, `DISABLED`, `DELETED`, `PROVISIONING`, `LOST`. |
| **Management Mode** | `DEVICE_OWNER`, `PROFILE_OWNER`, etc. |
| **Ownership** | `COMPANY_OWNED` or `PERSONALLY_OWNED`. |
| **Policy Name** | The currently applied policy ID. |
| **API Level** | Android API level of the device. |
| **Enrollment Time** | Timestamp of when the device was enrolled. |
| **Total RAM (MB)** | Total device RAM in MB (requires `memoryInfoEnabled` in policy). |
| **Total Internal/External Storage (MB)** | Storage in MB (requires `memoryInfoEnabled` in policy). |
| **Non-Compliance Count** | Number of policy non-compliance issues. |
| **Non-Compliance Details** | Details on policy non-compliance. |
| **Display Count** | Number of displays (requires `displayInfoEnabled` in policy). |
| **Enrollment Token Data** | Last enrollment token data (when applicable). |
| **Device Trust** | Device trust signal / posture (when reported). |

### Buttons (per device)

| Entity | Description |
|--------|-------------|
| **Reboot** | Sends a `REBOOT` command to the device (Android N+ only). |
| **Lock** | Sends a `LOCK` command to the device. |
| **Reset Password** | Sends a `RESET_PASSWORD` command. |
| **Factory Reset** | Wipes the device and removes it from the enterprise. |
| **Unenroll** | Removes the device from enterprise management. |
| **Relinquish Ownership** | Removes work profile and policies from company-owned device for personal use (Android 8+ COPE). |
| **Clear app data** | Clears app data for packages configured in integration options (General → package names). |

### Image (per enterprise)

The **Enrollment QR Code** entity generates a fresh enrollment token (valid for 24 hours) and renders it as a QR code PNG image each time it is accessed.

## Enrolling a device with the QR code

To enroll a new Android device using the QR code:

1. **Open the QR code in Home Assistant** — Go to **Settings** → **Devices & Services**, select your **Android Management API** integration, then open the **Enrollment QR Code** image entity. The QR code is generated (or refreshed) when you open the entity; each token is valid for 24 hours.
2. **Prepare the Android device** — Factory reset the device (or start with a device that has not been set up). During the initial setup wizard, choose the option to **Set up as work device** or **Enroll with QR code** (wording may vary by manufacturer and Android version). If you don't see an enrollment option, **tap the setup screen several times** (e.g. six times on the Welcome screen) to reveal the QR code scanner.
3. **Scan the QR code** — When prompted, scan the QR code displayed in Home Assistant (e.g. on your computer or phone screen). The device will enroll in your enterprise and apply the policy configured for new enrollments.
4. **Verify** — The new device will appear under your integration after the next coordinator poll (about 60 seconds). You can then assign or adjust its policy via the integration or Options flow.

For custom token duration or to get token data programmatically (e.g. for NFC or other provisioning), use the `android_management_api.create_enrollment_token` service and listen for the `android_management_api_enrollment_token_created` event.

## Services

### `android_management_api.set_policy`

Create or update an Android Management policy with raw JSON.

| Field | Required | Description |
|-------|----------|-------------|
| `policy_id` | Yes | The policy ID to create or update (e.g. `policy1`). |
| `policy_body` | No | JSON string representing the full policy body. |

### `android_management_api.set_kiosk_policy`

Create or update a kiosk policy with structured fields. Supports a primary kiosk app plus additional force-installed apps.

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `policy_id` | Yes | — | The policy ID to create or update. |
| `package_name` | Yes | — | Primary kiosk app package name. |
| `additional_packages` | No | — | Comma or newline-separated list of additional app package names (force-installed). |
| `install_type` | No | `KIOSK` | Install type for the primary app. |
| `auto_update_mode` | No | `AUTO_UPDATE_HIGH_PRIORITY` | Auto-update behavior for the primary app. |
| `lock_task_allowed` | No | `true` | Whether the primary app can lock the device to kiosk mode. |
| `default_permission_policy` | No | `GRANT` | Runtime permission policy for the primary app. |
| `power_button_actions` | No | `POWER_BUTTON_BLOCKED` | Power button behavior in kiosk mode. |
| `system_navigation` | No | `NAVIGATION_DISABLED` | Navigation bar behavior in kiosk mode. |
| `device_settings` | No | `SETTINGS_ACCESS_BLOCKED` | Device settings access in kiosk mode. |
| `status_bar` | No | `NOTIFICATIONS_AND_SYSTEM_INFO_DISABLED` | Status bar behavior in kiosk mode. |
| `screen_brightness_mode` | No | `BRIGHTNESS_FIXED` | Brightness control mode. |
| `screen_brightness` | No | `180` | Brightness level (0–255). |
| `screen_timeout_mode` | No | `SCREEN_TIMEOUT_ENFORCED` | Screen timeout control mode. |
| `screen_timeout` | No | `220s` | Screen timeout duration. |
| `developer_settings` | No | `DEVELOPER_SETTINGS_ALLOWED` | Developer options access. |
| `app_auto_update_policy` | No | `ALWAYS` | Global app auto-update policy. |
| `keyguard_disabled` | No | `true` | Disable lock screen. |
| `status_bar_disabled` | No | `true` | Disable status bar globally. |

### `android_management_api.create_enrollment_token`

Create a new enrollment token for device provisioning. Fires an `android_management_api_enrollment_token_created` event with the token data.

| Field | Required | Description |
|-------|----------|-------------|
| `enterprise_name` | Yes* | Full enterprise resource name (e.g. `enterprises/LC00t1kz5a`). *Required when calling from service; optional when triggered by integration. |
| `policy_id` | No | Policy ID to bind to the token (e.g. `policy1`). |
| `policy_name` | No | Full policy resource name (alternative to `policy_id`). |
| `duration` | No | Token validity duration (default `86400s` = 24 hours). |
| `one_time_only` | No | If true, token can only be used once. |
| `additional_data` | No | Optional string passed to the device during provisioning. |
| `allow_personal_usage` | No | `ALLOW_PERSONAL_USAGE_UNSPECIFIED`, `PERSONAL_USAGE_ALLOWED`, or `PERSONAL_USAGE_DISALLOWED`. |

### `android_management_api.clear_app_data`

Clear app data for specified packages on a device. (Android 9+)

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name (e.g. `enterprises/XXX/devices/YYY`). |
| `package_names` | Yes | List of app package names (e.g. `com.example.app`). Comma or newline-separated. |

### `android_management_api.start_lost_mode`

Put a device into lost mode. At least one of the message fields is required. (Fully managed or COPE devices)

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |
| `lost_message` | No | Message displayed on lock screen. |
| `lost_phone_number` | No | Phone number for call owner button. |
| `lost_email` | No | Email displayed on lock screen. |
| `lost_street_address` | No | Street address displayed. |
| `lost_organization` | No | Organization name displayed. |

### `android_management_api.stop_lost_mode`

Take a device out of lost mode.

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |

### `android_management_api.patch_device`

Update device state, policy, or disabled reason.

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |
| `state` | No | Set to `ACTIVE` or `DISABLED`. |
| `policy_id` | No | Policy ID to apply (e.g. `policy1`). |
| `disabled_reason` | No | Message shown when device is disabled. |

### `android_management_api.wipe`

Wipe a device via command (alternative to Factory Reset button).

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |
| `wipe_reason` | No | User-facing reason for wipe. |
| `wipe_data_flags` | No | Comma-separated flags (e.g. `WIPE_EXTERNAL_STORAGE`). |

### `android_management_api.add_esim`

Add an eSIM profile to a device. (Android 15+)

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |
| `activation_code` | Yes | eSIM activation code. |
| `activation_state` | No | `ACTIVATED`, `NOT_ACTIVATED`, or `ACTIVATION_STATE_UNSPECIFIED`. Default: `ACTIVATED`. |

### `android_management_api.remove_esim`

Remove an eSIM profile from a device. (Android 15+)

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |
| `icc_id` | Yes | ICC ID of the eSIM profile to remove. |

### `android_management_api.request_device_info`

Request device information (e.g. EID for eSIM). User must approve on device.

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |
| `device_info_type` | No | `EID` or `DEVICE_INFO_UNSPECIFIED`. Default: `EID`. |

### `android_management_api.issue_command`

Send a raw command to a device.

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |
| `command_type` | Yes | Command type (e.g. `REBOOT`, `LOCK`, `CLEAR_APP_DATA`). |
| `command_params` | No | Additional params as dict or JSON string (camelCase keys). |

### `android_management_api.reset_password`

Reset device password with optional new password and flags.

| Field | Required | Description |
|-------|----------|-------------|
| `device_id` | Yes | Device ID or full resource name. |
| `new_password` | No | New password (min 6 chars if numeric on Android 14). |
| `reset_password_flags` | No | Comma-separated: `REQUIRE_ENTRY`, `DO_NOT_ASK_CREDENTIALS_ON_BOOT`, `LOCK_NOW`. |

### Enterprise and policy listing

| Service | Description |
|---------|-------------|
| `android_management_api.list_policies` | List policies for the enterprise (requires `enterprise_name`). |
| `android_management_api.list_enrollment_tokens` | List enrollment tokens (requires `enterprise_name`). |
| `android_management_api.delete_enrollment_token` | Delete an enrollment token by name. |
| `android_management_api.get_operation` | Get status of a long-running operation by name. |
| `android_management_api.get_enterprise` | Get enterprise resource (display name, logo, contact, etc.). |
| `android_management_api.patch_enterprise` | Update enterprise (body + update mask). |
| `android_management_api.create_web_token` | Create a web token for managed Google Play iframe (parent frame URL, permissions). |

## Debug Logging

To enable debug logging for the integration, add the following to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.android_management_api: debug
```
