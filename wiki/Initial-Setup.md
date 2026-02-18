# Initial Setup

This page walks through the prerequisites for the Android Management API integration: Google Cloud project, Android Management API, service account, and enterprise.

---

## 1. Google Cloud project

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Note the project ID; you’ll use it when creating the enterprise and service account.

---

## 2. Enable Android Management API

1. In Cloud Console, go to **APIs & Services** → **Library**.
2. Search for **Android Management API**.
3. Open it and click **Enable** for your project.

---

## 3. Create a service account

1. Go to **APIs & Services** → **Credentials**.
2. Click **Create Credentials** → **Service account**.
3. Give it a name (e.g. `ha-android-management`) and optionally a description.
4. Click **Create and Continue**. You can skip optional steps (roles, access) unless you need them for other GCP resources.
5. Open the new service account → **Keys**.
6. Click **Add key** → **Create new key** → **JSON**, then download the key file.  
   Keep this file secure; it is the credential the integration will use.

---

## 4. Service account permissions (Android Management API)

The Android Management API uses the same identity for both API access and “signup” (enterprise creation). The service account does **not** need special IAM roles in Google Cloud for normal API use; access is controlled by the enterprises and policies you create.

To **create an enterprise** (first-time setup only):

- Use either:
  - A **user account** (not the service account) that has completed the [Android Management API signup flow](https://developers.google.com/android/management/provision-device#sign_up_for_the_api), or
  - The **same service account** after it has been used to sign up for the API (e.g. by creating an enterprise once via the API or the console).

After at least one enterprise exists, the service account only needs to be allowed to access that enterprise (see Android Management / Admin console, not GCP IAM).

---

## 5. Create an enterprise

You need at least one **enterprise** in Android Management. Its resource name (e.g. `enterprises/LC00t1kz5a`) is what you enter in the integration as **Enterprise Name**.

**Option A – Using Google’s Admin console**

1. Go to [Android Management API – Sign up](https://developers.google.com/android/management/signup) and complete signup with your Google account (or the one that will own the enterprise).
2. Use the [Android Management console](https://support.google.com/work/android/answer/6174145) to create and manage enterprises and policies.  
   The enterprise resource name is shown in the console (e.g. in URL or settings). It looks like `enterprises/LC00t1kz5a`.

**Option B – Using the API**

- If you use the API or a script to create enterprises, use the same project and ensure the identity (user or service account) has completed signup and has permission to create enterprises.

Once you have the enterprise name (e.g. `enterprises/LC00t1kz5a`), you can add the integration in Home Assistant and paste or point to the service account JSON key.

---

## 6. Allow the service account to manage the enterprise

- In the [Android Management console](https://support.google.com/work/android/answer/6174145), ensure the service account’s email (e.g. `ha-android-management@your-project.iam.gserviceaccount.com`) is allowed to manage the enterprise, if your setup requires explicit access control.
- If you created the enterprise with the same Google account that owns the project, the project’s service account is often already able to manage that enterprise; if you see permission errors, add the service account in the Android Management / Admin console.

---

## Summary checklist

- [ ] Google Cloud project created or selected  
- [ ] Android Management API enabled for that project  
- [ ] Service account created and JSON key downloaded  
- [ ] At least one enterprise created; enterprise name (e.g. `enterprises/LC00t1kz5a`) known  
- [ ] Service account has access to that enterprise (if required by your setup)  

Next: add the integration in Home Assistant and enter the **Enterprise Name** and service account credentials. See [Configuration](Configuration).
