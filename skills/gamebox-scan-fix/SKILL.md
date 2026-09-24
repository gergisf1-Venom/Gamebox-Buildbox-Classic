---
name: gamebox-scan-fix
description: Use when user invokes /gamebox-scan-fix or asks to scan and fix Buildbox-exported Android projects - target SDK, AGP, manifest exported, ProGuard keep rules, Billing 8+, 16KB alignment.
---
> **Public version:** no hardcoded developer identity ships in this copy. Ask the user for organization name, contact email, and country code at the start of each run - never assume values.


# 🎮 GAMEBOX-SCAN-FIX — Select, Scan, and Fix Projects
**GameBox V2.0 | Skill 2 of 6**
**Scope:** Only the Android projects the user selects from the given parent folder — scanned,
then fixed ONE PROJECT AT A TIME with user approval.
**Output:**
- `./Reports/_SCAN_ALL/SCAN_ALL_report.md` (consolidated scan, selected projects)
- `./Reports/[GameName]/[GameName]_Report.md` (the ONE master report per
  project — created here, appended to by every later skill)
- `./Reports/[GameName]/_internal/SCAN_data.txt` (machine-readable, not a
  user-facing report)
- `./Reports/[GameName]/_internal/STATE.json` (tracks pipeline progress for
  this project so nothing has to restart from scratch)
**Next:** GAMEBOX-TEST-APK

---

## PURPOSE

Given a parent folder, auto-detect every Android project inside it, show the
project count and list, let the user select one or multiple projects, deep-scan
only those selected projects for anything blocking a successful build or Google
Play submission, produce a consolidated scan report — then **immediately apply
fixes** project by project with user confirmation.

**PHASE 1 (SCAN)** makes NO changes to any project files.
**PHASE 2 (FIX)** modifies project files with user approval.

> Note: this pipeline does not use Git snapshots or version control of any
> kind. The user edits the source `.bbdoc` in Buildbox and re-exports, so
> this scan/fix cycle is expected to run fresh on every export — don't
> propose or require a git-based backup step.

---

# ═══════════════════════════════════════════
# PHASE 0 — POLICY & DIFFERENTIATION RISK CHECK
# (mandatory, runs before technical scanning, cannot be skipped silently)
# ═══════════════════════════════════════════

## WHY THIS EXISTS

Technical fixes (target SDK, ProGuard, 16 KB alignment, crash prevention)
cannot fix a **content policy** violation — things like Spam & Minimum
Functionality, Repetitive Content, or Intellectual Property. These are
judgment calls Google makes about the app itself and the developer
account's overall pattern, not bugs in the code. A pipeline that only
checks build correctness can produce a technically perfect AAB that still
gets suspended. This phase exists specifically to stop that from happening
silently.

**Do not skip this phase even if the user seems impatient to get to the
technical scan.** If a real content-policy risk exists and this phase is
skipped, the rest of the pipeline's work can be wasted on an app that was
never going to be approved regardless of code quality.

## STEP 1 — CATALOG-LEVEL SIMILARITY CHECK

Before scanning this project's code, look at what else is in
`./Reports/` from prior runs (other games already processed in this
workspace) and ask the user directly:

> `Does [GameName] share the same core mechanic, template structure, or
> art style with other apps already in this developer's Google Play
> account (published, in review, or previously rejected/suspended)?`

If the answer is yes, or the user is unsure, ask a follow-up:

> `What is genuinely different about this game versus the others — unique
> art/character design, a meaningfully different mechanic, original audio,
> original level design? (Reskinning a Buildbox template with a new coat
> of paint and a new name is NOT sufficient differentiation in Google's
> current enforcement — see the Repetitive Content policy notes in the
> ENV report.)`

Record the answer verbatim in the master report. **If the user cannot name
genuine differentiation beyond cosmetic changes, stop here and say so
plainly** — recommend they address content differentiation before this
game goes anywhere near Google Play, regardless of how clean the code
ends up. Continuing anyway is the user's call, but it must be an informed
one, not a silent pipeline default.

## STEP 2 — INTELLECTUAL PROPERTY QUICK CHECK

Ask/check:
- Does the app name, icon, or any character resemble an existing
  trademarked game, franchise, or character (even loosely)?
