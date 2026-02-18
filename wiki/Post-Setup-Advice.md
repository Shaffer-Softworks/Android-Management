# Post-setup Advice

Tips and best practices after the Android Management API integration is configured in Home Assistant.

---

## Policy ID

- Policies are created and managed in the [Android Management API](https://developers.google.com/android/management) (or the [Android Management console](https://support.google.com/work/android/answer/6174145)).
- In the integration’s **Options** flow, the **Apply Policy** step requires a **policy ID** (e.g. `policy1`). Create this policy in the console first, or create/update it via the `android_management_api.set_policy` or `set_kiosk_policy` service, then use that same ID when applying from the Options flow.
- The Options flow **fetches the live policy** from the enterprise when you open it, so the form reflects what’s currently applied.

---

## Enrollment QR code

- The **Enrollment QR Code** image entity generates a **new 24-hour enrollment token** each time the image is refreshed (e.g. when you open the entity in the frontend).
- Use this to provision new devices: open the entity, show the QR code on a screen, and scan it with the device.
- For longer-lived or custom tokens, use the `android_management_api.create_enrollment_token` service; the integration fires an event with the token data.

---

## Device list and polling

- The integration uses a **DataUpdateCoordinator** that polls the Android Management API about **every 60 seconds**.
- Newly enrolled devices appear after the next poll; removed or wiped devices disappear after the next update.
- If a device doesn’t show up, confirm it’s enrolled in the same enterprise and that the service account has access to that enterprise.

---

## Using services

- **Developer Tools → Services**: Call `android_management_api.set_policy`, `android_management_api.set_kiosk_policy`, and `android_management_api.create_enrollment_token` with the parameters documented in the [README](../README.md#services).
- **Automations and scripts**: Use the same service names and parameters to manage policies and tokens from automations or scripts.
- **Events**: After `create_enrollment_token`, listen for `android_management_api_enrollment_token_created` to get the token payload.

---

## Buttons and device state

- Per-device **buttons** (Reboot, Lock, Reset Password, Factory Reset, Unenroll) send commands through the API. The device must be **ACTIVE** (or in a state that accepts the command) for the action to apply.
- **Device tracker** entities map `ACTIVE` to `home` (online) and other states to `not_home` (offline).

---

## Authentication

- **Paste JSON**: The full contents of the service account JSON key are stored in the integration config. Prefer this if you don’t have filesystem access on the Home Assistant host.
- **File path**: If you use a path to the JSON file, ensure the path is correct on the **Home Assistant host** (e.g. in a mounted volume or add-on path). Restart may be required after changing the file.

If you run into errors, enable [Debug Logging](Debug-Logging) and check the logs.
