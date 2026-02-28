# Submit PR to HACS default (add this repo to the store)

You need to open **one PR** on [hacs/default](https://github.com/hacs/default) to add this repo to the default integration list. Steps below.

## 1. Fork and clone

1. Open https://github.com/hacs/default and click **Fork** (top right).
2. Clone **your fork** (replace `YOUR_USERNAME` with your GitHub username):

   ```bash
   git clone https://github.com/YOUR_USERNAME/default.git hacs-default
   cd hacs-default
   ```

## 2. Create branch and make the edit

```bash
git checkout master
git pull origin master
git checkout -b add-android-management-api
```

Edit the file **`integration`** and add this line **after** the line  
`"Sha-Darim/brandriskute",`  
so it looks like:

```json
 "Sha-Darim/brandriskute",
 "Shaffer-Softworks/Android-Management",
 "shadow578/homeassistant_sma-ennexos",
```

(Same indentation as the other lines — two spaces before the quote.)

## 3. Commit, push, and open the PR

```bash
git add integration
git commit -m "Add Shaffer-Softworks/Android-Management"
git push origin add-android-management-api
```

Then:

1. Go to https://github.com/YOUR_USERNAME/default
2. Use the **“Compare & pull request”** banner, or go to https://github.com/hacs/default/compare and choose your branch.
3. Base: **hacs/default `master`** ← **Your fork branch: `add-android-management-api`**.
4. Fill out the PR template (confirm you’re owner or major contributor, repo has description/topics/issues/release, etc.).
5. Submit the PR.

## One-line patch (alternative)

If you prefer to apply the change as a patch from the root of your `hacs-default` clone:

```bash
# From repo root of your hacs-default clone
sed -i '' '/"Sha-Darim\/brandriskute",/a\
 "Shaffer-Softworks/Android-Management",
' integration
```

On Linux (no space after `-i`):

```bash
sed -i '/"Sha-Darim\/brandriskute",/a\ "Shaffer-Softworks/Android-Management",' integration
```

Then commit and push as in step 3.

---

After the PR is merged, your integration will appear in the next HACS scan; users won’t need to add a custom repo.
