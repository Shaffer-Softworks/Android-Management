<!-- {% if not installed %} -->

## Installation

1. Add <https://github.com/Shaffer-Softworks/Android-Management> to your [HACS](https://hacs.xyz/) custom repositories.
1. Choose `Integration` from the category selection.
1. Click install.
1. Return to the Integrations page within HACS then click the `+ Explore & download repositories` button.
1. Search for `Android Management API`, select it, then click `Download this repository with HACS`.
1. Restart Home Assistant to load the integration.

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

## Entities Created

**Per managed device:**
- **Sensors** — State, Management Mode, Ownership, Policy Name, API Level, Enrollment Time
- **Buttons** — Reboot, Lock, Reset Password, Factory Reset, Unenroll
- **Device Tracker** — Online (`home`) / Offline (`not_home`) based on device state

**Per enterprise:**
- **Image** — Enrollment QR Code (generates a fresh 24-hour enrollment token on demand)

## Services

- `android_management_api.set_policy` — Create or update a policy by ID with an optional JSON body.
- `android_management_api.create_enrollment_token` — Create an enrollment token (fires a `android_management_api_enrollment_token_created` event with the token data).

<!-- {% endif %} -->

<!-- {% if installed %} -->
# Integration v0.1.0

**Initial Release:**
- Full integration with Google's [Android Management API](https://developers.google.com/android/management)
- Two-step config flow with service account authentication (paste JSON or provide file path)
- **DataUpdateCoordinator** polling device list every 60 seconds
- Per-device **sensor** entities: State, Management Mode, Ownership, Policy Name, API Level, Enrollment Time
- Per-device **button** entities: Reboot, Lock, Reset Password, Factory Reset (wipe), Unenroll
- Per-device **device tracker**: maps `ACTIVE` state to online, all others to offline
- Enterprise-level **enrollment QR code** image entity (generates a 24-hour token on demand)
- HA **services**: `set_policy` and `create_enrollment_token`
<!-- {% endif %} -->
