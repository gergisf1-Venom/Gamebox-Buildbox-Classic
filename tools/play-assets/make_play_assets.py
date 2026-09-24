"""Interactive Gamebox Play-assets maker — asks, validates, generates, enforces.

One command for any game (this is what SKILL_05 calls):

  python make_play_assets.py

It asks for:
  1. Reference folder (your existing screenshots — validation included)
  2. How many images per type (phones default 6, feature 1, icon 1)
  3. Game name + output folder
Then it validates GEMINI_API_KEY BEFORE spending anything, generates with
Nano Banana Pro (exact target sizes stated in every prompt), and enforces the
exact Play pixels with enforce_play_sizes.py. Pure upscaling is never presented
as a final deliverable.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
VALID_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip().strip("\"'")
    return val or default


def ask_int(prompt: str, default: int, lo: int, hi: int) -> int:
    while True:
        raw = ask(prompt, str(default))
        try:
            val = int(raw)
        except ValueError:
            print(f"Enter a number {lo}-{hi}.")
            continue
        if lo <= val <= hi:
            return val
        print(f"Enter a number {lo}-{hi}.")


def find_images(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in VALID_EXTS and p.is_file())


def main() -> int:
    print("=== Gamebox Play-assets maker (Nano Banana first, exact sizes enforced) ===\n")

    while True:
        ref_in = ask("Reference folder (existing screenshots)")
        ref_dir = Path(ref_in)
        if not ref_dir.is_dir():
            print(f"Not a folder: {ref_in}. Try again.")
            continue
        refs = find_images(ref_dir)
        if not refs:
            print(f"No png/jpg/webp images in {ref_dir}. Try again.")
            continue
        print(f"Found {len(refs)} reference image(s).")
        break

    phones = ask_int("How many phone screenshots (0-8)", 6, 0, 8)
    features = ask_int("How many feature graphics (0-2)", 1, 0, 2)
    icons = ask_int("How many icons (0-2)", 1, 0, 2)
    if phones + features + icons == 0:
        print("All counts are 0 — nothing to do.")
        return 2

    game = ask("Game name", ref_dir.parent.name.replace("-", " ").strip() or "Game")
    default_out = str(ref_dir / "PlayFinal")
    out_dir = ask("Final output folder", default_out)

    backend = ask("Backend (higgsfield = your credits, works now / gemini = API key)", "higgsfield").lower()
    if backend not in ("higgsfield", "gemini"):
        print("Unknown backend — use 'higgsfield' or 'gemini'.")
        return 2

    raw_dir = HERE / "gen_raw"
    if backend == "higgsfield":
        print("\nStep 1/2: generating with Higgsfield Nano Banana Pro...")
        rc = subprocess.call([
            sys.executable, str(HERE / "higgsfield_backend.py"),
            "--game", game,
            "--refs", str(ref_dir / "*.png"),
            "--phones", str(phones),
            "--features", str(features),
            "--icons", str(icons),
            "--out", str(raw_dir),
            "--playfinal", out_dir,
        ])
        if rc != 0:
            print(f"Generation stopped (exit {rc}). Fix the error above and re-run.")
            return rc
        print(f"\nDone. Client-ready files in {out_dir} "
              f"(phone 1080x1920, tablet, feature 1024x500, icon 512x512).")
        return 0

    # Key check BEFORE generation (import from the generator so logic lives in one place).
    sys.path.insert(0, str(HERE))
    from generate_play_assets import load_dotenv  # noqa: E402

    load_dotenv(HERE / ".env")
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("\nGEMINI_API_KEY is not set (env var or tools/play-assets/.env). "
              "Generation needs it — set it and re-run. Nothing was spent.")
        return 2
    try:
        from google import genai  # type: ignore
        from generate_play_assets import validate_key  # noqa: E402

        ok, msg = validate_key(genai.Client(api_key=api_key))
        print(msg)
        if not ok:
            print("Fix the key/quota issue above and re-run. Nothing was spent.")
            return 4
    except ImportError:
        print("Missing dependency: pip install -r requirements.txt", file=sys.stderr)
        return 2

    raw_dir = HERE / "gen_raw"
    gen_cmd = [
        sys.executable, str(HERE / "generate_play_assets.py"),
        "--game", game,
        "--refs", str(ref_dir / "*.png"),
        "--phones", str(phones),
        "--features", str(features),
        "--icons", str(icons),
        "--out", str(raw_dir),
        "--no-validate",  # already validated above; avoids a duplicate message
    ]
    print("\nStep 1/2: generating with Gemini Nano Banana Pro...")
    rc = subprocess.call(gen_cmd)
    if rc != 0:
        print(f"Generation stopped (exit {rc}). Fix the error above and re-run.")
        return rc

    print("\nStep 2/2: enforcing exact Play sizes...")
    rc = subprocess.call([
        sys.executable, str(HERE / "enforce_play_sizes.py"),
        "--in", str(raw_dir / game),
        "--out", out_dir,
        "--which", "all",
    ])
    if rc != 0:
        print(f"Size enforcement reported warnings (exit {rc}) — check files in {out_dir}.")
        return rc
    print(f"\nDone. Client-ready files in {out_dir} "
          f"(phone 1080x1920, tablet, feature 1024x500, icon 512x512).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
