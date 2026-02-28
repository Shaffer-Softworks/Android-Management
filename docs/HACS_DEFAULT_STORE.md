# Publishing to the HACS Default Store

So users can install your integration from HACS **without** adding a custom repository, you need to get the repo included in the [default HACS repositories](https://github.com/hacs/default). Follow these steps.

## Prerequisites (your repo already has)

- [x] **hacs.json** in repo root with at least `name` (you have this)
- [x] **GitHub Actions**: `hassfest` and `hacs/action` in `.github/workflows/validate.yaml` (you have both)
- [x] **manifest.json** with required keys (you have this)

## Steps to get into the default store

### 1. Brand images (in-repo only)

**Home Assistant no longer accepts PRs** for new custom integrations in [home-assistant/brands](https://github.com/home-assistant/brands). Custom integrations must ship their own brand images in-repo (HA 2026+).

This repo already does that: **`custom_components/android_management_api/brand/`** contains `icon.png`, `icon@2x.png`, `logo.png`, `logo@2x.png`, and dark variants. Home Assistant 2026.3+ will use these at runtime (Settings → Integrations, etc.).

For **HACS default store**, the hacs/default "Check brands" used to require the integration to be in `home-assistant/brands`. Since that’s no longer possible, **keep `ignore: brands`** in your HACS action (see step 2). Submit your PR to hacs/default as-is; maintainers may have updated their checks or accept integrations that ship in-repo brands. Check the [HACS publish docs](https://hacs.xyz/docs/publish/include/) and [hacs/action](https://github.com/hacs/action) for any updated policy.

### 2. Keep HACS validation passing (keep `ignore: brands`)

Leave the **`ignore: brands`** line in **`.github/workflows/validate.yaml`** for the HACS job. With home-assistant/brands closed to new custom integrations, you cannot satisfy the brands check there; the ignore is required for the action to pass. Do not remove it before submitting to hacs/default.

### 3. Repository settings on GitHub

On your repo **Settings** and **About**:

- **Description**: Set a short description (shows in HACS).
- **Topics**: Add e.g. `home-assistant`, `hacs`, `android-management`, `custom-component`.
- **Issues**: Ensure **Issues** are enabled.

### 4. Create a full GitHub Release

HACS default requires at least one **release** (not only a tag).

- Repo → **Releases** → **Create a new release**.
- Choose a tag (e.g. `v0.1.5` to match `manifest.json`) or create one.
- Add release title and notes, then publish.

### 5. Submit to hacs/default

- Fork [hacs/default](https://github.com/hacs/default).
- Create a **new branch from `master`** (do not push to `master`).
- Edit the file **`integration`** (JSON array of `"owner/repo"` strings).
- Add **`"Shaffer-Softworks/Android-Management"`** in **alphabetical order** (e.g. after `"Sha-Darim/brandriskute"`, before `"Sheep26/huawei_hg659"`).
- Run lint/sort if the repo uses it (e.g. `jq` lint and sorted order).
- Open a **Pull Request** to `hacs/default`, fill out the PR template, and submit.

Rules:

- Only the repo **owner** or a **major contributor** may submit.
- Submit from a **personal account** (PR must be editable; avoid org-owned PRs if that blocks edit).
- Do not submit custom integrations that alpha/beta test or override core integrations.

Official steps: [Include default repositories](https://hacs.xyz/docs/publish/include/).

### 6. After your PR is merged

- Your repo will be included in the next HACS scheduled scan.
- Users will see **Android Management API** in HACS under Integrations without adding a custom repo.

---

**Note:** New default additions can take months to be reviewed. You can track progress in the [hacs/default backlog](https://github.com/hacs/default/pulls?q=is%3Apr+is%3Aopen+draft%3Afalse+sort%3Acreated-asc).
