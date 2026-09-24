---
name: gamebox-update
description: Use when user invokes /gamebox-update or asks to refresh a Buildbox Android project after a .bbdoc/re-export - reuse prior reports, scan changed/high-risk files first, fix them, then run a full Play/policy audit.
---
> **Public version:** no hardcoded developer identity ships in this copy. Ask the user for organization name, contact email, and country code at the start of each run - never assume values.


# 🎮 GAMEBOX-UPDATE — Re-export Delta Scan, Fix, and Full Audit
**GameBox V2.0 | Skill 6 of 6**
**Scope:** Previously processed Android projects with a new or changed Buildbox export.
**Output:**
- `./Reports/[GameName]/[GameName]_Report.md` (appended — update/delta/full-audit sections)
- `./Reports/[GameName]/_internal/UPDATE_data.json` (machine-readable delta + audit state)
- `./Reports/[GameName]/_internal/EXPORT_BASELINE.json` (file fingerprint baseline for the current export)
- `./Reports/_UPDATE_ALL/UPDATE_ALL_summary.md` (consolidated update verdicts across selected projects)
- `./Reports/[GameName]/_internal/STATE.json` (adds/updates `"update"`)
**Next:** `/gamebox-test-apk`

---

## PURPOSE

When a `.bbdoc` changes and produces a new Android export, do not blindly rescan everything from zero. Read the existing report/state first, inspect changed and previously risky files first, fix those with approval, then run a full current Google Play and policy audit.

**PHASE 1 (DELTA)** scans and fixes changed/high-risk files only.
**PHASE 2 (FULL AUDIT)** rechecks the whole current export against live Play requirements and policies.
**PHASE 1 makes NO project changes until the user approves fixes.**
**PHASE 2 makes NO project changes until the user approves the newly found issues.**

---

## INPUT REQUIRED

Ask for, in this order:

1. New Android export path, or the parent folder containing it.
2. Prior reports location, if it is not the normal `./Reports/` folder.
3. Optional `.bbdoc` filename/version associated with the new export.

---

## STEP 0 — ROUTE CORRECTLY

- If the selected project has a prior master report, `SCAN_data.txt`, or `STATE.json`, continue below.
- If it has no prior report/state, stop update handling for that project and route it to `/gamebox-scan-fix`. Do not invent prior history.
- If the prior report exists but the package/game identity changed materially, record old/new identity and confirm with the user before continuing.

---

## STEP 1 — DISCOVER AND SELECT

Use the same discovery/selection behavior as `/gamebox-scan-fix`:

1. Ask for the export/parent folder unless already provided.
2. Auto-detect Android projects using `build.gradle`, `settings.gradle`, or `AndroidManifest.xml`.
3. Show `Found N Android projects:` with game/app name, package when known, project path, and prior report/state when available.
4. Use the `question` tool with `multiple: true`. Allow one, multiple, or all projects.
5. Do not inspect, initialize, modify, or report on unselected projects.

---

## STEP 2 — LOAD PRIOR HISTORY

For each selected project:

1. Match it to exactly one prior master report using, in order:
   - package name from `applicationId`/manifest;
   - game name from `strings.xml`;
   - project path recorded in `STATE.json` or the master report.
2. Load:
   - latest `## 🔍 Scan Results`;
   - latest `## 🛠️ Fix Results`;
   - `STATE.json`;
   - `SCAN_data.txt`;
   - detected ad SDK, billing, product-ID, permission, and `.so` lists.
3. Record the export identity:
   - `.bbdoc` filename/version when supplied;
   - new Android project path;
   - current package/version;
   - update date/time.
4. Ask whether the game, account, store listing, ads, IAP, permissions, or ownership changed since the prior run. Changed answers require refreshed policy handling.

---

## STEP 3 — DELTA DETECTION

Compare the new export against `EXPORT_BASELINE.json` when present:

```json
{
  "project": "[GameName]",
  "package": "[packageName]",
  "bbdoc": "[filename/version or 'not supplied']",
  "android_project_path": "[path]",
  "captured_at": "[date time]",
  "files": [
    {
      "path": "app/build.gradle",
      "size": 12345,
      "mtime": "[timestamp]",
      "sha256": "[hash]"
    }
  ]
}
```

Include all project configuration/source/resource files needed for compliance, but exclude generated outputs such as:

