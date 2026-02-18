# Android Management API custom component for Home Assistant

![android-logo](https://github.com/Shaffer-Softworks/Android-Management/blob/main/icon.png)


Manage your Android enterprise devices directly from Home Assistant using [Google's Android Management API](https://developers.google.com/android/management).

**This component will set up the following platforms.**

| Platform | Description |
|----------|-------------|
| `sensor` | Per-device diagnostic sensors: State, Management Mode, Ownership, Policy Name, API Level, Enrollment Time. |
| `button` | Per-device command buttons: Reboot, Lock, Reset Password, Factory Reset, Unenroll. |
| `device_tracker` | Per-device online/offline tracker based on device state. |
| `image` | Enterprise-level enrollment QR code generated on demand. |

### Key Features

- **Full Device Inventory**: All managed devices are automatically discovered and represented as Home Assistant devices with manufacturer, model, and serial number.
- **Device Commands**: Reboot, lock, reset password, factory reset (wipe), and unenroll devices with a single button press.
- **Online/Offline Tracking**: Device tracker entities map `ACTIVE` devices to online and all other states to offline.
- **Enrollment QR Code**: Generate a fresh 24-hour enrollment token and render it as a QR code image — ready to scan on a new device.
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

## Options Flow (Policy Configuration)

After setup, click **Configure** on the integration card to open the policy management UI. A menu lets you configure settings across 8 categories, then push them to the enterprise in one step.

The Options flow **fetches the live policy** from the enterprise when opened, so all fields reflect what's currently active on your devices.

### Categories

| Category | Settings |
|----------|----------|
| **Kiosk App** | Primary kiosk app package, install type, auto-update mode, lock task, permissions, additional force-installed apps (one per line). |
| **Kiosk UI** | Power button, system navigation, device settings access, status bar, system error warnings. |
| **Display** | Screen brightness mode/level (0–255), screen timeout mode/duration. |
| **Security & Privacy** | Developer settings, keyguard, camera, screen capture, location mode, untrusted apps policy, Google Play Protect, app verification. |
| **Network & Connectivity** | Wi-Fi, Bluetooth, Bluetooth config, VPN, tethering, data roaming, mobile networks, cell broadcasts, network reset. |
| **Device Restrictions** | Factory reset, install/uninstall apps, physical media, USB file transfer, volume, microphone, outgoing calls, SMS, add user, modify accounts, user icon, wallpaper, share location, credentials config. |
| **System** | App auto-update policy, system update type, Play Store mode, status bar, auto time, skip first-use hints, max time to lock, stay on while plugged (AC/USB/Wireless), long/short support messages. |
| **Apply Policy** | Enter a policy ID and push all configured settings to the enterprise. |

## Entities

### Sensors (per device)

| Entity | Description |
|--------|-------------|
| **State** | Device state: `ACTIVE`, `DISABLED`, `DELETED`, `PROVISIONING`. |
| **Management Mode** | `DEVICE_OWNER`, `PROFILE_OWNER`, etc. |
| **Ownership** | `COMPANY_OWNED` or `PERSONALLY_OWNED`. |
| **Policy Name** | The currently applied policy ID. |
| **API Level** | Android API level of the device. |
| **Enrollment Time** | Timestamp of when the device was enrolled. |

### Buttons (per device)

| Entity | Description |
|--------|-------------|
| **Reboot** | Sends a `REBOOT` command to the device (Android N+ only). |
| **Lock** | Sends a `LOCK` command to the device. |
| **Reset Password** | Sends a `RESET_PASSWORD` command. |
| **Factory Reset** | Wipes the device and removes it from the enterprise. |
| **Unenroll** | Removes the device from enterprise management. |

### Device Tracker (per device)

Maps the device `state` field — `ACTIVE` is reported as `home` (online), all other states as `not_home` (offline).

### Image (per enterprise)

The **Enrollment QR Code** entity generates a fresh enrollment token (valid for 24 hours) and renders it as a QR code PNG image each time it is accessed.

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
| `policy_name` | No | Full policy resource name to bind to the token. |
| `duration` | No | Token validity duration (default `86400s` = 24 hours). |

## Debug Logging

To enable debug logging for the integration, add the following to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.android_management_api: debug
```
