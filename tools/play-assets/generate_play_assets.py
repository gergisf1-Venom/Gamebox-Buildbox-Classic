"""Generate fresh listing assets with Nano Banana Pro, then enforce exact Play sizes separately.

Generic Gamebox tool — works for ANY game via --game / --refs. API key comes
only from the GEMINI_API_KEY environment variable (or tools/play-assets/.env),
never from argv.

  pip install -r requirements.txt
  python generate_play_assets.py --game "Shape Switch" --refs "path/to/refs/*.png" --phones 6 --features 1 --icons 1 --out gen_raw
  python enforce_play_sizes.py --in gen_raw/"Shape Switch" --out "<game>/PlayFinal" --which all

Model: gemini-3-pro-image (Nano Banana Pro). Every prompt states the exact
target size (1080x1920, 1024x500, 512x512); the model returns high-res art at
the right aspect, and enforce_play_sizes.py then guarantees the exact store
pixels Play Console enforces.
"""
from __future__ import annotations

import argparse
import base64
import glob
import os
import sys
from pathlib import Path

PHONE_PROMPT = (
    "Recreate this mobile game screenshot as a crisp high-resolution portrait "
    "gameplay image for game '{game}'. Target size 1080x1920 pixels, exact 9:16 "
    "portrait. Keep the same game (colors, shapes, UI style), show real gameplay "
    "only, no phone frame, no watermark, no extra text. Vertical composition "
    "with the key action centered. Moment {n}: {moment}."
)
FEATURE_PROMPT = (
    "Create a wide feature-graphic background for mobile game '{game}'. Target "
    "size exactly 1024x500 pixels (wide banner, ratio 2.048:1). Vibrant gameplay "
    "theme, empty center safe-area for title text, no text, no logo, no watermark."
)
ICON_PROMPT = (
    "Create a square mobile game icon for '{game}'. Target size exactly 512x512 "
    "pixels, 1:1 square. Single bold shape-switch motif on a vivid background, "
    "flat vector style, centered, no text, no watermark."
)

PHONE_MOMENTS = [
    "core gameplay loop, mid-action",
    "best power-up / combo moment",
    "new level or environment variant",
    "high-score / victory moment",
    "second gameplay mode or obstacle type",
    "close-up of the main character mechanic",
    "bonus round or special effect showcase",
    "early-game tutorial-style clear shot",
]


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line and "GEMINI_API_KEY" in line:
            _, _, val = line.partition("=")
            os.environ.setdefault("GEMINI_API_KEY", val.strip().strip("\"'"))


def validate_key(client) -> tuple[bool, str]:
    """Cheap key/quota check before spending generation calls.

    Returns (ok, message). Uses models.list (no generation quota consumed).
    """
    try:
        next(iter(client.models.list()), None)
    except AttributeError:
        return True, "Key present (validation skipped: SDK has no models.list)."
    except Exception as exc:
        msg = str(exc)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
            return False, (
                "Key is set but the project has NO image-generation quota "
                "(free-tier limit 0). Enable billing on the Google Cloud project "
                "behind this key, then re-run."
            )
        if "401" in msg or "403" in msg or "API key" in msg or "API_KEY" in msg:
            return False, f"Key rejected by Google API: {exc}"
        return False, f"Key validation failed: {exc}"
    return True, "Key valid."


