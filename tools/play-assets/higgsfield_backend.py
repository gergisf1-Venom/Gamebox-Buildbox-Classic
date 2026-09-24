"""Generate listing art via Higgsfield CLI (Nano Banana Pro), then enforce exact Play sizes separately.

Generic Gamebox backend — works for ANY game via --game / --refs. Auth comes
from `higgsfield auth login` (no API key). No video.

  higgsfield auth login   # once, browser sign-in
  python higgsfield_backend.py --game "Shape Switch" --refs "path/to/refs/*.png" --phones 2 --features 1 --icons 1 --out gen_raw
  python enforce_play_sizes.py --in gen_raw/"Shape Switch" --out "<game>/PlayFinal" --which all

Every prompt states the exact target size (1080x1920, 1024x500, 512x512);
Nano Banana Pro returns high-res art at the right aspect, and
enforce_play_sizes.py guarantees the exact store pixels.
"""
from __future__ import annotations

import argparse
import glob
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

MODEL = "nano_banana_pro"
RESOLUTION = "2k"

HF_CLI = shutil.which("higgsfield") or shutil.which("higgsfield.cmd") or "higgsfield"

PHONE_PROMPT = (
    "Recreate this mobile game screenshot as crisp high-resolution portrait "
    "gameplay art for game '{game}'. Target size 1080x1920 pixels, exact 9:16 "
    "portrait. Keep the same game (colors, shapes, UI style), show real gameplay "
    "only, no phone frame, no watermark, no extra text. Vertical composition "
    "with the key action centered. Moment {n}: {moment}."
)
FEATURE_PROMPT = (
    "Create a wide feature-graphic background for mobile game '{game}'. Target "
    "size exactly 1024x500 pixels (wide banner). Vibrant gameplay theme, empty "
    "center safe-area for title text, no text, no logo, no watermark."
)
ICON_PROMPT = (
    "Create a square mobile game icon for '{game}'. Target size exactly 512x512 "
    "pixels, 1:1 square. Single bold shape-switch motif on a vivid background, "
    "flat vector style, centered, no text, no watermark."
)

# Each generated kind maps ONLY to its correct Play targets (never cross-mapped).
KIND_TARGETS: dict[str, list[str]] = {
    "phone": ["phone_portrait", "tablet_7", "tablet_10"],
    "feature": ["feature"],
    "icon": ["icon"],
}

PHONE_MOMENTS = [
    "core gameplay loop, mid-action",
    "best power-up or combo moment",
]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    cmd = [HF_CLI if c == "higgsfield" else c for c in cmd]
    return subprocess.run(cmd, capture_output=True, text=True)


def check_auth() -> tuple[bool, str]:
    p = run(["higgsfield", "account", "status"])
    out = (p.stdout + p.stderr).strip()
    if p.returncode != 0:
        if "No workspace selected" in out:
            return False, "No Higgsfield workspace selected. Run: higgsfield workspace list + set."
        return False, f"Not signed in. Run: higgsfield auth login\n{out}"
    return True, out


def estimate_cost(prompt: str, aspect: str, refs: list[str]) -> str:
    cmd = ["higgsfield", "generate", "cost", MODEL, "--prompt", prompt,
           "--aspect_ratio", aspect, "--resolution", RESOLUTION]
    for r in refs:
        cmd += ["--image-references", r]
    p = run(cmd + ["--json"])
    if p.returncode != 0:
        return "unknown"
    try:
        return str(json.loads(p.stdout).get("credits", "unknown"))
    except Exception:
        return "unknown"


def generate_one(prompt: str, aspect: str, refs: list[str], timeout: str = "10m") -> dict:
    cmd = ["higgsfield", "generate", "create", MODEL, "--prompt", prompt,
           "--aspect_ratio", aspect, "--resolution", RESOLUTION]
    for r in refs:
        cmd += ["--image-references", r]
    cmd += ["--wait", "--wait-timeout", timeout, "--json"]
    p = run(cmd)
    if p.returncode != 0:
        raise RuntimeError(f"CLI error: {(p.stdout + p.stderr).strip()[-500:]}")
    try:
        jobs = json.loads(p.stdout)
    except Exception as exc:
        raise RuntimeError(f"Unparseable CLI output: {exc}\n{p.stdout[:300]}")
    job = jobs[0] if isinstance(jobs, list) else jobs
    if job.get("status") != "completed" or not job.get("result_url"):
        raise RuntimeError(f"Job {job.get('id')} ended with status {job.get('status')!r} (no result).")
    return job


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "gamebox-play-assets/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Generate Play assets via Higgsfield Nano Banana Pro (generic).")
    ap.add_argument("--game", required=True, help="Game name, e.g. 'Shape Switch'.")
    ap.add_argument("--refs", default="", help="Glob of reference screenshots. Strongly recommended.")
    ap.add_argument("--phones", type=int, default=2, help="Phone shots (0-8, default 2 = Play minimum).")
    ap.add_argument("--features", type=int, default=1, help="Feature graphics (0-2, default 1).")
    ap.add_argument("--icons", type=int, default=1, help="Icons (0-2, default 1).")
    ap.add_argument("--out", default="gen_raw", help="Raw output root folder.")
    ap.add_argument("--playfinal", default="", help="If set, auto-enforce kind-correct sizes here after generating.")
    ap.add_argument("--from-raw", default="",
                    help="Skip generation; enforce kind-correct sizes from an existing raw folder into --playfinal.")
    ap.add_argument("--dry-run", action="store_true", help="Print plan + cost, no generation.")
    return ap


