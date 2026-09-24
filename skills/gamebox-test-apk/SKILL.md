---
name: gamebox-test-apk
description: Use when user invokes /gamebox-test-apk or asks to re-verify fixes and build an unsigned test APK for real-device testing with crash diagnosis.
---
> **Public version:** no hardcoded developer identity ships in this copy. Ask the user for organization name, contact email, and country code at the start of each run - never assume values.


# 🎮 GAMEBOX-TEST-APK — Post-Fix Verification & Unsigned Test APK
**GameBox V2.0 | Skill 3 of 5**
**Scope:** Every project that went through GAMEBOX-SCAN-FIX.
**Output:**
- `./Reports/[GameName]/[GameName]_Report.md` (appended — verification + test results)
- `./Reports/_DEBUG_ALL/DEBUG_ALL_summary.md` (consolidated verdicts across projects)
- `./APK_AAB/[GameName]/[GameName]-test.apk` (**unsigned** — for real-device
  testing only, never uploaded anywhere)
**Next:** GAMEBOX-AAB-PUBLISH

---

## PURPOSE

Re-scan every fixed project to confirm the repairs actually took, catch
anything new the fixes might have broken, then build an **unsigned test
APK** for the user to install on their own real devices — this is the
required test path — plus an optional emulator test. This is the step that
catches crashes *before* a signed release ever gets built, instead of only
finding out after a Play Store rejection.

**PHASE 1 (RE-VERIFY)** makes NO changes to any project files.
**PHASE 2 (BUILD & TEST)** builds the unsigned test APK and optionally
installs it on a device/emulator.

---

# ═══════════════════════════════════════════
# PHASE 1 — RE-VERIFY ALL FIXES
# ═══════════════════════════════════════════

## STEP 0 — VERIFY INPUT

For each project, confirm `./Reports/[GameName]/[GameName]_Report.md` has a
`## 🛠️ Fix Results` section and `_internal/STATE.json` shows `"fix"` is
`"PASS"` or `"PARTIAL"`. If missing → skip that project, note "not
processed" in the summary, don't block the others.

---

## RE-SCAN CHECKLIST (per project)

For each item, record:
✅ FIXED · ✅ OK · ❌ STILL FAILING · 🆕 NEW ISSUE · ⏭️ SKIPPED

### Build System
- [ ] `build.gradle` (project-level) exists
- [ ] `app/build.gradle` exists
- [ ] `settings.gradle` exists
- [ ] `gradle/wrapper/gradle-wrapper.properties` points to Gradle 8.7+
- [ ] `build.xml` (Ant) removed or replaced

### SDK Versions
- [ ] `compileSdk` 36+
- [ ] `targetSdk` 36+
- [ ] `minSdk` declared

### AGP
- [ ] AGP 8.5.1+
- [ ] Gradle wrapper compatible (8.7+)

### Namespace
- [ ] `namespace` field present in `app/build.gradle`

### Java Compatibility
- [ ] `sourceCompatibility` / `targetCompatibility` = `VERSION_17`

### AndroidX
- [ ] No `android.support.*` imports remain
- [ ] `android.useAndroidX=true` / `android.enableJetifier=true`

