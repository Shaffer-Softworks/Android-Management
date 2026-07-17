# Debug Logging

Enabling debug logging helps troubleshoot issues with the Android Management API integration.

---

## Enable debug logs

Add the following to your Home Assistant `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.android_management_api: debug
```

Then:

1. Save the file.
2. Restart Home Assistant (or reload the **Logger** integration under **Settings → System → Control** if you use the UI).
3. Reproduce the issue (e.g. add the integration, press a button, refresh the enrollment QR code).
4. Check the logs.

---

## Where to view logs

- **Settings → System → Logs** in the Home Assistant UI.
- Or the log file on the host (e.g. `/config/home-assistant.log` or the path used by your installation).

---

## What appears in debug

With `custom_components.android_management_api` set to `debug`, the integration will log:

- API requests and responses (including errors)
- Config and options flow steps
- Coordinator updates and device list changes
- Service calls (e.g. `set_policy`, `set_kiosk_policy`, `modify_policy_applications`, `remove_policy_applications`, `create_enrollment_token`, `refresh`, device-level services like `clear_app_data`, `start_lost_mode`, `wipe`, `patch_device`, etc.)
- Authentication and validation steps

Use this to verify credentials, policy IDs, enterprise names, and any error messages returned by the Android Management API.

---

## Turn off debug when done

To reduce log volume after troubleshooting:

1. Remove the `custom_components.android_management_api: debug` line from `configuration.yaml`, or change `debug` to `info` or `warning`.
2. Restart Home Assistant or reload the Logger integration.
