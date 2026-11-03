#!/usr/bin/env python3
"""Local media helpers for scroll-world-local.

Commands:
  ffmpeg-path
  probe <video>
  first <video> <image>
  last <video> <image>
  frame <video> <seconds> <image>
  contact <video> <contact.jpg> [count=12]
  scene-detect <video> <out-dir> [threshold=0.28]
  split <video> <start-sec> <end-sec> <output.mp4>
  encode <video> <output.mp4> [desktop|mobile]
  seamdiff <image-a> <image-b>

All commands preserve the source file. Generated paths should be absolute when
this script is called from an agent workflow.
"""

import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path


def ffmpeg_path():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        from shutil import which
        path = which("ffmpeg")
        if path:
            return path
        raise SystemExit(
            "ffmpeg not found. Install imageio-ffmpeg or provide ffmpeg on PATH.\n"
            f"Original error: {exc}"
        )


def run(args, capture=False):
    return subprocess.run(
        args,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def ensure_parent(path):
    Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def probe_video(src):
    ff = ffmpeg_path()
    proc = subprocess.run(
        [ff, "-hide_banner", "-i", src],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    text = proc.stderr
    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
    if not duration_match:
        raise SystemExit(f"Could not read video metadata: {src}")
    hours, minutes, seconds = duration_match.groups()
    duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    video_line = next((line.strip() for line in text.splitlines() if "Video:" in line), "")
    audio_line = next((line.strip() for line in text.splitlines() if "Audio:" in line), "")
    size_match = re.search(r"(?<!\d)(\d{2,5})x(\d{2,5})(?!\d)", video_line)
    fps_match = re.search(r"(?:,\s*)(\d+(?:\.\d+)?)\s*fps", video_line)
    codec_match = re.search(r"Video:\s*([^,\s]+)", video_line)
    bitrate_match = re.search(r"bitrate:\s*(\d+)\s*kb/s", text)
    return {
        "source": str(Path(src).expanduser().resolve()),
        "duration_seconds": round(duration, 3),
        "width": int(size_match.group(1)) if size_match else None,
        "height": int(size_match.group(2)) if size_match else None,
        "fps": float(fps_match.group(1)) if fps_match else None,
        "codec": codec_match.group(1) if codec_match else None,
        "bitrate_kbps": int(bitrate_match.group(1)) if bitrate_match else None,
        "has_audio": bool(audio_line),
    }


def frame_at(src, seconds, dst):
    ensure_parent(dst)
    ff = ffmpeg_path()
    run([
        ff, "-v", "error", "-y", "-ss", str(seconds), "-i", src,
        "-frames:v", "1", "-q:v", "2", dst,
    ])
    print(f"frame {seconds}s -> {dst}")


def first_frame(src, dst):
    frame_at(src, 0, dst)


def last_frame(src, dst):
    ensure_parent(dst)
    ff = ffmpeg_path()
    run([
        ff, "-v", "error", "-y", "-sseof", "-0.12", "-i", src,
        "-frames:v", "1", "-q:v", "2", dst,
    ])
    print("last frame ->", dst)


def contact_sheet(src, dst, count=12):
    meta = probe_video(src)
    duration = max(meta["duration_seconds"], 0.1)
    count = max(4, min(int(count), 48))
    cols = math.ceil(math.sqrt(count * 16 / 9))
    rows = math.ceil(count / cols)
    interval = duration / count
    ensure_parent(dst)

    font_candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font = next((p for p in font_candidates if os.path.exists(p)), None)
    label = ""
    if font:
        label = (
            f",drawtext=fontfile='{font}':text='%{{pts\\:hms}}':"
            "x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6"
        )
    vf = (
        f"fps=1/{interval:.6f},scale=360:-2{label},"
        f"tile={cols}x{rows}:padding=4:margin=4"
    )
    ff = ffmpeg_path()
    run([ff, "-v", "error", "-y", "-i", src, "-vf", vf, "-frames:v", "1", dst])
    sidecar = str(Path(dst).with_suffix(".json"))
    times = [round(i * interval, 3) for i in range(count)]
    Path(sidecar).write_text(json.dumps({"contact_sheet": dst, "sample_times": times}, indent=2), encoding="utf-8")
    print(f"contact sheet -> {dst} ({cols}x{rows}, {count} samples)")
    print("sample map ->", sidecar)


def scene_detect(src, out_dir, threshold=0.28):
    out = Path(out_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    ff = ffmpeg_path()
    pattern = str(out / "scene_%03d.png")
    vf = f"select='gt(scene,{float(threshold)})',showinfo,scale=640:-2"
    proc = subprocess.run(
        [ff, "-hide_banner", "-y", "-i", src, "-vf", vf, "-fps_mode", "vfr", "-c:v", "png", pattern],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0 and "Nothing was written" not in proc.stderr:
        raise SystemExit(proc.stderr)
    times = [float(v) for v in re.findall(r"pts_time:([0-9.]+)", proc.stderr)]
    images = sorted(str(p) for p in out.glob("scene_*.png"))
    result = {
        "source": str(Path(src).expanduser().resolve()),
        "threshold": float(threshold),
        "candidates": [
            {"time": round(times[i], 3) if i < len(times) else None, "image": image}
            for i, image in enumerate(images)
        ],
    }
    manifest = out / "scenes.json"
    manifest.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"scene candidates -> {out} ({len(images)} frames)")
    print("manifest ->", manifest)


def encode(src, dst, profile="desktop"):
    ensure_parent(dst)
    ff = ffmpeg_path()
    args = [ff, "-v", "error", "-y", "-i", src, "-an", "-c:v", "libx264"]
    if profile == "mobile":
        args += ["-vf", "scale=-2:720", "-crf", "22", "-g", "4"]
    else:
        args += ["-crf", "20", "-g", "8"]
    args += ["-pix_fmt", "yuv420p", "-movflags", "+faststart", dst]
    run(args)
    print(f"encoded ({profile}) -> {dst}")


def split_clip(src, start, end, dst):
    if float(end) <= float(start):
        raise SystemExit("split end must be greater than start")
    ensure_parent(dst)
    ff = ffmpeg_path()
    run([
        ff, "-v", "error", "-y", "-ss", str(start), "-to", str(end), "-i", src,
        "-an", "-c:v", "libx264", "-crf", "20", "-g", "8",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst,
    ])
    print(f"split {start}s..{end}s -> {dst}")


def seamdiff(a_path, b_path):
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError as exc:
        raise SystemExit(
            "seamdiff requires Pillow in the current Python environment. "
            "Use the host's visual comparison capability when Pillow is unavailable."
        ) from exc
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    if a.size != b.size:
        b = b.resize(a.size)
        print("(resized b to match a)")
    diff = ImageChops.difference(a, b)
    means = ImageStat.Stat(diff).mean
    mean = sum(means) / len(means)
    extrema = diff.getextrema()
    maximum = max(channel[1] for channel in extrema)
    pixel_iter = diff.get_flattened_data() if hasattr(diff, "get_flattened_data") else diff.getdata()
    pixels = list(pixel_iter)
    total = max(len(pixels), 1)
    pct8 = sum(1 for px in pixels if max(px) > 8) * 100 / total
    pct24 = sum(1 for px in pixels if max(px) > 24) * 100 / total
    print(f"mean abs diff : {mean:.3f} / 255")
    print(f"max abs diff  : {maximum}")
    print(f"pixels >8     : {pct8:.2f}%")
    print(f"pixels >24    : {pct24:.2f}%")
    if mean < 5 and pct24 < 2:
        print("VERDICT: SEAM OK")
        return 0
    print("VERDICT: SEAM SUSPECT")
    return 2


def usage_error():
    raise SystemExit(__doc__)


def main():
    if len(sys.argv) < 2:
        usage_error()
    cmd = sys.argv[1]
    if cmd == "ffmpeg-path":
        print(ffmpeg_path())
    elif cmd == "probe" and len(sys.argv) == 3:
        print(json.dumps(probe_video(sys.argv[2]), indent=2))
    elif cmd == "first" and len(sys.argv) == 4:
        first_frame(sys.argv[2], sys.argv[3])
    elif cmd == "last" and len(sys.argv) == 4:
        last_frame(sys.argv[2], sys.argv[3])
    elif cmd == "frame" and len(sys.argv) == 5:
        frame_at(sys.argv[2], float(sys.argv[3]), sys.argv[4])
    elif cmd == "contact" and len(sys.argv) in (4, 5):
        contact_sheet(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) == 5 else 12)
    elif cmd == "scene-detect" and len(sys.argv) in (4, 5):
        scene_detect(sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) == 5 else 0.28)
    elif cmd == "split" and len(sys.argv) == 6:
        split_clip(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])
    elif cmd == "encode" and len(sys.argv) in (4, 5):
        encode(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) == 5 else "desktop")
    elif cmd == "seamdiff" and len(sys.argv) == 4:
        raise SystemExit(seamdiff(sys.argv[2], sys.argv[3]))
    else:
        usage_error()


if __name__ == "__main__":
    main()
