# Gamebox-Buildbox-Classic

OpenCode plugin with 6 summonable skills for shipping **Buildbox-exported Android games** to Google Play: environment check, scan & fix, re-export update, test APK, signed AAB + publish guide, and store-listing graphics.

## One-line install

```bash
npx -y gamebox-buildbox-classic
```

Then restart OpenCode. (This adds `gamebox-buildbox-classic@latest` to the `plugin[]` array in your global `opencode.json`. Dry run: append `--dry-run`. Project-local instead: run with `--project` inside the project folder.)

> Requires the package to be published to npm. Until then: `gh repo clone gergisf1-Venom/Gamebox-Buildbox-Classic` and add `"plugin": ["file:<path>"]`, or copy `skills/` + `commands/` into your project's `.opencode/` folder.

## Commands

| Command | Skill | What it does |
|---|---|---|
| `/gamebox-env` | `gamebox-env` | Machine setup check (JDK/SDK/NDK/Gradle/emulator) + live Play requirements |
| `/gamebox-scan-fix` | `gamebox-scan-fix` | Discover/count projects, select one or multiple, policy check, then fix one project at a time |
| `/gamebox-update` | `gamebox-update` | Refresh a re-export from prior reports: delta-scan changed files, fix, then full audit |
| `/gamebox-test-apk` | `gamebox-test-apk` | Re-verify fixes, build unsigned test APK, real-device testing |
| `/gamebox-aab-publish` | `gamebox-aab-publish` | Signed release AAB, privacy policy, SEO listing, Play Console guide |
| `/gamebox-listing-assets` | `gamebox-listing-assets` | Play Store graphics (screenshots, feature graphic, icon) |

Pipeline order: `env` → `scan-fix` → `test-apk` → `aab-publish` (→ `listing-assets` when graphics are missing). Use `update` after a `.bbdoc` change/new export instead of rescanning blindly. Each skill ends with a `## Next` pointer.

## Bundled screenshot tool

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
skills/<name>/SKILL.md   # full procedure per stage (loaded via skill tool)
commands/<name>.md       # thin /command wrappers (Follow the skill exactly)
tools/play-assets/       # bundled screenshot/listing-asset pipeline (no secrets, no generated images)
src/index.js             # no-op plugin entry so OpenCode loads the package
bin/install.mjs          # one-line installer (gamebox-install)
```

## License

MIT
