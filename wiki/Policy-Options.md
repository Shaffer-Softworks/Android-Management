# Policy Options

The integration’s **Options** flow provides a menu-driven UI to configure kiosk and device policies and push them to your enterprise. It **fetches the live policy** from the enterprise when you open it, so the form reflects what’s currently set.

---

## Opening the Options flow

1. Go to **Settings** → **Devices & Services** → **Integrations**.
2. Find **Android Management API** and click **Configure** on its card.

You’ll see a menu with several categories. Configure the ones you need, then use **Apply Policy** to send everything to the enterprise.

---

## Categories

| Category | What you can configure |
|----------|-------------------------|
| **Kiosk App** | Primary kiosk app package name, install type, auto-update mode, lock task allowed, default permission policy, and additional force-installed apps (one per line). |
| **Kiosk UI** | Power button behavior, system navigation, device settings access, status bar, and system error warnings. |
| **Display** | Screen brightness mode and level (0–255), screen timeout mode and duration. |
| **Security & Privacy** | Developer settings, keyguard, camera, screen capture, location mode, untrusted apps, Google Play Protect, app verification. |
| **Network & Connectivity** | Wi-Fi, Bluetooth, Bluetooth config, VPN, tethering, data roaming, mobile networks, cell broadcasts, network reset. |
| **Device Restrictions** | Factory reset, install/uninstall apps, physical media, USB file transfer, volume, microphone, outgoing calls, SMS, add user, modify accounts, user icon, wallpaper, share location, credentials config. |
| **System** | App auto-update policy, system update type, Play Store mode, status bar, auto time, skip first-use hints, max time to lock, stay on while plugged (AC/USB/Wireless), long/short support messages. |
| **Apply Policy** | Enter the **policy ID** (e.g. `policy1`) and push all configured settings to the enterprise in one step. |

---

## Policy ID

- The **policy ID** is the name of the policy in your enterprise (e.g. `policy1`, `kiosk-policy`).
- You can create a new policy by entering an ID that doesn’t exist yet; the API will create it. To change an existing policy, use its current ID.
- The Options flow does **not** create the enterprise; it only creates or updates a **policy** under the enterprise you configured in the integration.

---

## Using policies on devices

- After applying a policy, assign it to devices (or enrollment tokens) via the [Android Management console](https://support.google.com/work/android/answer/6174145) or the API.
- The integration’s **Enrollment QR Code** and `create_enrollment_token` service can bind a policy to new enrollment tokens so newly provisioned devices get that policy.

---

## Services vs Options flow

- **Options flow** – Best for interactive, form-based editing; all categories are available and the UI is pre-filled from the live policy.
- **Services** – Use from automations, scripts, or Developer Tools:
  - `android_management_api.set_policy` – Raw JSON policy body.
  - `android_management_api.set_kiosk_policy` – Structured kiosk fields (primary app, additional apps, display, security, etc.).

See the [README – Services](../README.md#services) for the full list of service parameters.
