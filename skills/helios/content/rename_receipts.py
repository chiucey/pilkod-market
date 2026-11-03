#!/usr/bin/env python3
"""
Receipt Photo Converter & Renamer
- Prompts for a project code once at the start
- Converts HEIC/PNG/MOV/JPG → JPG
- Fixes EXIF rotation so images arrive upright to Claude
- Resizes to max 1200px on the long edge before sending to API
- Extracts frame from .mov (Apple Live Photos); skips .mov if paired image exists
- Uses Claude Haiku 4.5 (vision) to extract date and total cost from each receipt
- Renames to: PROJECTCODE_Expense_Mon_DD_YYYY_AMOUNT.jpg
  e.g.  PJ_Q_Expense_Mar_14_2026_40.50.jpg
- Cost falls back to _UNKNOWN if not found
"""

import os
import sys
import base64
import json
import shutil
import subprocess
from pathlib import Path

# ── Dependency bootstrap ─────────────────────────────────────────────────────
def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

try:
    from PIL import Image, ExifTags
except ImportError:
    print("Installing Pillow..."); install("Pillow")
    from PIL import Image, ExifTags

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    print("Installing pillow-heif..."); install("pillow-heif")
    import pillow_heif; pillow_heif.register_heif_opener()

try:
    import anthropic
except ImportError:
    print("Installing anthropic..."); install("anthropic"); import anthropic

# ── Constants ────────────────────────────────────────────────────────────────
IMAGE_EXTS   = {".heic", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
VIDEO_EXTS   = {".mov", ".mp4"}
ALL_EXTS     = IMAGE_EXTS | VIDEO_EXTS
RESIZE_MAX   = 1200
JPEG_QUALITY = 92

MONTH_ABBR = {
    "january": "Jan", "february": "Feb", "march": "Mar", "april": "Apr",
    "may": "May", "june": "Jun", "july": "Jul", "august": "Aug",
    "september": "Sep", "october": "Oct", "november": "Nov", "december": "Dec",
}

# ── Image helpers ────────────────────────────────────────────────────────────

def has_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def extract_frame_ffmpeg(src: Path, out_dir: Path) -> Path:
    dest = out_dir / (src.stem + "_frame.jpg")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src),
         "-vf", "select=eq(n\\,0)", "-vframes", "1", str(dest)],
        capture_output=True, check=True,
    )
    return dest


def fix_rotation(img: Image.Image) -> Image.Image:
    """Rotate image to upright using EXIF orientation tag."""
    try:
        # Works for standard JPEGs
        exif = img._getexif()
        if exif:
            orientation = exif.get(274)
            rotations = {3: 180, 6: 270, 8: 90}
            if orientation in rotations:
                return img.rotate(rotations[orientation], expand=True)
    except Exception:
        pass
    try:
        # Works for HEIC and other formats via getexif()
        exif = img.getexif()
        if exif:
            orientation = exif.get(274)
            rotations = {3: 180, 6: 270, 8: 90}
            if orientation in rotations:
                return img.rotate(rotations[orientation], expand=True)
    except Exception:
        pass
    return img


def resize_and_save(img: Image.Image, dest: Path) -> Path:
    """Fix rotation → resize so long edge ≤ RESIZE_MAX → save as JPEG."""
    img = fix_rotation(img)
    w, h = img.size
    long_edge = max(w, h)
    if long_edge > RESIZE_MAX:
        scale = RESIZE_MAX / long_edge
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.convert("RGB").save(dest, "JPEG", quality=JPEG_QUALITY)
    return dest


def prepare_jpg(src: Path, out_dir: Path, ffmpeg_ok: bool) -> Path | None:
    """Convert/extract → fix rotation → resize → return JPEG path, or None."""
    ext = src.suffix.lower()
    tmp = out_dir / (src.stem + "_tmp.jpg")

    if ext in VIDEO_EXTS:
        if not ffmpeg_ok:
            return None
        raw = extract_frame_ffmpeg(src, out_dir)
        img = Image.open(raw)
        raw.unlink(missing_ok=True)
    else:
        img = Image.open(src)

    return resize_and_save(img, tmp)


def image_to_base64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


# ── Claude extraction ────────────────────────────────────────────────────────

def extract_info_with_claude(client, img_path: Path, debug: bool = False) -> dict:
    """
    Returns {"date": "Mar_14_2026", "cost": "40.50"}
    Either field may be None if not found.
    """
    b64 = image_to_base64(img_path)
    prompt = (
        "This is a photo of a receipt.\n"
        "1. Find the transaction/purchase date.\n"
        "2. Find the total amount charged (the final total the customer paid).\n\n"
        "Reply with ONLY a JSON object — no markdown, no extra text:\n"
        '{"month": "March", "day": "14", "year": "2026", "total": "40.50"}\n\n'
        "Rules:\n"
        "- month: full English month name\n"
        "- day: numeric day without leading zero\n"
        "- year: four-digit year\n"
        "- total: numeric amount only, no currency symbol, with two decimal places\n"
        "- If you cannot find a field, set it to null.\n"
        "Reply with {} if this does not appear to be a receipt."
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=120,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": prompt},
            ],
        }],
    )

    raw = response.content[0].text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    if debug:
        print(f"\n  [debug] Claude raw response: {raw}")

    result = {"date": None, "cost": None}
    try:
        data = json.loads(raw)
        month_key = (data.get("month") or "").lower()
        abbr = MONTH_ABBR.get(month_key)
        day  = data.get("day")
        year = data.get("year")
        if abbr and day and year:
            result["date"] = f"{abbr}_{str(day).zfill(2)}_{year}"
        total = data.get("total")
        if total is not None:
            result["cost"] = f"{float(total):.2f}"
    except Exception:
        pass

    return result


