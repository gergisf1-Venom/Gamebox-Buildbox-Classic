---
name: gamebox-5-aab
description: Build a signed release AAB using the designated signing key after a real-device test pass.
---

# Release AAB

**Step 5 of 5.** The only release artifact is a signed `.aab`. Never create a release APK, upload an artifact, or perform a production rollout.

## Release gate

Require all of the following before changing version/signing/build configuration:

- Latest ENV and Scan/Fix reports have no unresolved critical blockers.
- `test_apk` is explicitly `PASS` from a physical device; an emulator pass is insufficient.
- Confirm the application ID and version match the intended Play app. Propose any version change and wait for approval.
- Current official Play requirements have been checked again if ENV is stale or requirements may have changed.

## Signing key

Use the designated private keystore locally. Keep key passwords out of command arguments, reports, chat, source control, and logs. Use a private local credential store or masked prompt supported by the environment. If a keystore already exists, ask **keep / replace / abort**; never overwrite it implicitly. Do not create a plaintext credential sidecar.

## Build and verify

From the Android project, run its wrapper's release bundle task (`gradlew.bat bundleRelease` on Windows or `./gradlew bundleRelease` on macOS). Confirm the expected `.aab` exists, verify its signature with the platform's `jarsigner -verify -verbose -certs`, and check bundled native libraries for current 16 KB compatibility when applicable. Do not produce or retain a release `.apk`.

Save the AAB under the selected project's `APK_AAB/[GameName]/` (or its existing output convention), report its path, signer verification result, package/version, and remaining Play Console steps. Do not include passwords, private key material, or raw credential output in the report. Do not upload the artifact or perform production rollout.