- Are any audio/music files, fonts, or bought asset packs used without a
  license the user can confirm they hold?
- Web-search the exact app name + "google play" to see if a similarly
  named existing app/trademark already exists.

Flag anything uncertain as 🟠 HIGH in the scan report — this is not
something code can fix, only asset/licensing changes can.

## STEP 3 — ACCOUNT HISTORY CHECK

Ask the user to confirm: has this specific app, or any app from this
developer account, been previously rejected or suspended? If yes, ask for
the exact policy name from that notice (not just "policy violation") and
record it — a repeat submission of a previously-flagged issue is treated
by Google as escalating, not as a fresh case.

## OUTPUT — append to `./Reports/[GameName]/[GameName]_Report.md`

```markdown
## ⚠️ Policy & Differentiation Risk Check
**Checked:** [date time]

| Question | Answer |
|----------|--------|
| Shares template/mechanic/art with other apps in this account? | Yes/No |
| Genuine differentiation named by user | [verbatim answer, or "none identified"] |
| IP/trademark concern flagged? | Yes/No — [detail] |
| Prior rejection/suspension on this app or account? | Yes/No — [exact policy name if known] |

**Risk level:** 🟢 Low / 🟠 Elevated / 🔴 High — proceed only with user's
explicit acknowledgment if 🟠 or 🔴.
```

Only proceed to Phase 1 (technical scan) once this is recorded — if risk is
🔴 High, get an explicit "I understand and want to proceed anyway" before continuing.

---

# ═══════════════════════════════════════════
# PHASE 1 — SCAN
# ═══════════════════════════════════════════

## STEP 0 — VERIFY ENV

Confirm `./Reports/_ENV/ENV_report.md` exists with no unresolved 🔴 CRITICAL
items. If missing or unresolved → stop and direct user to GAMEBOX-ENV first.

Re-confirm the current Google Play requirements table from that report —
every project scanned below is checked against those same live-confirmed
numbers.

---

## STEP 1 — DISCOVER PROJECTS

Ask the user for the parent folder path, unless already provided.

Auto-detect a folder as an Android project if it contains any of:
- `build.gradle` (project-level) or `build.gradle.kts`
- `settings.gradle` or `settings.gradle.kts`
- `AndroidManifest.xml` anywhere under it

List all detected projects with their count, then let the user select one or
multiple projects before scanning anything:

1. Show: `Found N Android projects:` followed by a numbered list with game/app
   name when known, package when known, project path, and prior report/state
   when available.
2. Use the `question` tool with `multiple: true` so the user can select one or
   multiple entries. Include an explicit “All N projects” choice.
3. Do not scan, initialize, modify, or create reports/state for unselected
   projects.

For each selected project, derive its **Game Name** (from `strings.xml`
`app_name`, or the folder name if that fails) and create its folder
structure:

```bash
mkdir -p ./Reports/[GameName]/_internal
mkdir -p ./APK_AAB/[GameName]
```

Create/initialize `./Reports/[GameName]/_internal/STATE.json`:
```json
{
  "project": "[GameName]",
  "package": "[packageName]",
  "last_updated": "[date time]",
  "env": "PASS",
  "scan": "PENDING",
  "fix": "PENDING",
  "test_apk": "PENDING",
  "aab_publish": "PENDING"
}
```
Update this file's relevant field at the end of every phase in every skill
from now on — this is how the pipeline knows where a project left off if
the user comes back to it later. Keep it small; it is not a report the user
needs to read, just state.

Create/initialize `./Reports/[GameName]/[GameName]_Report.md` (the master
report — see format at the end of this skill) with the Scan section filled
in once scanning finishes.

---

## SCAN AREAS (run for EACH selected project)

### 1. Project Identity
- Game Name → `res/values/strings.xml` (app_name)
- Package Name → `AndroidManifest.xml` or `applicationId` in `build.gradle`
- Version Name + Code → `app/build.gradle`
- Build system type: Gradle or Ant

### 2. Build System Detection
- [ ] `build.gradle` (project-level) exists
- [ ] `app/build.gradle` exists
- [ ] `gradle/wrapper/gradle-wrapper.properties` exists
- [ ] `build.xml` exists → CRITICAL: Ant detected, full migration required
- [ ] `settings.gradle` exists