# ── File collection ──────────────────────────────────────────────────────────

def collect_files(folder: Path):
    all_files   = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in ALL_EXTS]
    image_stems = {f.stem.lower() for f in all_files if f.suffix.lower() in IMAGE_EXTS}

    to_process, skipped_movs = [], []
    for f in sorted(all_files):
        if f.suffix.lower() in VIDEO_EXTS and f.stem.lower() in image_stems:
            skipped_movs.append(f.name)
        else:
            to_process.append(f)
    return to_process, skipped_movs


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    i = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{i}{path.suffix}")
        if not candidate.exists():
            return candidate
        i += 1


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # ── Folder ──────────────────────────────────────────────────────────────
    if len(sys.argv) > 1:
        folder = Path(sys.argv[1].strip().strip("'\""))
    else:
        folder = Path(input("Enter the path to your receipts folder: ").strip().strip("'\""))

    if not folder.is_dir():
        print(f"❌  Folder not found: {folder}"); sys.exit(1)

    # ── Project code ─────────────────────────────────────────────────────────
    project_code = input("Enter project code (e.g. PJ_Q): ").strip() or "PROJ"

    # ── Debug mode ───────────────────────────────────────────────────────────
    debug_input = input("Enable debug mode? Shows Claude's raw response (y/n): ").strip().lower()
    debug = debug_input == "y"

    # ── API key ──────────────────────────────────────────────────────────────
    api_key = os.environ.get("ANTHROPIC_API_KEY") or input(
        "Enter your Anthropic API key: "
    ).strip()
    client = anthropic.Anthropic(api_key=api_key)

    # ── ffmpeg ───────────────────────────────────────────────────────────────
    ffmpeg_ok = has_ffmpeg()
    if not ffmpeg_ok:
        print("⚠️  ffmpeg not found — standalone .mov files will be skipped.")
        print("   Mac: brew install ffmpeg\n")

    # ── Output folder ────────────────────────────────────────────────────────
    out_dir = folder / "renamed_receipts"
    out_dir.mkdir(exist_ok=True)
    print(f"\n📁  Output → {out_dir}")
    print(f"🏷️   Project code : {project_code}")
    print(f"📐  Resize to    : {RESIZE_MAX}px long edge")
    print(f"🤖  Model        : Claude Haiku 4.5")
    print(f"🐛  Debug mode   : {'on' if debug else 'off'}\n")

    files, skipped_movs = collect_files(folder)

    if not files:
        print("No supported files found."); sys.exit(0)

    if skipped_movs:
        print(f"ℹ️  Skipping {len(skipped_movs)} paired Live Photo .mov(s):")
        for name in skipped_movs:
            print(f"   • {name}")
        print()

    print(f"Processing {len(files)} file(s)...\n")

    success = unknown_date = unknown_cost = errors = 0

    for i, src in enumerate(files, 1):
        ext = src.suffix.lower()
        print(f"[{i}/{len(files)}] {src.name}", end=" … ", flush=True)

        try:
            jpg_path = prepare_jpg(src, out_dir, ffmpeg_ok)
            if jpg_path is None:
                print("⏭️  skipped (no ffmpeg for .mov)")
                errors += 1
                continue

            if ext in VIDEO_EXTS:
                print("[frame]", end=" ", flush=True)

            info = extract_info_with_claude(client, jpg_path, debug=debug)
            date_str = info["date"]
            cost_str = info["cost"]

            date_part = date_str or "UNKNOWN_DATE"
            cost_part = cost_str or "UNKNOWN"

            final_name = unique_path(out_dir / f"{project_code}_Expense_{date_part}_{cost_part}.jpg")
            jpg_path.rename(final_name)

            if not date_str: unknown_date += 1
            if not cost_str: unknown_cost += 1
            if date_str and cost_str: success += 1

            print(f"✅  → {final_name.name}")

        except Exception as e:
            print(f"❌  Error: {e}")
            errors += 1

    print(f"\n── Summary {'─' * 36}")
    print(f"  ✅  Fully resolved           : {success}")
    print(f"  📅  Date unknown             : {unknown_date}")
    print(f"  💰  Cost unknown             : {unknown_cost}")
    print(f"  ❌  Errors                   : {errors}")
    print(f"  ⏭️   Live Photo .movs skipped : {len(skipped_movs)}")
    print(f"\n📂  Files saved to: {out_dir}")


if __name__ == "__main__":
    main()
