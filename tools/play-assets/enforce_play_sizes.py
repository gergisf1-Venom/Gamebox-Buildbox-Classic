"""Enforce exact Google Play listing sizes (generic Gamebox tool, Pillow-only).

Usage (any game):
  python enforce_play_sizes.py --in "<refs folder>" --out "<PlayFinal folder>" --which phone,tablet,feature,icon --png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

TARGETS: dict[str, tuple[int, int]] = {
    "phone_portrait": (1080, 1920),
    "phone_landscape": (1920, 1080),
    "tablet_7": (1200, 1920),
    "tablet_10": (1600, 2560),
    "feature": (1024, 500),
    "icon": (512, 512),
}

GROUPS: dict[str, list[str]] = {
    "phone": ["phone_portrait"],
    "tablet": ["tablet_7", "tablet_10"],
    "feature": ["feature"],
    "icon": ["icon"],
    "all": list(TARGETS),
}

VALID_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def cover_crop(img: Image.Image, tw: int, th: int) -> Image.Image:
    """Scale to fill (tw,th) then center-crop. No distortion."""
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, round(sw * scale)), max(1, round(sh * scale))
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def process_one(src: Path, dst: Path, target: str, use_png: bool) -> dict:
    tw, th = TARGETS[target]
    with Image.open(src) as im:
        if target == "icon":
            out = cover_crop(im.convert("RGBA"), tw, th)
            dst = dst.with_suffix(".png")
            out.save(dst, optimize=True)
        else:
            out = cover_crop(im.convert("RGB"), tw, th)
            if use_png or src.suffix.lower() == ".png":
                dst = dst.with_suffix(".png")
                out.save(dst, "PNG", optimize=True)
            else:
                dst = dst.with_suffix(".jpg")
                out.save(dst, "JPEG", quality=95, optimize=True)
    size = dst.stat().st_size
    w, h = tw, th
    long_side, short_side = max(w, h), min(w, h)
    # 2:1 ratio rule applies to screenshots only — feature (1024x500 banner) and icon are exempt.
    ok_ratio = True if target in ("feature", "icon") else long_side <= 2 * short_side
    limit = 1024 * 1024 if target == "icon" else 8 * 1024 * 1024
    ok_size = size <= limit
    return {"file": str(dst), "target": target, "size": size,
            "ok_dims": True, "ok_ratio": ok_ratio, "ok_size": ok_size}


def parse_which(value: str) -> list[str]:
    out: list[str] = []
    for part in value.split(","):
        part = part.strip().lower()
        if part in TARGETS:
            out.append(part)
        elif part in GROUPS:
            out.extend(GROUPS[part])
        else:
            raise ValueError(f"Unknown target/group: {part!r}. Valid: {sorted(set(TARGETS) | set(GROUPS))}")
    seen, deduped = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Enforce exact Google Play sizes for any game.")
    ap.add_argument("--in", dest="src", required=True, help="Input folder with source images (any size).")
    ap.add_argument("--out", dest="dst", required=True, help="Output PlayFinal folder.")
    ap.add_argument("--which", default="phone,feature,icon",
                    help="Comma list of targets/groups: phone,tablet,feature,icon,all or exact names.")
    ap.add_argument("--png", action="store_true", help="Save screenshots as PNG instead of JPEG.")
    args = ap.parse_args(argv)

    src_dir = Path(args.src)
    dst_dir = Path(args.dst)
    if not src_dir.is_dir():
        print(f"Input folder not found: {src_dir}", file=sys.stderr)
        return 2
    targets = parse_which(args.which)
    files = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in VALID_EXTS and p.is_file())
    if not files:
        print(f"No images found in {src_dir}", file=sys.stderr)
        return 2
    dst_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for target in targets:
        tdir = dst_dir / target
        tdir.mkdir(parents=True, exist_ok=True)
        for src in files:
            # process_one may adjust the suffix (PNG sources stay PNG); use its returned path for logging.
            dst_guess = tdir / f"{src.stem}_{target}{'.png' if (target == 'icon' or args.png or src.suffix.lower() == '.png') else '.jpg'}"
            info = process_one(src, dst_guess, target, args.png)
            status = "OK" if (info["ok_ratio"] and info["ok_size"]) else "WARN"
            if status == "WARN":
                failures += 1
            print(f"[{status}] {info['target']}: {src.name} -> {Path(info['file']).name} ({info['size']/1024:.0f} KB)")
    print(f"Done: {len(files)} source(s) x {len(targets)} target(s) -> {dst_dir}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