- `**/build/**`
- `**/.gradle/**`
- `local.properties`
- `*.log`
- report/output folders inside the scanned export, if any

Classify the current export as:

- `ADDED`
- `CHANGED`
- `REMOVED`
- `PREVIOUSLY FLAGGED`
- `UNCHANGED`

Always include previously flagged paths in the first-pass scope, even when their hashes did not change, because a Buildbox re-export can silently overwrite prior fixes.

If no baseline exists:

1. Use every file/path cited in the previous scan/fix report as the first-pass scope.
2. Add mandatory high-risk files: project/app `build.gradle`, `settings.gradle`, wrapper properties, `gradle.properties`, manifest(s), ProGuard files, AIDL directories, `jniLibs/`/`libs/`, and dependency declarations.
3. Create the baseline during finalization after the approved fixes are applied.

---

## STEP 4 — DELTA SCAN AND FIX

For each selected project:

1. Re-run only the scan checks relevant to the delta/high-risk file set.
2. Present delta tasks in `TASK-NNN` format with severity, file, before/after diff, and reason.
3. Ask apply mode for this project:
   - **One by one** *(recommended)*
   - **All at once**
4. Apply only approved changes.
5. Use the same safety rules as `/gamebox-scan-fix`:
   - Never modify gameplay, assets, levels, audio, ad/monetization behavior, or purchase logic.
   - Only modify build/configuration/manifest/ProGuard packaging files.
   - If a delta issue requires source/gameplay changes, record it as manual work for the `.bbdoc` or developer; do not rewrite game logic.
6. Update `UPDATE_data.json` with applied/skipped/failed delta tasks.

---

## STEP 5 — FULL CURRENT AUDIT

After delta fixes, run a full audit of the current export:

1. Live-check current Google Play technical requirements:
   - target/compile SDK;
   - Play Billing Library;
   - 16 KB page-size/native-library requirements.
2. Live-check current content-policy enforcement:
   - Spam/Minimum Functionality;
   - Repetitive Content;
   - Intellectual Property;
   - Ads/data-safety behavior when relevant.
3. Re-run the full `/gamebox-scan-fix` scan areas against the current export.
4. Separately report:
   - ✅ still fixed;
   - ❌ regressed by the re-export;
   - 🆕 newly introduced;
   - ⏭️ previously skipped and still present.
5. Present any new/regressed tasks and ask for approval before applying fixes.
6. Do not mark the project ready if unresolved 🔴 CRITICAL issues remain.

---

## STEP 6 — FINALIZE REPORTS, BASELINE, AND STATE

Append to `./Reports/[GameName]/[GameName]_Report.md`:

```markdown
## 🔄 Re-export Update
**Updated:** [date time]
**Export source:** [.bbdoc filename/version or "not supplied"]
**Project path:** [current path]

### Prior history used
- Master report: [path]
- Previous scan/fix state: [PASS/PARTIAL]
- Baseline present: Yes/No

### Changed files checked first
- ADDED: [paths]
- CHANGED: [paths]
- REMOVED: [paths]
- PREVIOUSLY FLAGGED: [paths]

### Delta fixes
| Status | Count |
|--------|-------|
| ✅ Applied | N |
| ⏭️ Skipped | N |
| ❌ Failed | N |

### Full current audit
| Result | Count |
|--------|-------|
| ✅ Still fixed | N |
| ❌ Regressed | N |
| 🆕 New | N |
| ⏭️ Still skipped | N |

### 🏁 Update verdict
🟢 READY FOR TEST / 🟡 PROCEED WITH CAUTION / 🔴 NOT READY
```

Also:

1. Write/update `UPDATE_data.json`.
2. Recreate `EXPORT_BASELINE.json` from the fixed current export.
3. Update `STATE.json` with `"update": "PASS"` or `"update": "PARTIAL"`.
4. For multiple projects, append the verdict to `./Reports/_UPDATE_ALL/UPDATE_ALL_summary.md`.
5. List every unresolved 🔴 CRITICAL issue directly in chat, grouped by project.

---

## AFTER ALL SELECTED PROJECTS

> `✅ GAMEBOX-UPDATE complete across [M] selected projects.`
> `Run /gamebox-test-apk to re-verify the updated export on a real device.`

---

## Next - Run /gamebox-test-apk to re-verify the updated export and build a test APK.
