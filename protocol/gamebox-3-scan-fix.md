---
name: gamebox-3-scan-fix
description: Run a read-only policy and Android configuration audit on a selected reskinned game, then apply only approved fixes.
---

# Scan and Fix

**Step 3 of 5.** Requires successful ENV and Update steps. Inspect only the selected Android project.

## 1. Policy and differentiation gate

Review current official Play policy pages identified in ENV, the app description, title/package, assets and gameplay at a high level, and any related apps voluntarily provided for context. Assess whether this appears to be a minimally changed/repetitive app or uses third-party IP without rights. State uncertainty honestly. If there is a credible unresolved policy/IP blocker, stop before technical edits and explain what needs review. Do not claim that a technical pass guarantees Play approval.

## 2. Read-only technical scan

Check current live Play requirements from ENV, then inspect target/compile SDK, AGP and Gradle compatibility, Java/Kotlin level, manifest and permissions, package/namespace consistency, release/debug configuration, ProGuard/R8 rules, dependency health, AdMob setup, IAP product IDs and Billing Library (`billing` and `billing-ktx`), native `.so` ABIs and 16 KB alignment requirements. Check supplied AdMob and IAP values against every discovered location. Do not modify files during the scan. Do not copy or print credential values.

Write findings to `Reports/[GameName]/[GameName]_Report.md` and machine-readable scan data under `_internal/`. Label each issue by severity, evidence, affected file, recommended minimal fix, and any additional information required.

## 3. Approval-based fixes

Present fixes one at a time, with the exact file and proposed change. Wait for explicit approval for each fix. Apply only Android configuration/build/policy fixes that do not alter gameplay, assets, ad behavior, or purchase behavior. If a fix would alter those, stop and explain. Re-scan changed locations and update report/state after each approved fix. If blockers remain, do not proceed to APK build.

When there are no unresolved blockers, continue with `gamebox-4-test-apk.md`.
