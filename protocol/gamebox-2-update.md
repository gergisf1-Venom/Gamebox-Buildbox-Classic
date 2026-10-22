---
name: gamebox-2-update
description: Apply confirmed reskin identity, AdMob IDs, and existing IAP product IDs to a selected Android project after presenting exact proposed changes.
---

# Application Update

**Step 2 of 5.** Requires a completed `Reports/_ENV/ENV_report.md`. Work only in the selected Android project. Buildbox and `.bbdoc` files are not required.

## 1. Validate scope and inputs

Read the ENV report and re-check current project values. Request any missing app information. Detect every relevant occurrence of the app label, application ID/namespace, AdMob IDs, and IAP product IDs in the project. Check both `billing` and `billing-ktx` dependencies when IAP is present. Never assume an integration or placement the project does not contain.

## 2. Propose exact edits

Show a table of file, current value, proposed value, and reason. Include package/namespace/manifest references and all detected ad/IAP ID locations. Flag edits that may affect Firebase configuration, deep links, OAuth, service files, or external dashboards; do not silently change them. Avoid broad search-and-replace. Do not change gameplay, assets, ad display/frequency behavior, purchase flow, or purchase logic.

Present the complete proposed change set and wait for explicit approval. Without approval, make no edits. If the package rename is too broad or cannot be traced safely, stop and explain manual steps instead of guessing.

## 3. Apply and report

After explicit approval, make only the listed substitutions. Preserve file encoding and unrelated content. Re-read each changed location and summarize actual edits in `Reports/[GameName]/_internal/UPDATE_data.json` (create report directories as needed). Store no signing secrets. Record unresolved external-console tasks separately. Continue with `gamebox-3-scan-fix.md`.
