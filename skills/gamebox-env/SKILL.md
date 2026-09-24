---
name: gamebox-env
description: Use when user invokes /gamebox-env or asks to verify machine setup for Buildbox Android builds - JDK, Android SDK/NDK, Gradle, ADB, Firebase CLI, emulator, live Play requirements.
---
> **Public version:** no hardcoded developer identity ships in this copy. Ask the user for organization name, contact email, and country code at the start of each run - never assume values.


# 🎮 GAMEBOX-ENV — Environment Check (+ Emulator Ready)
**GameBox V2.0 | Skill 1 of 6**
**Scope:** Machine-wide. Runs ONCE per machine/session — NOT per project.
**Output:** `./Reports/_ENV/ENV_report.md`
**Next:** GAMEBOX-SCAN-FIX

---

## PURPOSE

Verify the developer machine has every tool required to build, sign, and test
Buildbox-exported Android projects — for **any and all** projects the user
will work on afterward, including a working emulator so device testing in
GAMEBOX-TEST-APK (skill 3) can actually happen. One-time (or occasional
re-check) machine setup step, not repeated per project.

This skill makes **NO changes** to any project files.

---

## DEVELOPER DEFAULTS

Ask the user for these values at the start of each run - there are no baked-in defaults in this public copy:

| Field | Default Value |
|-------|---------------|
| Developer / Organization | Ask the user (e.g. GameBox) |
| Developer Email | [ask the user - developer contact email] |
| Country Code | Ask the user (e.g. EG) |

---

## STEP -1 — LIVE GOOGLE PLAY REQUIREMENTS CHECK (ALWAYS DO THIS FIRST)

Google Play's minimum target API level, Billing Library version, and 16 KB
page size deadlines change on a rolling basis. **Before running any checks,
web-search for the current requirements** — do not rely on memorized values.
Search terms to use:

- `Google Play target API level requirement current year`
- `Google Play Billing Library deprecation current version`
- `Google Play 16 KB page size requirement deadline`

Also, separately, web-search current enforcement on the **content policies**
that cause suspensions rather than build failures — these are judgment
calls, not code checks, and this pipeline previously treated them as
out-of-scope, which was a mistake:

- `Google Play Spam Minimum Functionality policy current`
- `Google Play Repetitive Content policy same developer account`
- `Google Play Intellectual Property policy games`

Record findings under a `## ⚠️ Content Policy Risk (live-checked)` section
in the report — this feeds directly into GAMEBOX-SCAN-FIX's new Policy &
Differentiation Risk Check (Phase 0). As of the last update to this skill:

| Policy | What it targets | Relevant here because |
|---|---|---|
| Spam & Minimum Functionality | Apps that crash, freeze, or function abnormally, or that provide no real value | Google explicitly folds "crashes/force closes" into this policy, not just a technical Broken Functionality bucket — repeated crash issues across an account read as a pattern, not isolated bugs |
| Repetitive Content | "Apps that are functionally identical to others the developer has published... uploading many similar apps under one developer account" | A developer account with many lightly-reskinned Buildbox template games is close to the textbook example Google gives |
| Intellectual Property | Using trademarked names, characters, music, or assets without rights | Common in template-based games that reuse stock names/audio |

> If this developer account has multiple similar Buildbox-template games,
> flag this explicitly to the user before continuing the pipeline — see
> GAMEBOX-SCAN-FIX Phase 0. Don't let technical fixes create false
> confidence about an app that has an unresolved content-policy risk.

---

## STEP -0.5 — ACCOUNT-LEVEL STATUS CHECK

