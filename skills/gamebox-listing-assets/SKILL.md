---
name: gamebox-listing-assets
description: Use when user invokes /gamebox-listing-assets or asks to generate Play Store graphics - phone screenshots, feature graphic, icon via tools/play-assets.
---
> **Public version:** no hardcoded developer identity ships in this copy. Ask the user for organization name, contact email, and country code at the start of each run - never assume values.


# 🎮 GAMEBOX-LISTING-ASSETS — Play Store Graphics (generic tool)
**GameBox V2.0 | Skill 5 of 6**
**Scope:** Any game. Called from GAMEBOX-AAB-PUBLISH Phase 4 when screenshots / feature graphic / icon are needed.
**Tool:** `./tools/play-assets/` (generic — asks for the game at runtime)
**Key:** `GEMINI_API_KEY` env var or `tools/play-assets/.env`. Never committed, never pasted into reports.

---

## WHEN TO CALL

SKILL_04 needs: 2–8 phone shots, 1024×500 feature (exact), 512×512 icon.
If the game's `5-Online Listing/` shots are missing, undersized (e.g. 640×1136),
or not featuring-eligible, call this skill instead of hand-editing images.
Never ship pure-upscaled art to a client — always generate first, then enforce.

## INTERACTIVE (default) — asks refs, counts, validates key, generates, enforces

```bash
pip install -r tools/play-assets/requirements.txt
python tools/play-assets/make_play_assets.py
```

It asks: reference folder (validated: exists + contains images), phone count
(default 6), feature count (1), icon count (1), game name, output folder.
Then it validates the key with a free check BEFORE spending anything, generates
with Nano Banana Pro (`gemini-3-pro-image`, exact target size stated in every
prompt: 1080x1920 / 1024x500 / 512x512), and enforces exact pixels into
`<game>/PlayFinal/`. Bad key or zero quota stops the run with the fix printed.

## NON-INTERACTIVE

Higgsfield backend (works now, ~2 credits/image):
```powershell
python tools/play-assets/higgsfield_backend.py --game "<Game>" --refs "<refs>/*.png" --phones 2 --features 1 --icons 1 --out tools/play-assets/gen_raw --playfinal "<game>/PlayFinal"
```

Gemini backend (needs billing-enabled key):
```powershell
python tools/play-assets/generate_play_assets.py --game "<Game>" --refs "<refs>/*.png" --phones 6 --features 1 --icons 1 --out tools/play-assets/gen_raw
python tools/play-assets/enforce_play_sizes.py --in tools/play-assets/gen_raw/<Game> --out "<game>/PlayFinal" --which all
```

`enforce_play_sizes.py` alone is repair/verify only.

## OUTPUT

`<game>/PlayFinal/phone_portrait/` (1080×1920), `tablet_7/`, `tablet_10/`,
`feature/` (1024×500 exact), `icon/` (512×512 exact) + console OK/WARN per file.
Upload `PlayFinal` contents in SKILL_04 Screens 1–2.
Record the folder path in `./Reports/[GameName]/[GameName]_Report.md`.

---

## Next - Upload PlayFinal contents in /gamebox-aab-publish Screens 1-2. Record the folder path in the master report.



