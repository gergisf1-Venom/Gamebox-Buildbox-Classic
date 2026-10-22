---
name: gamebox-1-env
description: Collect reskin identity and ad/IAP identifiers, inspect a selected Android export and build machine, and verify live Google Play requirements before changes.
---

# Environment and App Information

**Step 1 of 5. Read-only.** This is for one selected, already-exported Android project. Do not ask for or require Buildbox or a `.bbdoc` file. Do not edit project files.

## 1. Collect app information

Collect these values together, allowing “not used” where applicable:

- Game title shown on the device.
- New Android application/package ID.
- Every AdMob app/ad-unit ID to use, grouped by placements supported by this project (for example banner, interstitial, rewarded, app-open). Do not invent placement types or IDs.
- Whether in-app purchases exist in the selected game. If yes, collect every product ID and its intended mapping/name. If no, record “no IAP”.
- Android project folder path, unless already supplied.

Do not request Google account passwords, keystore files, signing passwords, or secret API credentials in chat. Keep sensitive values local to the project.

## 2. Locate and identify the project

Find the Android project by `settings.gradle[.kts]`, `build.gradle[.kts]`, `gradlew`/`gradlew.bat`, and `AndroidManifest.xml`. If discovery is ambiguous, ask which project to use. Read the existing application ID, app label, supported ad integration points, and IAP product IDs. Report mismatches between discovered and supplied values. Do not inspect unrelated folders or other games.

If the folder is an APK only, an incomplete source export, or has no usable Gradle project, stop and explain what source files are missing.

## 3. Inspect machine and current Play requirements

Check available Java/JDK, Android SDK, platform/build tools, NDK when the project requires it, Git, and the project's Gradle wrapper. On Windows use the wrapper in the project (`gradlew.bat`); on macOS use `./gradlew` from the Android project. Do not install tools or alter machine settings in this step.

Before recommending requirements, search the web for the current official Google Play/Android developer documentation covering target API, Billing Library when IAP is present, native 16 KB page-size compatibility, and current policy rules relevant to reskinned/repetitive apps. Prefer official sources. Record source URLs and checked date, and distinguish confirmed requirements from inferred project risks. Do not rely on copied threshold tables in old protocol files.

## 4. Report and gate

Write `Reports/_ENV/ENV_report.md` in the selected project (create only the report folder/file). Include machine readiness, project identity, supplied values, discovered ad/IAP integrations, mismatches, live requirement sources/date, blockers, and the next step. Do not write signing credentials or unrelated secrets. Mask credential-like values found in files; note where a secret was found without reproducing it.

If a critical machine or requirement blocker exists, stop and explain it. Otherwise continue with `gamebox-2-update.md`. This report does not authorize project edits.