### 3. SDK Versions
- `minSdk` → record value
- `targetSdk` → must be **36+ (Android 16)** → ❌ CRITICAL if lower
  - 35 → 🟠 HIGH
  - 34 or lower → 🔴 CRITICAL
- `compileSdk` → must be **36+** → ❌ CRITICAL if lower

### 4. Android Gradle Plugin (AGP)
- Current AGP version in project-level `build.gradle`
- Target: **AGP 8.5.1 or higher**
- Below AGP 7.x → 🔴 CRITICAL
- AGP 7.x or 8.0–8.4.x → 🟠 HIGH
- Verify Gradle wrapper compatible (AGP 8.5.1+ needs Gradle 8.7+)

### 5. Namespace Field
- Must exist inside `android { }` in `app/build.gradle`
- Missing → 🔴 CRITICAL (build fails with AGP 8.x)

### 6. Java Compatibility
- `sourceCompatibility` + `targetCompatibility` must be `JavaVersion.VERSION_17`
- Anything lower → 🟠 HIGH

### 7. AndroidX Migration
- Search for `android.support.*` imports/dependencies → 🟠 HIGH
- Check `gradle.properties` for `android.useAndroidX=true`

### 8. Build Tools Version
- Must be 36.x or higher → 🟠 HIGH if lower

### 9. ProGuard / R8 Rules
- Does `proguard-rules.pro` exist?
- Contains Buildbox native library keep rules? → 🟠 HIGH if missing
- Contains Cocos2dx, ad SDK, IAB class rules **for every SDK actually
  detected in section 17 below**? → 🟠 HIGH if any detected SDK has no
  matching keep rule (see PHASE 2 dynamic ProGuard generation — this is the
  #1 cause of "app opens then crashes" rejections when a real ad SDK class
  gets stripped by R8 in the release build with no rule protecting it)

### 10. Native Libraries (NDK / .so files)
- Scan `jniLibs/` or `libs/` for ABI folders
- Missing `arm64-v8a` → 🟠 HIGH
- `android.ndkVersion` not declared → 🟡 MEDIUM

### 11. AndroidManifest.xml
- All `<activity>`, `<service>`, `<receiver>` must have `android:exported`
- Missing → 🔴 CRITICAL
- Risky permissions scan:
  - `ACCESS_FINE_LOCATION` → requires privacy policy
  - `READ_PHONE_STATE` → may trigger review
  - `QUERY_ALL_PACKAGES` → requires justification
  - `READ_CONTACTS` → sensitive
  - `WRITE_EXTERNAL_STORAGE` → requires justification on SDK 29+

### 12. Dependencies
- List all with current version vs latest stable
- Flag outdated critical dependencies

### 13. Google Play Services
- Included as local library project? → 🔴 CRITICAL
- Must be Maven dependency: `com.google.android.gms:play-services-*`

### 14. Google Play Billing Library Version
- Search for `com.android.billingclient:billing`
- Below 8.0.0 → 🔴 CRITICAL
- 8.0.0+ → ✅ OK. Record exact version.
- Not present but game has IAP → 🟠 HIGH (verify manually)

### 15. 16 KB Memory Page Size Support
- [ ] `android.ndkVersion` is 27.x+ in `app/build.gradle`
- [ ] AGP version is 8.5.1+
- [ ] No legacy packaging override that would repack unaligned `.so` files
- [ ] Third-party `.so` files (ad SDKs, analytics, Buildbox native runtime)
      verified for 16 KB alignment
- Missing/insufficient NDK or AGP → 🔴 CRITICAL
- Unverified third-party `.so` → 🟠 HIGH

Verification:
```bash
objdump -p <extracted.so> | grep LOAD
```
`align 2**14` (16384) = compliant. `align 2**12` = 4 KB only → non-compliant.

### 16. In-App Purchase Detection
- Search for `com.android.vending.BILLING` permission in `AndroidManifest.xml`
- Search for `com.android.billingclient` in dependencies
- Search for IAP-related class imports in Java/Kotlin source
- Record: **Has IAP: Yes/No**
- If Yes, scan for product ID strings in source (common patterns:
  `"remove_ads"`, `"coins_"`, `"no_ads"`, `"premium"`) and list any found —
  needed in GAMEBOX-AAB-PUBLISH for Google Play Console IAP setup

