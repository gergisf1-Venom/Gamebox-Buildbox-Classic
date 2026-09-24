# Gamebox Play Assets Tool (generic — any game)

Nano Banana first, exact sizes enforced after. Pure upscaling is NOT a
deliverable — every client-ready file starts as fresh AI art at the right
aspect, then Pillow guarantees the exact Play pixels.

## Backends

- **higgsfield** (works now) — Nano Banana Pro via your Higgsfield account
  credits (~2 credits/image). One-time: `npm i -g @higgsfield/cli`,
  `higgsfield auth login`, `npx skills add higgsfield-ai/skills`.
- **gemini** — Nano Banana Pro via `GEMINI_API_KEY` (needs a billing-enabled
  Cloud project; free-tier keys get quota 0).

## 1. Install

```bash
pip install -r tools/play-assets/requirements.txt
```

Put the Gemini key in `tools/play-assets/.env` (`GEMINI_API_KEY=...`) or the
env var (gemini backend only). Never commit it.

## 2. Interactive (recommended — asks everything, checks cost first)

```bash
python tools/play-assets/make_play_assets.py
```

It asks for the reference folder (must exist, must contain images), how many
phone shots, feature graphics and icons, game name, output folder, and backend
(higgsfield/gemini) — then checks key/credits BEFORE spending anything,
generates with Nano Banana Pro with the exact target size written in every
prompt (1080x1920, 1024x500, 512x512), and enforces exact sizes into `PlayFinal/`.
Each generated kind maps only to its correct targets (phone art never becomes
an icon, etc.).

## 3. Non-interactive Higgsfield (same pipeline, explicit flags)

```powershell
python tools/play-assets/higgsfield_backend.py --game "Shape Switch" --refs "working on/9-Shape Switch/SHAPE SWITCH/5-Online Listing/*.png" --phones 2 --features 1 --icons 1 --out tools/play-assets/gen_raw --playfinal "working on/9-Shape Switch/SHAPE SWITCH/5-Online Listing/PlayFinal"
```

Add `--dry-run` to print plan + cost only. Re-run sizes without spending:
`--from-raw <gen_raw folder> --playfinal <PlayFinal>`.

## 4. Non-interactive Gemini backend

```bash
python tools/play-assets/make_play_assets.py
```

It asks for the reference folder (must exist, must contain images), how many
phone shots (default 6), feature graphics (1) and icons (1), game name and
output folder — then validates `GEMINI_API_KEY` (cheap check, nothing spent),
generates with Nano Banana Pro with the exact target size written in every
prompt (1080x1920, 1024x500, 512x512), and enforces exact sizes into `PlayFinal/`.
If the key/quota is bad it stops BEFORE spending anything, with the fix printed.

## 3. Non-interactive Higgsfield (same pipeline, explicit flags)

```powershell
python tools/play-assets/generate_play_assets.py --game "Shape Switch" --refs "working on/9-Shape Switch/SHAPE SWITCH/5-Online Listing/*.png" --phones 6 --features 1 --icons 1 --out tools/play-assets/gen_raw --dry-run
python tools/play-assets/generate_play_assets.py --game "Shape Switch" --refs "working on/9-Shape Switch/SHAPE SWITCH/5-Online Listing/*.png" --phones 6 --features 1 --icons 1 --out tools/play-assets/gen_raw
python tools/play-assets/enforce_play_sizes.py --in tools/play-assets/gen_raw/ShapeSwitch --out "working on/9-Shape Switch/SHAPE SWITCH/5-Online Listing/PlayFinal" --which all
```

`enforce_play_sizes.py` alone is a repair/verify utility only — never ship its
upscaled output to a client as final art.

Outputs per target: `phone_portrait` 1080x1920, `phone_landscape` 1920x1080,
`tablet_7` 1200x1920, `tablet_10` 1600x2560, `feature` 1024x500 exact,
`icon` 512x512 exact.