def auto_enforce(raw_dir: Path, playfinal: Path) -> int:
    """Enforce each generated file ONLY to its kind's correct targets."""
    import shutil
    import tempfile

    here = Path(__file__).parent
    failures = 0
    for kind, targets in KIND_TARGETS.items():
        files = sorted(raw_dir.glob(f"{kind}_*.png"))
        if not files:
            continue
        with tempfile.TemporaryDirectory(prefix=f"hf_{kind}_") as tmp:
            for f in files:
                shutil.copy2(f, str(Path(tmp) / f.name))
            p = run([sys.executable, str(here / "enforce_play_sizes.py"),
                     "--in", tmp, "--out", str(playfinal), "--which", ",".join(targets)])
            print(p.stdout.strip())
            if p.returncode != 0:
                print(p.stderr.strip(), file=sys.stderr)
                failures += 1
    if failures:
        print(f"Size enforcement reported issues in {failures} group(s).", file=sys.stderr)
        return 1
    print(f"PlayFinal ready (kind-correct only) -> {playfinal}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    refs = sorted(glob.glob(args.refs)) if args.refs else []
    out_dir = Path(args.out) / args.game

    jobs: list[tuple[str, str, str]] = []
    for i in range(args.phones):
        moment = PHONE_MOMENTS[i % len(PHONE_MOMENTS)]
        jobs.append(("phone", PHONE_PROMPT.format(game=args.game, n=i + 1, moment=moment), "9:16"))
    for _ in range(args.features):
        jobs.append(("feature", FEATURE_PROMPT.format(game=args.game), "16:9"))
    for _ in range(args.icons):
        jobs.append(("icon", ICON_PROMPT.format(game=args.game), "1:1"))
    if not jobs:
        print("Nothing to generate (all counts are 0).", file=sys.stderr)
        return 2
    if not 0 <= args.phones <= 8:
        print("--phones must be 0-8.", file=sys.stderr)
        return 2
    if not refs and not args.from_raw:
        print("WARNING: no --refs matched. Results will drift from the real game.", file=sys.stderr)

    print(f"Plan: {len(jobs)} image(s) for {args.game!r} -> {out_dir} ({len(refs)} ref(s))")
    if args.from_raw:
        if not args.playfinal:
            print("--from-raw needs --playfinal <dir>.", file=sys.stderr)
            return 2
        return auto_enforce(Path(args.from_raw), Path(args.playfinal))
    if args.dry_run:
        sample = run(["higgsfield", "generate", "cost", MODEL, "--prompt", jobs[0][1],
                      "--aspect_ratio", jobs[0][2], "--resolution", RESOLUTION] +
                     (["--image-references", refs[0]] if refs else []) + ["--json"])
        print("Sample cost: " + sample.stdout.strip())
        print("No generation (dry-run).")
        return 0

    ok, msg = check_auth()
    print(msg)
    if not ok:
        return 4

    out_dir.mkdir(parents=True, exist_ok=True)
    idx = 0
    for kind, prompt, aspect in jobs:
        idx += 1
        print(f"[{idx}/{len(jobs)}] generating {kind} ({aspect})...")
        try:
            job = generate_one(prompt, aspect, refs[:6])
        except RuntimeError as exc:
            text = str(exc)
            if "credit" in text.lower() or "insufficient" in text.lower():
                print("Out of Higgsfield credits. Top up, then re-run — files already saved are kept.",
                      file=sys.stderr)
                return 5
            print(f"Generation failed on {kind}: {text}", file=sys.stderr)
            return 3
        dest = out_dir / f"{kind}_{idx:02d}.png"
        download(job["result_url"], dest)
        print(f"Saved {dest}")
    if args.playfinal:
        return auto_enforce(out_dir, Path(args.playfinal))
    print(f"Done -> {out_dir}. Next: enforce kind-correct sizes with --from-raw \"{out_dir}\" --playfinal <PlayFinal>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