### 17. Ad SDK Detection *(feeds directly into dynamic ProGuard rules — do not skip)*
Search for ad-related dependencies in `build.gradle`:
- `com.google.android.gms:play-services-ads` (AdMob)
- `com.unity3d.ads` (Unity Ads)
- `com.vungle` (Vungle/Liftoff)
- `com.facebook.ads` (Meta Audience Network)
- `com.applovin` (AppLovin)
- `com.ironsource` (ironSource)

Record: **Has Ads: Yes/No** and the **exact list** of which SDK package
prefixes are present — this exact list is what PHASE 2 uses to generate
ProGuard keep rules. Missing a detected SDK from this list is what causes
silent R8 stripping and "app opens then crashes" store rejections.

### 18. Proven Buildbox Issue Catalog (Fast AI Detection)
Check for these 12 recurring issues discovered in previous real-world
Buildbox exports (Ball Blast, Up Heights, Risky Rooms, The Impossible Game,
Zombie Killer, Adventure):

1. **`ConsentActivity` Missing `android:exported`**
   - Check `AndroidManifest.xml` for `com.buildbox.consent.ConsentActivity` missing `android:exported="false"`.
   - *Severity:* 🔴 CRITICAL (Causes build failure / crash on API 31+).

2. **Missing `proguard-rules.pro` File or Reference Mismatch**
   - Check if `app/build.gradle` references `proguard-rules.txt` (or `.pro`) but the file does not exist, or lacks keep rules for `com.secrethq.**`, `org.cocos2dx.**`, `com.google.android.gms.**`, `com.android.billingclient.**`, `com.vungle.**`, or `com.buildbox.consent.**`.
   - *Severity:* 🟠 HIGH (Causes R8/ProGuard release build to strip JNI / AdMob / Billing native classes — the same root cause tracked in section 9/17).

3. **Version Attributes in `AndroidManifest.xml` instead of `app/build.gradle`**
   - Check `<manifest>` tag for `android:versionCode` or `android:versionName`.
   - *Severity:* 🟠 HIGH (Overrides Gradle versioning during store upload).

4. **Legacy AIDL Billing Directory (`IInAppBillingService.aidl`)**
   - Check if `app/src/main/aidl/` exists containing `IInAppBillingService.aidl`.
   - *Severity:* 🔴 CRITICAL (Conflicts with Google Play Billing Library 8.0.0+).

5. **Deprecated Nested `android { packagingOptions {} }` Block**
   - Check `app/build.gradle` for nested `packagingOptions { }` inside `android { }` block or deprecated AGP 7 syntax.
   - *Severity:* 🟠 HIGH (Deprecated in AGP 8.x).

6. **Kotlin `jvmTarget` Mismatch**
   - Check project-level `build.gradle` for `jvmTarget = "11"` (or lower) when `app/build.gradle` `compileOptions` uses `VERSION_17`.
   - *Severity:* 🟠 HIGH (Kotlin compile error with Java 17).

7. **AdMob `AdActivity` Missing `configChanges` or `android:exported`**
   - Check `AndroidManifest.xml` for `com.google.android.gms.ads.AdActivity` missing `android:configChanges="keyboard|keyboardHidden|orientation|screenLayout|uiMode|screenSize|smallestScreenSize"` or `android:exported="false"`.
   - *Severity:* 🔴 CRITICAL (Primary cause of app crashes after watching rewarded/interstitial ads on real devices — this is very likely the exact cause behind any "app opens, but it keeps crashing" rejection).

8. **Missing `android.suppressUnsupportedCompileSdk` in `gradle.properties`**
   - Check `gradle.properties` when compiling against API 35/36 with AGP 8.x.
   - *Severity:* 🟡 MEDIUM.

9. **Duplicate Dependency Declarations**
   - Check `app/build.gradle` for duplicate entries.
   - *Severity:* 🟡 MEDIUM.

10. **Deprecated `ProgressDialog` in Buildbox Purchase Code**
    - Check `com/secrethq/store/PTStoreBridge.java` or `PTPlayer.java`.
    - *Severity:* 🟡 MEDIUM.

11. **Legacy Local Library Projects / Local JARs**
    - Check for `compile project(':libs/google-play-services_lib')` or unused legacy JARs in `app/libs/`.
    - *Severity:* 🔴 CRITICAL.