def is_quota_error(exc: Exception) -> bool:
    msg = str(exc)
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Generate Play assets with Nano Banana Pro (generic).")
    ap.add_argument("--game", required=True, help="Game name, e.g. 'Shape Switch'. Used in prompts + output subfolder.")
    ap.add_argument("--refs", default="", help="Glob of reference screenshots, e.g. 'path/*.png'. Strongly recommended.")
    ap.add_argument("--phones", type=int, default=6, help="Phone screenshots to generate (0-8, default 6).")
    ap.add_argument("--count", type=int, default=None, help="Deprecated alias for --phones.")
    ap.add_argument("--features", type=int, default=1, help="Feature-graphic bases to generate (0-2, default 1).")
    ap.add_argument("--icons", type=int, default=1, help="Icon bases to generate (0-2, default 1).")
    ap.add_argument("--model", default="gemini-3-pro-image", help="Image model (default Nano Banana Pro).")
    ap.add_argument("--aspect", default="9:16", help="Phone aspect (default 9:16).")
    ap.add_argument("--size", default="2K", help="Output resolution 1K/2K/4K (default 2K).")
    ap.add_argument("--out", default="gen_raw", help="Raw output root folder.")
    ap.add_argument("--also-feature", action="store_true", help="Shortcut for --features 1.")
    ap.add_argument("--also-icon", action="store_true", help="Shortcut for --icons 1.")
    ap.add_argument("--dry-run", action="store_true", help="Print plan without calling the API (no key needed).")
    ap.add_argument("--no-validate", action="store_true", help="Skip key validation (caller already validated).")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv(Path(__file__).with_name(".env"))

    phones = args.count if args.count is not None else args.phones
    features = 1 if args.also_feature else args.features
    icons = 1 if args.also_icon else args.icons

    refs = sorted(glob.glob(args.refs)) if args.refs else []
    out_dir = Path(args.out) / args.game
    plan = {
        "game": args.game, "model": args.model, "aspect": args.aspect,
        "size": args.size, "phones": phones, "features": features,
        "icons": icons, "ref_count": len(refs), "out": str(out_dir),
    }
    if args.dry_run:
        print(f"DRY-RUN {plan}")
        print("Refs: " + ("\n  ".join(refs) if refs else "(none — generation works far better WITH refs)"))
        print("No API call made. Set GEMINI_API_KEY and re-run without --dry-run to generate.")
        return 0

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("GEMINI_API_KEY is not set (env var or tools/play-assets/.env).", file=sys.stderr)
        return 2
    if not 0 <= phones <= 8:
        print("--phones must be 0-8.", file=sys.stderr)
        return 2
    if not refs:
        print("WARNING: no --refs matched. Results will drift from the real game — add refs if you can.",
              file=sys.stderr)

    try:
        from google import genai  # type: ignore
    except ImportError:
        print("Missing dependency: pip install -r requirements.txt", file=sys.stderr)
        return 2

    client = genai.Client(api_key=api_key)
    if not args.no_validate:
        ok, msg = validate_key(client)
        print(msg)
        if not ok:
            return 4

    out_dir.mkdir(parents=True, exist_ok=True)
    ref_parts: list = []
    for r in refs[:6]:
        data = Path(r).read_bytes()
        ref_parts.append({"inline_data": {"mime_type": "image/png", "data": base64.b64encode(data).decode()}})

    jobs: list[tuple[str, str, str]] = []
    for i in range(phones):
        moment = PHONE_MOMENTS[i % len(PHONE_MOMENTS)]
        jobs.append(("phone", PHONE_PROMPT.format(game=args.game, n=i + 1, moment=moment), args.aspect))
    for _ in range(features):
        jobs.append(("feature", FEATURE_PROMPT.format(game=args.game), "16:9"))
    for _ in range(icons):
        jobs.append(("icon", ICON_PROMPT.format(game=args.game), "1:1"))
    if not jobs:
        print("Nothing to generate (all counts are 0).", file=sys.stderr)
        return 2

    idx = 0
    for kind, prompt, aspect in jobs:
        contents: list = [{"text": f"{prompt} Aspect {aspect}, resolution {args.size}."}]
        contents.extend(ref_parts)
        try:
            resp = client.models.generate_content(model=args.model, contents=contents)
        except Exception as exc:
            if is_quota_error(exc):
                print("Quota exhausted mid-run (429). Enable billing, then re-run — "
                      f"files already saved in {out_dir} are kept.", file=sys.stderr)
                return 5
            print(f"API error on {kind}: {exc}", file=sys.stderr)
            return 3
        saved = False
        for part in getattr(resp, "parts", []) or []:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                raw = base64.b64decode(inline.data) if isinstance(inline.data, str) else inline.data
                idx += 1
                dest = out_dir / f"{kind}_{idx:02d}.png"
                dest.write_bytes(raw)
                print(f"Saved {dest}")
                saved = True
        if not saved:
            print(f"No image returned for {kind} (text-only response?).", file=sys.stderr)
            return 3
    print(f"Done -> {out_dir}. Next: enforce_play_sizes.py --in \"{out_dir}\" --out <PlayFinal> --which all")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
