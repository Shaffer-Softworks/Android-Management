# Configuration

How to add and configure the Android Management API integration in Home Assistant.

---

## Add the integration

1. Go to **Settings** (or **Configuration**) → **Devices & Services** → **Integrations**.
2. Click **+ Add Integration**.
3. Search for **Android Management API**.
4. If it doesn’t appear, clear your browser cache or do a hard refresh (e.g. Ctrl+F5 / Cmd+Shift+R), then search again.
5. Select **Android Management API**.

---

## Enter details

1. **Enterprise Name**  
   Enter the full enterprise resource name (e.g. `enterprises/LC00t1kz5a`). You get this from the [Android Management console](https://support.google.com/work/android/answer/6174145) or when you create the enterprise. Do not omit the `enterprises/` prefix.

2. **Authentication method**  
   Choose one:
   - **Paste JSON key contents** – Paste the entire contents of your Google service account JSON key file into the text area.
   - **Provide file path on disk** – Enter the **absolute** path to the JSON key file on the machine running Home Assistant (e.g. `/config/google-service-account.json`).

3. Click **Submit**.  
   The integration will validate the credentials with a test API call. If something is wrong (e.g. invalid JSON, wrong enterprise name, or missing API access), you’ll see an error message.

---

## After setup

- **Configure (Options)** – On the integration card, click **Configure** to open the policy management UI. See [Policy Options](Policy-Options).
- **Entities** – Per-device sensors (state, policy, software/network info, memory, non-compliance), buttons (Reboot, Lock, Reset Password, Factory Reset, Unenroll, Relinquish Ownership), device tracker, and enterprise-level enrollment QR image entity. They appear under the integration device(s) and under **Settings → Devices & Services → Entities**.

---

## Multiple enterprises

To manage more than one enterprise, add the integration again and use a different **Enterprise Name** (and optionally a different service account or key) for each.

---

## Changing credentials or enterprise

- Edit the integration: go to **Devices & Services** → **Integrations**, find **Android Management API**, click the three dots → **Configure**, and update **Enterprise Name** or authentication (JSON/path) as needed.
- If you switch from “paste JSON” to “file path” (or the other way around), ensure the new option is filled in correctly and submit. You may need to restart Home Assistant if the integration caches the previous config.

For prerequisites (Google Cloud, API, service account, enterprise), see [Initial Setup](Initial-Setup).