12. **Missing `ndkVersion` Declaration**
    - Check `app/build.gradle` for missing `ndkVersion "27.0.12077973"`.
    - *Severity:* 🟡 MEDIUM.

---

## ISSUE CLASSIFICATION

| Level | Meaning |
|-------|---------|
| 🔴 CRITICAL | Prevents build or Play Store submission entirely |
| 🟠 HIGH | Likely store rejection or release crash |
| 🟡 MEDIUM | Compatibility or maintainability concern |
| 🔵 LOW | Optimization suggestion |

---

## FIXING PLAN SOP FORMAT (per project)

```
### TASK-001 — [Short title]
**Severity:** 🔴 CRITICAL
**File:** `relative/path/to/file`

**Remove:**
```code to remove (or "N/A — new addition")```

**Add / Replace with:**
```exact new code```

**Reason:** One sentence.
```

Number from 001 **within each project** (tasks reset per project).

---

## SCAN OUTPUT

### `./Reports/_SCAN_ALL/SCAN_ALL_report.md` (consolidated, selected projects)

```markdown
# 🎮 GAMEBOX-SCAN-FIX Report (Scan Phase)
**Parent Folder:** [path]
**Projects Discovered:** N
**Projects Selected:** M
**Projects Scanned:** M
**Generated:** [date time]
**Skill:** GameBox V2.0 — 2 of 6

---

## 📊 Overall Summary

| Project | 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🔵 LOW | Has Ads | Has IAP |
|---------|------------|--------|-----------|--------|---------|---------|
| [GameName1] | N | N | N | N | Yes (AdMob) | No |
| **TOTAL** | N | N | N | N | | |

## ✅ Scan complete — proceeding to Fix Phase below.
```

### `./Reports/[GameName]/_internal/SCAN_data.txt` (per project, machine-readable)
Plain text, `KEY=VALUE` per line for identity fields + that project's task
list + detected ad SDK list. Not a user-facing report.

### `./Reports/[GameName]/[GameName]_Report.md` — SCAN section
Append a `## 🔍 Scan Results` section to the master report with: identity
table, SDK/build config table, native libs table, 16 KB alignment table,
Google Play compliance table, permission risk table, ads/IAP summary. Keep
it a straight factual record — the fixing plan detail itself lives in the
scan data file, not duplicated at length in the master report.

---

## AFTER SCAN, TELL THE USER:

> `✅ Scan complete across [M] selected projects ([N] discovered). [X] total CRITICAL, [X] HIGH, [X] MEDIUM, [X] LOW.`
> `Proceeding to Fix Phase — you'll confirm each selected project separately.`

List every project with 🔴 CRITICAL issues directly in chat, grouped by project name.

---

# ═══════════════════════════════════════════
# PHASE 2 — FIX
# ═══════════════════════════════════════════

## GLOBAL SAFETY RULES (apply to every project)

**Never modify under any circumstances:**
- Gameplay logic or game mechanics
- Game assets (images, audio, levels)
- Advertisement or monetization logic

**Only allowed to modify:**
- `build.gradle` (project and app level)
- `settings.gradle`
- `gradle/wrapper/gradle-wrapper.properties`
- `AndroidManifest.xml` (structural attributes only)
- `proguard-rules.pro`
- `gradle.properties`

There is no Git or snapshot step in this pipeline — the user re-exports
from the Buildbox `.bbdoc` source and expects to re-run this scan/fix fresh
each time. Don't propose backups; just apply approved fixes directly.

---

## EXECUTION PROCESS — PROJECT BY PROJECT

Process projects **one at a time, in the order listed in SCAN_ALL_report.md**.
Do not start Project N+1 until Project N is either fully processed or the
user explicitly says to move on / skip it.

### For each project:

1. Announce: `📦 Now fixing: [GameName] ([X] tasks)`
2. Load that project's task list from `_internal/SCAN_data.txt`
3. Ask: **Apply mode for THIS project?**
   - **One by one** *(recommended)* — user reviews each diff before applying
   - **All at once** — applies all of this project's fixes after a single confirmation
   - This choice does **not** carry over to the next project.

