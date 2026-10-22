---
name: gamebox-4-test-apk
description: Recheck and build a debug test APK from the selected Android project, then require a real-device test result.
---

# Test APK

**Step 4 of 5.** Requires a clean Scan and Fix gate. The APK is test-only and must never be uploaded to Play.

1. Confirm the selected project, application ID, and current ENV/scan reports. Stop if findings remain unresolved.
2. From the Android project directory, use its local wrapper: Windows `gradlew.bat tasks --all`, then `gradlew.bat clean assembleDebug`; macOS `./gradlew tasks --all`, then `./gradlew clean assembleDebug`. Do not run Gradle from the protocol/workspace root.
3. Confirm the debug APK exists and report its path and size. Keep it in the selected project's output folder.
4. Have the APK installed and exercised on a physical Android device, including launch, core gameplay, ads if present, and every IAP path if present. Record PASS/FAIL and device/OS. Emulator-only results do not pass this gate.
5. On failure, capture relevant diagnostics, return to Scan and Fix for an approved repair, then rebuild and repeat the real-device pass.

Update pipeline state to reflect the actual real-device result. Only after `PASS` continue with `gamebox-5-aab.md`.
