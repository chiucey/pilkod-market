#!/usr/bin/env python3
"""
Template: cut one MP3 clip per sentence, embed Base64, and convert word times
to clip-relative times.

Requires ffmpeg in PATH.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
from pathlib import Path


def run_ffmpeg(media: Path, start: float, end: float, out_mp3: Path) -> None:
    duration = max(end - start, 0.05)
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(media),
        "-t",
        f"{duration:.3f}",
        "-vn",
        "-acodec",
        "libmp3lame",
        str(out_mp3),
    ]
    subprocess.run(cmd, check=True)


def embed_audio(data: dict, media: Path, clips_dir: Path, start_pad: float, end_pad: float) -> dict:
    clips_dir.mkdir(parents=True, exist_ok=True)
    for sentence in data["sentences"]:
        abs_start = float(sentence["start"])
        abs_end = float(sentence["end"])
        clip_start = max(abs_start - start_pad, 0)
        clip_end = abs_end + end_pad
        clip_path = clips_dir / f"sentence_{int(sentence['index']):04d}.mp3"
        run_ffmpeg(media, clip_start, clip_end, clip_path)
        encoded = base64.b64encode(clip_path.read_bytes()).decode("ascii")

        sentence["a"] = "data:audio/mp3;base64," + encoded
        sentence["s"] = round(abs_start, 2)
        sentence["e"] = round(abs_end, 2)
        sentence["clip_start"] = round(clip_start, 3)
        for word in sentence.get("words", []):
            word["start_abs"] = round(float(word["start"]), 3)
            word["end_abs"] = round(float(word["end"]), 3)
            word["start"] = round(max(float(word["start"]) - clip_start, 0), 3)
            word["end"] = round(max(float(word["end"]) - clip_start, 0), 3)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--learning-data", required=True, help="Step 03 learning_data.json")
    parser.add_argument("--media", required=True, help="Local video/audio file")
    parser.add_argument("--out", required=True, help="JSON with embedded audio")
    parser.add_argument("--clips-dir", default=None, help="Directory for generated sentence MP3 clips")
    parser.add_argument("--start-pad", type=float, default=0.08)
    parser.add_argument("--end-pad", type=float, default=0.12)
    args = parser.parse_args()

    data = json.loads(Path(args.learning_data).read_text(encoding="utf-8"))
    if "sentences" not in data:
        raise SystemExit("Step 04 requires Step 03 learning_data.json with a top-level 'sentences' array.")
    missing = [s.get("index") for s in data["sentences"] if not (s.get("translation") or s.get("z"))]
    if missing:
        raise SystemExit(f"Step 03 is incomplete; missing translations for sentence indexes: {missing[:20]}")
    out_path = Path(args.out)
    clips_dir = Path(args.clips_dir) if args.clips_dir else out_path.parent / "audio_clips_tmp"
    data = embed_audio(data, Path(args.media), clips_dir, args.start_pad, args.end_pad)
    out_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote audio-embedded data to {args.out}")


if __name__ == "__main__":
    main()