#### One by one mode
For each TASK-NNN in order:
1. Show task title and severity
2. Show exact before/after diff
3. Ask: `Apply this fix? (yes / skip / stop)`
4. YES → apply, confirm success, wait for "continue"
5. SKIP → log as skipped with reason
6. STOP → halt, write partial log for this project, ask whether to move to
   the next project or stop the whole run

#### All at once mode
1. Show complete list of all changes for this project
2. Ask for single confirmation
3. Apply all in sequence, log each result

### On failure (any mode)
Show exact error. Do NOT move to next task/project. Ask: `retry / skip / stop`.

### Between projects
`Move on to [next GameName]? (yes / skip this project / stop entirely)`

---

## PHASE 2a — DYNAMIC PROGUARD RULE GENERATION *(do this before the fix list)*

Before applying the standard fix reference below, build this project's
**exact** ProGuard keep-rule set from what section 17 actually detected —
never rely on a fixed generic list, since a missing rule for an SDK the
game actually uses is the single most common cause of "app opens, then
crashes" store rejections (R8 silently strips a class the ad SDK needs at
runtime, but the debug/unoptimized build never showed the problem).

Base rules (always include):
```proguard
-keep class com.buildbox.** { *; }
-keepclassmembers class com.buildbox.** { *; }
-dontwarn com.buildbox.**
-keep class org.cocos2dx.** { *; }
-keepclassmembers class org.cocos2dx.** { *; }
-dontwarn org.cocos2dx.**
-keep class **.R
-keep class **.R$* { *; }
```

Then add ONE block per SDK actually found in section 17 / section 16:

| Detected in project | Add these keep rules |
|---|---|
| Play Billing (`com.android.billingclient`) | `-keep class com.android.billingclient.** { *; }` |
| AdMob (`play-services-ads`) | `-keep class com.google.android.gms.ads.** { *; }`<br>`-keep class com.google.android.gms.internal.ads.** { *; }` |
| Vungle/Liftoff (`com.vungle`) | `-keep class com.vungle.** { *; }`<br>`-dontwarn com.vungle.**` |
| Meta Audience Network (`com.facebook.ads`) | `-keep class com.facebook.ads.** { *; }`<br>`-dontwarn com.facebook.ads.**` |
| AppLovin (`com.applovin`) | `-keep class com.applovin.** { *; }`<br>`-dontwarn com.applovin.**` |
| ironSource (`com.ironsource`) | `-keep class com.ironsource.** { *; }`<br>`-dontwarn com.ironsource.**` |
| Unity Ads (`com.unity3d.ads`) | `-keep class com.unity3d.ads.** { *; }`<br>`-dontwarn com.unity3d.ads.**` |

Write the resulting merged rule set to `proguard-rules.pro` as one of the
fix tasks (TASK-NNN, severity 🟠 HIGH if any detected SDK was previously
unprotected). Show the user the exact final file content before applying.

---

## COMMON FIX REFERENCE

### compileSdk / targetSdk
```gradle
// REMOVE:
compileSdkVersion 29
targetSdkVersion 29
// ADD:
compileSdk 36
targetSdk 36
```

### AGP version
```gradle
// project-level build.gradle — REMOVE:
classpath 'com.android.tools.build:gradle:4.x.x'
// ADD:
classpath 'com.android.tools.build:gradle:8.5.1'
```
> Prefer the newest stable 8.x release available at fix time — check before applying.

### Gradle wrapper
```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-all.zip
```

### namespace field
```gradle
namespace "com.yourorg.gamename"
```

### Java compatibility
```gradle
compileOptions {
    sourceCompatibility JavaVersion.VERSION_17
    targetCompatibility JavaVersion.VERSION_17
}
```

### android:exported
```xml
android:exported="true"   <!-- launcher activity / external intents -->
android:exported="false"  <!-- internal components only -->
```

### NDK version
```gradle
ndkVersion "27.0.12077973"
```

### Google Play Billing Library version
```gradle
// REMOVE (any version below 8.0.0):
implementation 'com.android.billingclient:billing:6.x.x'
implementation 'com.android.billingclient:billing:7.x.x'
// ADD:
implementation 'com.android.billingclient:billing:8.0.0'
```
> Check for the latest stable 8.x+ release before applying. If the game has
> no in-app purchases, confirm with the user before skipping. Flag any
> removed-API call sites for manual review — this skill does not rewrite
> game logic.

