---
description: Refresh a Buildbox export from prior reports - delta-scan changed files, fix, then full audit
---

Follow the `gamebox-update` skill exactly: match the new export to its prior report/state, scan changed and previously risky files first, fix with approval, then run a full current Play/policy audit. Ask the user for the export path, prior reports location if nonstandard, and optional .bbdoc version each time.

Extra context from user: $ARGUMENTS