### AndroidManifest
- [ ] All `<activity>`/`<service>`/`<receiver>` have `android:exported`
- [ ] AdMob `AdActivity` has correct `configChanges` + `exported="false"`
      **if the project uses AdMob** (this is the #1 real-device crash cause)
- [ ] No new risky permissions introduced

### ProGuard Rules
- [ ] `proguard-rules.pro` exists
- [ ] Contains a keep-rule block for **every** ad SDK / billing SDK detected
      in GAMEBOX-SCAN-FIX section 17 — re-check the actual current file
      content against the actual current dependency list, not just against
      what was fixed last time (dependencies may have been re-exported
      differently)

### Native Libraries
- [ ] `arm64-v8a` present in `jniLibs/` or `libs/`
- [ ] `android.ndkVersion` declared and 27.x+

### Build Tools
- [ ] `buildToolsVersion` 36.x+

### Google Play Billing Library
- [ ] `com.android.billingclient:billing` 8.0.0+ (only if game has IAP)
- [ ] No removed-API references remain unaddressed

### 16 KB Memory Page Size
- [ ] `ndkVersion` 27.x+
- [ ] `packagingOptions.jniLibs.useLegacyPackaging` is `false`
- [ ] Every `.so` re-checked for 2**14 alignment

### Gradle Config Syntax
- [ ] No deprecated `compile` (must be `implementation`)
- [ ] No duplicate dependency declarations

---

## GRADLE CONFIGURATION VALIDATION (per project)

```bash
./gradlew tasks --all
```
Record ✅ Configuration successful or ❌ Configuration failed (capture full error).

**Common error diagnosis:**

| Error contains | Cause | Fix |
|---|---|---|
| `Namespace not specified` | namespace missing | Add namespace to build.gradle |
| `android:exported` | manifest attribute missing | Add exported to AndroidManifest |
| `No version of NDK` | ndkVersion mismatch | Adjust ndkVersion |
| `Duplicate class` | AndroidX conflict | Enable Jetifier |
| `Could not resolve` | dependency version | Update dependency |
| `Unsupported class file` | Java version mismatch | Fix compileOptions |
| `BillingClient` method not found | Billing Library below 8.0.0 | Update, review call sites |
| `align 2**12` on any `.so` | Not 16 KB compliant | Update NDK/dependency |

---

## READINESS VERDICT (per project)

### 🟢 READY TO TEST
All CRITICAL and HIGH issues resolved.

### 🟡 PROCEED WITH CAUTION
All CRITICAL resolved, some HIGH/MEDIUM remain.

### 🔴 NOT READY
One or more CRITICAL issues remain. Direct back to GAMEBOX-SCAN-FIX.

Only continue to Phase 2 with 🟢 or 🟡 projects.

---

# ═══════════════════════════════════════════
# PHASE 2 — BUILD UNSIGNED TEST APK & TEST
# ═══════════════════════════════════════════

## PRE-BUILD VERIFICATION

Confirm in `app/build.gradle`:
- [ ] `compileSdk 36`+, `targetSdk 36`+
- [ ] `namespace` field present
- [ ] `compileOptions` Java 17
- [ ] `buildToolsVersion "36.x.x"`+
- [ ] `ndkVersion` 27.x+
- [ ] `packagingOptions.jniLibs.useLegacyPackaging = false`
- [ ] `com.android.billingclient:billing` 8.0.0+ (only if IAP)

If any missing → stop and report which item needs fixing.

---

## BUILD STEPS

### Step 1 — Clean
```bash
cd [project_path]
./gradlew clean
```

### Step 2 — Build unsigned debug-mode test APK
```bash
./gradlew assembleDebug
```
Expected: `BUILD SUCCESSFUL in Xs`
Expected APK: `app/build/outputs/apk/debug/app-debug.apk`

> Note: this is a debug-variant build (unsigned, `minifyEnabled=false`), so
> it is a good first sanity check but does **not** exercise R8/ProGuard the
> way the real release build will. Treat a clean pass here as necessary,
> not sufficient — GAMEBOX-AAB-PUBLISH (skill 4) does its own release-mode
> device test for exactly this reason.

### Step 3 — Verify APK exists
```bash
ls -lh app/build/outputs/apk/debug/
```
Confirm `app-debug.apk` exists and is **larger than 1 MB**.

### Step 4 — Inspect APK contents
```bash
aapt dump badging app/build/outputs/apk/debug/app-debug.apk
```
Verify correct package name, version code/name, `native-code: 'arm64-v8a'`.

### Step 4b — Verify 16 KB page size alignment
```bash
unzip -o app/build/outputs/apk/debug/app-debug.apk -d /tmp/apk_check "lib/*"
for f in $(find /tmp/apk_check/lib -name "*.so"); do
  echo "$f:"
  objdump -p "$f" | grep LOAD
done
```
Every `LOAD` segment should show `align 2**14` or higher. Flag any at
`align 2**12`.

### Step 5 — Copy to APK_AAB folder
```bash
mkdir -p ./APK_AAB/[GameName]
cp app/build/outputs/apk/debug/app-debug.apk ./APK_AAB/[GameName]/[GameName]-test.apk
ls -lh ./APK_AAB/[GameName]/
```

---

## STEP 6 — TESTING (real device required, emulator optional)

### Real device (required test path)
Ask the user to connect their physical device and confirm it's detected:
```bash
adb devices
```
Then:
```bash
adb install -r ./APK_AAB/[GameName]/[GameName]-test.apk
adb shell am start -n [packageName]/[launcherActivity]
```
Ask the user to actually play for a bit — launch, basic gameplay, trigger
an ad if the game has ads (interstitial/rewarded), background/resume the
app. This is the scenario that most often reveals crashes that a simple
launch-and-close test misses.

### Ads policy compliance check (if the game has ads)

This is separate from crash-testing — it's checking for **behavior** that
can trigger Ads policy violations regardless of code stability:

- [ ] Ads never cover navigation buttons, system UI, or the close/back
      button of another ad (accidental-click risk)
- [ ] Every interstitial/rewarded ad has a clearly visible, working close
      button that appears within a reasonable time
- [ ] Ads don't launch immediately on app open before any real content is
      shown (this reads as disruptive/deceptive placement)
- [ ] No ad mimics system notifications or device UI
- [ ] Rewarded ad rewards are only granted after the ad is actually
      watched, not on click/skip

Record results in the master report — a fail here is a real Play Store
rejection/suspension risk (Ads policy) independent of any crash.

### Emulator (optional, only if the user wants it)
If an AVD was set up in GAMEBOX-ENV:
```bash
$ANDROID_HOME/emulator/emulator -avd GameBox_Test -no-snapshot &
adb wait-for-device
adb install -r ./APK_AAB/[GameName]/[GameName]-test.apk
adb shell am start -n [packageName]/[launcherActivity]
```

---

## CRASH DIAGNOSIS PROTOCOL

If the app crashes during testing (device or emulator), follow these steps
**in order** before asking the user for more info:

### Step 1 — Capture crash log
```bash
adb logcat --pid=$(adb shell pidof [packageName]) -d *:E
```
If `pidof` returns empty (app already dead):
```bash
adb logcat -d | grep -A 20 "FATAL EXCEPTION"
```

### Step 2 — Identify crash type

| Crash pattern | Likely cause | Fix |
|---|---|---|
| `java.lang.UnsatisfiedLinkError` | Missing native `.so` for this ABI | Check `jniLibs/` for `arm64-v8a` |
| `java.lang.ClassNotFoundException: com.buildbox.*` | ProGuard stripping Buildbox classes | Add/verify keep rules |
| `java.lang.ClassNotFoundException` for an ad SDK class | Missing keep rule for that SDK | Return to GAMEBOX-SCAN-FIX PHASE 2a, regenerate ProGuard rules |
| `java.lang.NullPointerException` in ad SDK | Ad not loaded before display attempted | Ad SDK timing issue (not fixable in Buildbox export) |
| `android.view.WindowManager$BadTokenException` | Activity destroyed before ad shown | Check ProGuard rules + AdActivity manifest entry |
| `Fatal signal 11 (SIGSEGV)` | Native crash in `.so` library | Check 16 KB alignment, NDK version |
| Crash after watching rewarded video | Ad SDK callback on destroyed activity | Ensure `AdActivity` has `android:configChanges` in manifest |
| `java.lang.NoSuchMethodError: com.android.billingclient.*` | Billing Library API mismatch | Update to 8.0.0+, review call sites |

### Step 3 — If crash is ad-related
Check `AndroidManifest.xml` for:
```xml
<activity
    android:name="com.google.android.gms.ads.AdActivity"
    android:configChanges="keyboard|keyboardHidden|orientation|screenLayout|uiMode|screenSize|smallestScreenSize"
    android:theme="@android:style/Theme.Translucent"
    android:exported="false" />
```
If missing, this is the single most common cause of post-ad crashes in
Buildbox games — add it and re-test.

### Step 4 — Re-test after fix
1. `./gradlew clean assembleDebug`
2. `adb install -r [new apk]`
3. Re-launch and re-test the same scenario
4. Capture logcat again to confirm resolution

---

## FAILURE DIAGNOSIS (build errors)

| Error contains | Cause | Fix |
|---|---|---|
| `Namespace not specified` | namespace missing | Add namespace to build.gradle |
| `android:exported` | manifest attribute | Add exported attr |
| `No version of NDK` | NDK mismatch | Fix ndkVersion |
| `Duplicate class` | AndroidX conflict | Enable Jetifier |
| `Could not resolve` | Dependency version | Update dependency |
| `Unsupported class file major version` | Java version | Fix compileOptions |
| `Resource linking failed` | Malformed XML in res/ | Check res/ for broken XML |
| `More than one file was found` | Duplicate .so file | Add packagingOptions exclusion |
| Any `.so` shows `align 2**12` | Not 16 KB aligned | Update NDK/dependency |
| Billing-related `NoSuchMethodError` | Billing Library < 8.0.0 | Update, review call sites |

**Duplicate .so fix:**
```gradle
android {
    packagingOptions {
        pickFirst '**/libc++_shared.so'
        pickFirst '**/libfbjni.so'
    }
}
```

For any error not in the table: show full error, propose a fix, wait for approval, then re-run from Step 1.

---

## OUTPUT — append to `./Reports/[GameName]/[GameName]_Report.md`

```markdown
## 🔁 Re-Verification & Test APK
**Generated:** [date time]

### Fix Verification

| Check | Before | After | Status |
|-------|--------|-------|--------|
| targetSdk | 23 | 36 | ✅ FIXED |
| ProGuard: AdMob rule | Missing | Present | ✅ FIXED |
| 16 KB alignment | Failing | Passing | ✅ FIXED |

### Gradle Configuration Check
**Result:** ✅ Configuration successful / ❌ Failed

### Test APK
| Field | Value |
|-------|-------|
| File | `./APK_AAB/[GameName]/[GameName]-test.apk` |
| Size | 28.4 MB |
| Package | com.yourorg.gamename |
| Version | 1.0 (code: 1) |
| Native ABIs | arm64-v8a, armeabi-v7a |
| 16 KB alignment | ✅ ALL LIBS ALIGNED |

### Real-Device Test Results
| Test | Result |
|------|--------|
| App launches | ✅ / ❌ |
| Basic gameplay | ✅ / ❌ / ⏭️ Not tested |
| Ad display | ✅ / ❌ / ⏭️ Not tested / N/A (no ads) |
| Post-ad stability | ✅ / ❌ / ⏭️ Not tested / N/A |
| Ads policy compliance (placement/accidental-click/close button) | ✅ / ❌ / ⏭️ Not tested / N/A |

### Emulator Test Results (optional)
| Test | Result |
|------|--------|
| App launches | ✅ / ❌ / ⏭️ Skipped |

### New Issues Detected
[Any new problems introduced during the fix phase]

### 🏁 Readiness Verdict
🟢 READY FOR RELEASE BUILD / 🟡 PROCEED WITH CAUTION / 🔴 NOT READY
```

Update `_internal/STATE.json`: `"test_apk": "PASS"` (or `"FAILED"` with note).

## OUTPUT — consolidated: `./Reports/_DEBUG_ALL/DEBUG_ALL_summary.md`

```markdown
# 🎮 GAMEBOX-TEST-APK Summary
**Projects checked:** N
**Generated:** [date time]

| Project | Verdict | Critical Remaining | Real-Device Tested |
|---------|---------|--------------------|---------------------|
| [GameName1] | 🟢 READY | 0 | ✅ Yes |
| [GameName2] | 🔴 NOT READY | 2 | ⏭️ Not yet |

## ✅ Next Step
🟢 projects → GAMEBOX-AAB-PUBLISH
🔴 projects → back to GAMEBOX-SCAN-FIX
```

---

## AFTER WRITING THE REPORTS

> `🟢 [GameName1]: verified on real device, ready for release build.`
> `🔴 [GameName2]: 2 critical issues remain — return to GAMEBOX-SCAN-FIX.`
> `Test APK: ./APK_AAB/[GameName]/[GameName]-test.apk`
> `Summary: ./Reports/_DEBUG_ALL/DEBUG_ALL_summary.md`

---

## Next - Green projects go to /gamebox-aab-publish. Red projects go back to /gamebox-scan-fix.