Before doing anything else, ask the user to check **Play Console → Policy
and programmes → Policy status** (the account-level page, not any single
app's page). Record:
- Any account-level warning or strike count shown
- Whether any other apps in the account are currently suspended or rejected

If there's an active account-level warning, treat every project in this
session as higher-risk and make sure the Phase 0 check in GAMEBOX-SCAN-FIX
is not skipped for any of them.

---

## STEP -0 — LIVE GOOGLE PLAY TECHNICAL REQUIREMENTS TABLE

As of the last update to this skill, the known floor values were:

| Requirement | Minimum | Hard deadline |
|---|---|---|
| Target API level | Android 16 (API 36) | Aug 31, 2026 (extension to Nov 1, 2026 available) |
| Play Billing Library | 8.0.0 or later | Aug 31, 2026 (extension to Nov 1, 2026 available) — this is a **publishing gate**: apps already live keep working on older versions, but no new app/update can ship below 8.0.0 after the deadline |
| 16 KB memory page size support | Required for all native code | Already in effect for new apps/updates targeting Android 15+ |

Treat this table as a fallback only. **Always confirm with a fresh search**
and flag if the live search found newer/stricter values. These live-checked
values are what GAMEBOX-SCAN-FIX and every later skill compare projects
against.

---

## STEP 0 — CREATE THE SHARED FOLDERS

```bash
mkdir -p ./Reports/_ENV
mkdir -p ./Reports/_SCAN_ALL
mkdir -p ./APK_AAB
```

> Per-project folders (`Reports/[GameName]/`, `APK_AAB/[GameName]/`) are
> created later by GAMEBOX-SCAN-FIX once it knows how many projects exist
> and what they're named.

---

## INPUT REQUIRED

None. This skill checks the machine, not any specific project.

---

## CHECKS TO PERFORM

Run each check. Record result as ✅ OK, ❌ MISSING, or ⚠️ OUTDATED.

### Java JDK
```bash
java -version
```
- ✅ OK: 17.x or higher
- ⚠️ OUTDATED: below 17
- ❌ MISSING: command not found

**If missing:** `winget install Microsoft.OpenJDK.17` (Windows) or `sudo apt install openjdk-17-jdk` (Linux)

### Android SDK
Check `ANDROID_HOME` / `ANDROID_SDK_ROOT`.
Required: `platforms/android-36` (Android 16) or higher installed.
- ✅ OK: android-36+ present
- ⚠️ OUTDATED: only android-35/34 present (still buildable, but won't clear
  the Google Play target API requirement — see GAMEBOX-SCAN-FIX)
Also verify `cmdline-tools` and `platform-tools` exist.

### Android NDK
Check `$ANDROID_HOME/ndk/`.
Required: NDK **27.x or higher** (r28+ recommended) — reliable 16 KB page
size alignment for native `.so` libraries.
- ✅ OK: 27.x+ installed
- ⚠️ OUTDATED: below 27.x — flag as a 16 KB page size risk
List all installed NDK versions if multiple exist.

### Gradle
```bash
gradle -version
```
Required: **8.7 or higher** globally OR each project's own `gradlew`
wrapper pinned to 8.7+ (verified per-project in GAMEBOX-SCAN-FIX).

### ADB
```bash
adb version
```
Required: any version present. Record version string.

### Android Build Tools
Check `$ANDROID_HOME/build-tools/`.
Required: **36.x or higher**. List ALL installed versions.

### Keytool
```bash
keytool -help
```
Required: present (confirms JDK is properly installed). Needed for
GAMEBOX-AAB-PUBLISH keystore generation.

### Firebase CLI *(required for privacy policy hosting in GAMEBOX-AAB-PUBLISH)*
```bash
firebase --version
```
- ✅ OK: any version present
- ❌ MISSING: `npm install -g firebase-tools`

### Node.js *(required for Firebase CLI)*
```bash
node --version
```
- ✅ OK: 16.x or higher
- ❌ MISSING: install from https://nodejs.org

### Emulator / Device Testing Readiness *(new — needed for GAMEBOX-TEST-APK)*

The user has real physical devices to test on (required test path) and may
optionally also want an emulator (optional test path). Check both:

**Physical device path:**
```bash
adb devices
```
Just confirm ADB itself works — a physical device only needs to be plugged
in when GAMEBOX-TEST-APK actually runs, not now. Record ✅ ADB ready.

**Emulator path (optional but set up now so it's ready later):**
```bash
$ANDROID_HOME/emulator/emulator -list-avds
```
- ✅ OK: at least one AVD (Android Virtual Device) exists
- ⚠️ NONE FOUND: no AVD configured yet

If no AVD exists, offer to create one now (skip if the user says they'll
only test on real devices):
```bash
# List available system images first
sdkmanager --list | grep system-images

# Install a recent system image (adjust API level/ABI to match dev machine —
# use x86_64 for Intel/AMD hosts, arm64-v8a for Apple Silicon hosts)
sdkmanager "system-images;android-36;google_apis;x86_64"

# Create the AVD
avdmanager create avd -n GameBox_Test -k "system-images;android-36;google_apis;x86_64" -d pixel_6

# Quick boot test (run in background, then close)
$ANDROID_HOME/emulator/emulator -avd GameBox_Test -no-snapshot &
adb wait-for-device
adb devices
```
Confirm the emulator boots and appears in `adb devices` as `device` (not
`offline`), then it can be closed — GAMEBOX-TEST-APK will start it again
when actually needed.

### Disk Space
⚠️ Warn if less than 2 GB available.

---

## ISSUE CLASSIFICATION

| Level | Meaning |
|-------|---------|
| 🔴 CRITICAL | Tool missing or too old to build at all |
| 🟠 HIGH | Tool present but version may cause issues |
| 🟡 MEDIUM | Optional tool missing or suboptimal |
| 🔵 LOW | Optimization suggestion |

---

## OUTPUT — `./Reports/_ENV/ENV_report.md`

```markdown
# 🎮 GAMEBOX-ENV Report
**Scope:** Machine-wide (applies to all projects)
**Generated:** [date time]
**Skill:** GameBox V2.0 — 1 of 6

---

## 📊 Summary

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | N |
| 🟠 HIGH | N |
| 🟡 MEDIUM | N |
| 🔵 LOW | N |

---

## 🖥️ Environment Status

| Tool | Status | Version / Path | Notes |
|------|--------|----------------|-------|
| Java JDK | ✅ OK | 17.0.x | |
| Android SDK | ✅ OK | /path/to/sdk (android-36) | |
| Android NDK | ✅ OK | 27.x+ | 16 KB page size ready |
| Gradle | ❌ MISSING | | need 8.7+ |
| ADB | ✅ OK | 36.0.0 | |
| Build Tools | ✅ OK | 36.0.0 | |
| Keytool | ✅ OK | via JDK 17 | |
| Firebase CLI | ✅ OK | 13.x.x | |
| Node.js | ✅ OK | 20.x.x | |
| Emulator / AVD | ✅ OK | GameBox_Test (android-36) | boots and appears in `adb devices` |
| Disk Space | ✅ OK | 45 GB free | |

---

## 🌐 Current Google Play Requirements (live-checked)

| Requirement | Minimum found via search | Deadline |
|---|---|---|
| Target API level | [fill from live search] | [fill from live search] |
| Play Billing Library | [fill from live search] | [fill from live search] |
| 16 KB page size support | [fill from live search] | [fill from live search] |

---

## ⚠️ Content Policy Risk (live-checked)

| Policy | Current enforcement notes (live search) |
|---|---|
| Spam & Minimum Functionality | [fill from live search] |
| Repetitive Content | [fill from live search] |
| Intellectual Property | [fill from live search] |

## 🏢 Account-Level Status (user-reported)

| Field | Value |
|-------|-------|
| Account-level warning/strikes shown? | Yes/No — [detail] |
| Other apps currently suspended/rejected in this account | [list] |

> If Yes above, GAMEBOX-SCAN-FIX Phase 0 (Policy & Differentiation Risk
> Check) is mandatory for every project this session, not optional.

---

## 🚨 Issues Found

### 🔴 CRITICAL
- [ ] **[Issue title]** — [description]
  > Fix: [exact command]

### 🟠 HIGH
*(none)*

### 🟡 MEDIUM
*(none)*

### 🔵 LOW
*(none)*

---

## ✅ Next Step
All CRITICAL issues resolved → Run **GAMEBOX-SCAN-FIX** and point it at the
folder containing one or more Android projects.
```

---

## AFTER WRITING THE REPORT

Tell the user:

> `✅ ENV report saved to ./Reports/_ENV/ENV_report.md`
> `Machine is ready — including an emulator for testing later.`
> `Resolve any CRITICAL items, then run GAMEBOX-SCAN-FIX and point it at your projects folder.`

List any CRITICAL issues directly in chat — don't make the user open the file to find blockers.

---

## Next - Run /gamebox-scan-fix and point it at your projects folder.



