# Release notes

Use the section below when creating a new [GitHub Release](https://github.com/Shaffer-Softworks/Android-Management/releases). Copy the block for the version you are releasing.

---

## v1.0.0 (2026-07-17)

First major release: Android Management API 2025–H1 2026 surface — new policy Options fields, policy-application services, buttons/sensors, and client library bumps.

### Changes

- **Dependencies**: `google-api-python-client==2.198.0`, `google-auth==2.56.0`.
- **Policy Options**: Application roles, `CUSTOM` install + signing cert, autofill, enterprise display name visibility, app functions, private space, wipe data flags, private DNS, Bluetooth sharing, user-initiated eSIM add, application/default-app reporting, optional JSON for APN / preferential network / Wi-Fi roaming / default apps.
- **Services**: `modify_policy_applications`, `remove_policy_applications`; `set_kiosk_policy` gains optional `application_roles` and `signing_key_cert_sha256`.
- **Buttons**: Wipe (`WIPE`), Start/Stop Lost Mode, Request Device Info (EID). Factory Reset remains `devices.delete`.
- **Sensors**: EID, Telephony Info, Application Report Count, Signing Cert SHA-256, Default Application Info.
- **Fix**: `request_device_info` sends `deviceInfo` as the API enum string.

See the [README](https://github.com/Shaffer-Softworks/Android-Management#readme) and [Wiki](https://github.com/Shaffer-Softworks/Android-Management/wiki) for setup and configuration.

---

## v0.1.5 (2026-02-27)

Update focusing on General/Enterprise options, new services, Clear app data button, and removal of the device tracker.

### Changes

- **General options**: Configure scan interval (API polling), default policy for enrollment QR code, and package names for the Clear app data button.
- **Enterprise options**: Configure identity (display name, primary color, logo), notifications, contact info, terms & conditions, and sign-in details from the integration UI.
- **New sensors**: Enrollment Token Data, Device Trust.
- **Clear app data button**: Per-device button using packages from General options.
- **Enrollment token**: Supports `policy_id`, `one_time_only`, `additional_data`, `allow_personal_usage`.
- **New services**: `list_policies`, `list_enrollment_tokens`, `delete_enrollment_token`, `get_operation`, `get_enterprise`, `patch_enterprise`, `create_web_token`.
- **Device tracker removed**: The Android Management API does not provide device location. The device tracker platform has been removed; any existing device_tracker entities are removed from the entity registry when the integration is reloaded.

See the [README](https://github.com/Shaffer-Softworks/Android-Management#readme) and [Wiki](https://github.com/Shaffer-Softworks/Android-Management/wiki) for setup and configuration.

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