### 16 KB memory page size support
```gradle
android {
    packagingOptions {
        jniLibs {
            useLegacyPackaging = false
        }
    }
}
```

### AndroidX migration
```properties
android.useAndroidX=true
android.enableJetifier=true
```

### Google Play Services (local → Maven)
```gradle
// REMOVE:
compile project(':libs/google-play-services_lib')
// ADD:
implementation 'com.google.android.gms:play-services-ads:23.x.x'
```

### Duplicate .so files
```gradle
android {
    packagingOptions {
        pickFirst '**/libc++_shared.so'
        pickFirst '**/libfbjni.so'
    }
}
```

### ConsentActivity missing android:exported
```xml
<!-- REMOVE: -->
<activity android:name="com.buildbox.consent.ConsentActivity" android:theme="@style/Theme.AppCompat.Light.NoActionBar">
</activity>
<!-- ADD: -->
<activity android:name="com.buildbox.consent.ConsentActivity" android:theme="@style/Theme.AppCompat.Light.NoActionBar" android:exported="false">
</activity>
```

### Manifest Versioning to Gradle
```xml
<!-- REMOVE from AndroidManifest.xml <manifest> tag: -->
android:versionCode="1"
android:versionName="1.0"

<!-- ADD to app/build.gradle defaultConfig { }: -->
versionCode 1
versionName "1.0"
```

### Delete Legacy AIDL Directory
```bash
rm -rf app/src/main/aidl/
```

### Modern packagingOptions (AGP 8.x)
```gradle
android {
    packaging {
        resources {
            excludes += ['META-LOG/LICENSE.txt', 'META-INF/DEPENDENCIES']
        }
        jniLibs {
            useLegacyPackaging = false
            pickFirsts += ['**/libc++_shared.so', '**/libfbjni.so']
        }
    }
}
```

### Kotlin jvmTarget Match
```gradle
// project-level build.gradle — REMOVE:
jvmTarget = "11"
// ADD:
jvmTarget = "17"
```

### AdMob AdActivity Configuration *(most common crash-after-ad fix)*
```xml
<!-- Add/Update in AndroidManifest.xml under <application>: -->
<activity
    android:name="com.google.android.gms.ads.AdActivity"
    android:configChanges="keyboard|keyboardHidden|orientation|screenLayout|uiMode|screenSize|smallestScreenSize"
    android:theme="@android:style/Theme.Translucent"
    android:exported="false" />
```

### Suppress Unsupported CompileSDK Warning
```properties
android.suppressUnsupportedCompileSdk=36
```

### Deprecated ProgressDialog to Toast
```java
Toast.makeText(getContext(), "Restoring purchases...", Toast.LENGTH_SHORT).show();
```

---

## FIX OUTPUT — append to `./Reports/[GameName]/[GameName]_Report.md`

Add a `## 🛠️ Fix Results` section to the master report:

```markdown
## 🛠️ Fix Results
**Applied:** [date time]

| Status | Count |
|--------|-------|
| ✅ Applied | N |
| ⏭️ Skipped | N |
| ❌ Failed | N |

### Applied
- TASK-001 [Title] — [file] — [one-line change summary]

### Skipped
- TASK-002 [Title] — reason: [user reason]

### Failed
- TASK-003 [Title] — error: [message] — manual action needed: [what to do]

### ProGuard rules generated for detected SDKs
[list of SDK → rule blocks actually written]
```

Update `_internal/STATE.json`: `"scan": "PASS"`, `"fix": "PASS"` (or
`"PARTIAL"` if any task failed/was skipped — note which).

---

## AFTER EACH PROJECT

> `📦 [GameName]: [N] fixes applied, [N] skipped, [N] failed.`
> `Master report updated: ./Reports/[GameName]/[GameName]_Report.md`

## AFTER ALL PROJECTS ARE DONE

> `✅ GAMEBOX-SCAN-FIX complete across [M] selected projects.`
> `Run /gamebox-test-apk to re-verify and build a test APK for real-device testing.`

List any FAILED tasks directly in chat, grouped by project, with manual fix instructions.

---

## Next - Run /gamebox-test-apk to re-verify fixes and build a test APK.



