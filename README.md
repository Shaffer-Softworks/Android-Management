# Android Management API custom component for Home Assistant

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
- **Policy Management**: Use the `set_policy` service to create or update Android Management policies from automations or scripts.
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

Create or update an Android Management policy.

| Field | Required | Description |
|-------|----------|-------------|
| `policy_id` | Yes | The policy ID to create or update (e.g. `policy1`). |
| `policy_body` | No | JSON string representing the full policy body. |

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
