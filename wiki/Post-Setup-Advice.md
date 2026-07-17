# Post-setup Advice

Tips and best practices after the Android Management API integration is configured in Home Assistant.

---

## Policy ID

- Policies are created and managed in the [Android Management API](https://developers.google.com/android/management) (or the [Android Management console](https://support.google.com/work/android/answer/6174145)).
- In the integration’s **Options** flow, the **Apply Policy** step requires a **policy ID** (e.g. `policy1`). Create this policy in the console first, or create/update it via `android_management_api.set_policy`, `set_kiosk_policy`, or `modify_policy_applications`, then use that same ID when applying from the Options flow.
- The Options flow **fetches the live policy** from the enterprise when you open it, so the form reflects what’s currently applied.

---

## Enrolling a device with the QR code

To enroll a new Android device using the QR code:

1. **Open the QR code in Home Assistant** — Go to **Settings** → **Devices & Services**, select your **Android Management API** integration, then open the **Enrollment QR Code** image entity. The QR code is generated (or refreshed) when you open the entity; each token is valid for 24 hours.
2. **Prepare the Android device** — Factory reset the device (or start with a device that has not been set up). During the initial setup wizard, choose the option to **Set up as work device** or **Enroll with QR code** (wording may vary by manufacturer and Android version). If you don’t see an enrollment option, **tap the setup screen several times** (e.g. six times on the Welcome screen) to reveal the QR code scanner.
3. **Scan the QR code** — When prompted, scan the QR code displayed in Home Assistant (e.g. on your computer or phone screen). The device will enroll in your enterprise and apply the policy configured for new enrollments.
4. **Verify** — The new device will appear under your integration after the next coordinator poll (about 60 seconds). You can then assign or adjust its policy via the integration or Options flow.

For custom token duration or to get token data programmatically (e.g. for NFC or other provisioning), use the `android_management_api.create_enrollment_token` service and listen for the `android_management_api_enrollment_token_created` event.

---

## Device list and polling

- The integration uses a **DataUpdateCoordinator** that polls the Android Management API. The **scan interval** (default 60 seconds) can be changed in **Configure** → **General**.
- Newly enrolled devices appear after the next poll; removed or wiped devices disappear after the next update.
- If a device doesn’t show up, confirm it’s enrolled in the same enterprise and that the service account has access to that enterprise.

---

## Using services

- **Developer Tools → Services**: Call `android_management_api.set_policy`, `set_kiosk_policy`, `modify_policy_applications`, `remove_policy_applications`, `create_enrollment_token`, `refresh`, and device-level services (`clear_app_data`, `start_lost_mode`, `stop_lost_mode`, `patch_device`, `wipe`, `add_esim`, `remove_esim`, `request_device_info`, `issue_command`, `reset_password`) with the parameters documented in the [README](../README.md#services).
- **Automations and scripts**: Use the same service names and parameters to manage policies, tokens, and devices from automations or scripts.
- **Events**: After `create_enrollment_token`, listen for `android_management_api_enrollment_token_created`. After modify/remove policy applications, listen for `android_management_api_policy_applications_modified` / `android_management_api_policy_applications_removed`.

---

## Buttons and device state

- Per-device **buttons** send commands through the API. The device must be **ACTIVE** (or in a state that accepts the command) for the action to apply.
- **Factory Reset** deletes the device (with external storage wipe flags). **Wipe** issues the `WIPE` command (device acknowledges before reset / work-profile removal).
- **Start Lost Mode** uses a default message; use the `start_lost_mode` service for phone/email/address fields.
- **Request Device Info** requests EID; personally owned work profiles may require user approval.
- **Clear app data** uses the package names configured in **Configure** → **General**.

---

## Authentication

- **Paste JSON**: The full contents of the service account JSON key are stored in the integration config. Prefer this if you don’t have filesystem access on the Home Assistant host.
- **File path**: If you use a path to the JSON file, ensure the path is correct on the **Home Assistant host** (e.g. in a mounted volume or add-on path). Restart may be required after changing the file.

If you run into errors, enable [Debug Logging](Debug-Logging) and check the logs.
