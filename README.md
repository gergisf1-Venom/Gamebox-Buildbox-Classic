# Gamebox-Buildbox-Classic

Take a Buildbox-exported Android game from source code to a signed release AAB on Google Play, in two ways:

- **GameBox Protocol v2** — a paste-per-step protocol you run with any AI coding assistant on a single exported Android project. **Recommended for buyers.**
- **OpenCode plugin** — summonable `/gamebox-xxx` skills for OpenCode users.

---

## Way 1 — GameBox Protocol v2 (paste-per-step, buyers)

Works on **one already-exported Android project** — no Buildbox and no `.bbdoc` file required. Open the project folder in your working environment, copy the step prompt to your assistant, and it follows the referenced file. Run the five steps in order: every file states what is read-only and where the assistant must wait for your approval.

| Step | File | What it does |
|---|---|---|
| 1 | [protocol/gamebox-1-env.md](protocol/gamebox-1-env.md) | Collect the reskin identity (app title, new package ID, every AdMob unit ID, IAP product IDs), locate and identify the project, inspect machine + live Google Play requirements. **Read-only.** |
| 2 | [protocol/gamebox-2-update.md](protocol/gamebox-2-update.md) | Apply the confirmed identity, AdMob IDs, and IAP product IDs — every proposed edit is shown first and applied only after your explicit approval. |
| 3 | [protocol/gamebox-3-scan-fix.md](protocol/gamebox-3-scan-fix.md) | Policy & differentiation gate, then a read-only Android configuration audit, then approval-only fixes. |
| 4 | [protocol/gamebox-4-test-apk.md](protocol/gamebox-4-test-apk.md) | Build a test-only debug APK and require a real-device test result (emulator-only never passes). |
| 5 | [protocol/gamebox-5-aab.md](protocol/gamebox-5-aab.md) | Signed release AAB with the designated key; verify the signature and 16 KB page-size compatibility. |

### Paste prompts

Tell your assistant exactly this, one step at a time:

1. `Read and follow protocol/gamebox-1-env.md for this project. Collect the displayed app name, package name, every AdMob ID in use, and the IAP IDs if the app has purchases. Then inspect the Android project, the build machine, and the current Google Play requirements. Do not modify project files in this step.`
2. `Read and follow protocol/gamebox-2-update.md using the ENV report and the information I provide. Show the files, old values, new values, and proposed changes in full, and wait for my confirmation before editing any file.`
3. `Read and follow protocol/gamebox-3-scan-fix.md for this project now that Update is complete. Scan first without editing, then show each proposed fix and wait for my approval before applying it.`
4. `Read and follow protocol/gamebox-4-test-apk.md. Build a test APK only, and record the result of testing on a real Android device before moving on to release.`
5. `Read and follow protocol/gamebox-5-aab.md only after the real-device test passes. Use the approved signing key for this app, and produce a signed AAB only.`

### Protocol rules

- Never change gameplay, graphics, ad behavior, or purchase logic.
- Every modification is shown before it is applied, with approval at the points the step files specify.
- Passwords and signing keys never go into the repository, commands, or reports — local handling only, and an existing key is replaced only by an explicit decision.
- The APK is for testing only; the release artifact is a signed AAB. No release APK, no upload, no production rollout by the assistant.
- Check Google Play requirements from official sources at execution time — never trust numbers copied from older files.

---

## Way 2 — OpenCode plugin

One-line install:

```bash
npx -y gamebox-buildbox-classic
```

Then restart OpenCode. (This adds `gamebox-buildbox-classic@latest` to the `plugin[]` array in your global `opencode.json`. Dry run: append `--dry-run`. Project-local instead: run with `--project` inside the project folder.)

> Need OpenCode-agnostic use or just want the docs? Run the protocol in Way 1 instead.

### Commands

| Command | Skill | What it does |
|---|---|---|
| `/gamebox-env` | `gamebox-env` | Machine setup check (JDK/SDK/NDK/Gradle/emulator) + live Play requirements |
| `/gamebox-scan-fix` | `gamebox-scan-fix` | Discover/count projects, select one or multiple, policy check, then fix one project at a time |
| `/gamebox-update` | `gamebox-update` | Refresh a re-export from prior reports: delta-scan changed files, fix, then full audit |
| `/gamebox-test-apk` | `gamebox-test-apk` | Re-verify fixes, build unsigned test APK, real-device testing |
| `/gamebox-aab-publish` | `gamebox-aab-publish` | Signed release AAB, privacy policy, SEO listing, Play Console guide |
| `/gamebox-listing-assets` | `gamebox-listing-assets` | Play Store graphics (screenshots, feature graphic, icon) |

Pipeline order: `env` → `scan-fix` → `test-apk` → `aab-publish` (→ `listing-assets` when graphics are missing). Use `update` after a `.bbdoc` change/new export instead of rescanning blindly. Each skill ends with a `## Next` pointer.

### Bundled screenshot tool

`tools/play-assets/` contains the generic listing-asset pipeline used by `/gamebox-listing-assets`:

```bash
pip install -r tools/play-assets/requirements.txt
python tools/play-assets/make_play_assets.py
```

Copy `.env.example` to `.env` for the Gemini backend only; never commit a real key. Generated `gen_raw/` output, caches, and `.env` files are intentionally not shipped.

## Privacy note

Unlike the author's private copy, **this public version ships with no hardcoded developer identity**. Every run asks you for organization name, contact email, and country code — nothing of the author's is baked in.

## Layout

```
protocol/gamebox-1-env.md … gamebox-5-aab.md  # GameBox Protocol v2 step files (any AI assistant)
skills/<name>/SKILL.md                        # full procedure per stage (loaded via skill tool)
commands/<name>.md                            # thin /command wrappers (Follow the skill exactly)
tools/play-assets/                            # bundled screenshot/listing-asset pipeline (no secrets)
src/index.js                                  # no-op plugin entry so OpenCode loads the package
bin/install.mjs                               # one-line installer (gamebox-install)
```

## License

MIT
