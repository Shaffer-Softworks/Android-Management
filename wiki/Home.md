# Android Management API – Wiki

This wiki covers setup, configuration, and troubleshooting for the **Android Management API** Home Assistant integration. The integration lets you manage Android enterprise devices from Home Assistant using [Google's Android Management API](https://developers.google.com/android/management).

---

## Quick links

| Topic | Description |
|--------|-------------|
| [Initial Setup](#initial-setup) | Google Cloud project, API, service account, and enterprise |
| [Post-setup Advice](#post-setup-advice) | Best practices after the integration is configured |
| [Debug Logging](#debug-logging) | Enable and use debug logs for troubleshooting |
| [Configuration](Configuration) | Adding and configuring the integration in Home Assistant |
| [Policy options](Policy-Options) | Options flow and kiosk policy categories |

---

## Initial setup

Before adding the integration in Home Assistant, you need:

1. **A Google Cloud project** with the Android Management API enabled.
2. **A service account** with the right permissions and a downloaded JSON key.
3. **An enterprise** created in Android Management (you’ll use its resource name, e.g. `enterprises/LC00t1kz5a`).

For step-by-step instructions, see **[Initial Setup](Initial-Setup)**.

---

## Post-setup advice

After the integration is set up:

- **Policy ID**: Create or choose a policy in the [Android Management API console](https://support.google.com/work/android/answer/6174145) and use its ID in the integration’s Options flow when applying settings.
- **Enrollment QR code**: The enrollment QR image entity creates a new 24-hour token each time it’s refreshed; use it for provisioning new devices.
- **Device list**: The integration polls the API about every 60 seconds; new or removed devices appear after the next update.
- **Services**: Use `set_policy`, `set_kiosk_policy`, and `create_enrollment_token` from Developer Tools → Services or from automations.

More detail: **[Post-setup Advice](Post-Setup-Advice)**.

---

## Debug logging

To see detailed logs for this integration, add the following to your `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.android_management_api: debug
```

Restart Home Assistant, reproduce the issue, then check **Settings → System → Logs** or the log file. See **[Debug Logging](Debug-Logging)** for more.

---

## See also

- [Main README](../README.md) – Installation (HACS/manual), entities, services reference
- [Android Management API (Google)](https://developers.google.com/android/management) – Official API docs
