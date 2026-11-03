#!/usr/bin/env python3
"""Plan, prepare, conform, and preflight MiniMax H3 video timelines."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


H3_FPS = 24
FRAME_STEP = 17
FRAME_OFFSET = 5


class ContractError(RuntimeError):
    pass


def run(command: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
    except FileNotFoundError as exc:
        raise ContractError(f"required executable not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "command failed").strip().splitlines()
        raise ContractError(detail[-1] if detail else "command failed") from exc


def require_file(path: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise ContractError(f"video does not exist: {resolved}")
    return resolved


def probe(path: str | Path) -> dict:
    media = require_file(str(path))
    completed = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=index,codec_type,width,height,avg_frame_rate,r_frame_rate,nb_frames",
        "-of", "json", str(media),
    ])
    payload = json.loads(completed.stdout)
    video = next((s for s in payload.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video:
        raise ContractError(f"no video stream: {media}")
    duration = float(payload.get("format", {}).get("duration") or 0)
    if duration <= 0:
        raise ContractError(f"invalid duration: {media}")
    rate_text = video.get("avg_frame_rate") or video.get("r_frame_rate") or "0/1"
    try:
        fps = float(Fraction(rate_text))
    except (ValueError, ZeroDivisionError) as exc:
        raise ContractError(f"invalid frame rate: {rate_text}") from exc
    if fps <= 0:
        raise ContractError(f"invalid frame rate: {rate_text}")
    width, height = int(video.get("width") or 0), int(video.get("height") or 0)
    if width <= 0 or height <= 0:
        raise ContractError(f"invalid frame size: {media}")
    return {
        "path": str(media),
        "duration": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "aspect_ratio": width / height,
        "frames": int(video["nb_frames"]) if str(video.get("nb_frames", "")).isdigit() else None,
        "has_audio": any(s.get("codec_type") == "audio" for s in payload.get("streams", [])),
    }


def legal_frames(min_seconds: float, max_seconds: float) -> list[int]:
    if min_seconds <= 0 or max_seconds <= min_seconds:
        raise ContractError("invalid H3 duration limits")
    minimum = math.ceil(min_seconds * H3_FPS)
    maximum = math.floor(max_seconds * H3_FPS)
    first_n = max(0, math.ceil((minimum - FRAME_OFFSET) / FRAME_STEP))
    values = []
    n = first_n
    while True:
        frames = FRAME_STEP * n + FRAME_OFFSET
        if frames > maximum:
            break
        if frames >= minimum:
            values.append(frames)
        n += 1
    if not values:
        raise ContractError("no legal 17n+5 frame count inside provider limits")
    return values


def make_plan(source: dict, min_seconds: float, max_seconds: float) -> dict:
    candidates = legal_frames(min_seconds, max_seconds)
    target = min(candidates, key=lambda frames: (abs(frames / H3_FPS - source["duration"]), frames))
    generation_duration = target / H3_FPS
    delta = generation_duration - source["duration"]
    ratio = generation_duration / source["duration"]
    return {
        "source": source,
        "h3_fps": H3_FPS,
        "num_frames": target,
        "generation_duration": generation_duration,
        "duration_delta": delta,
        "retime_percent": (ratio - 1.0) * 100.0,
        "prepare_setpts_factor": ratio,
        "conform_setpts_factor": 1.0 / ratio,
        "requires_disclosure": abs(ratio - 1.0) > 0.001,
        "strict_single_pass_recommended": abs(ratio - 1.0) <= 0.03,
    }


def ffmpeg_executable() -> str:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise ContractError("required executable not found: ffmpeg")
    return executable


def command_plan(args: argparse.Namespace) -> int:
    plan = make_plan(probe(args.source), args.min_seconds, args.max_seconds)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


def command_prepare(args: argparse.Namespace) -> int:
    source = probe(args.source)
    if args.num_frames <= 0 or (args.num_frames - FRAME_OFFSET) % FRAME_STEP:
        raise ContractError("num-frames must satisfy 17n+5")
    target_duration = args.num_frames / H3_FPS
    factor = target_duration / source["duration"]
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    run([
        ffmpeg_executable(), "-hide_banner", "-loglevel", "error", "-y",
        "-i", source["path"],
        "-an", "-vf", f"setpts={factor:.12f}*PTS,fps={H3_FPS}",
        "-frames:v", str(args.num_frames),
        "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(output),
    ], capture=True)
    result = probe(output)
    print(json.dumps({"output": str(output), "target_frames": args.num_frames, "result": result}, ensure_ascii=False, indent=2))
    return 0


def atempo_chain(factor: float) -> str:
    values = []
    remaining = factor
    while remaining > 2.0:
        values.append(2.0)
        remaining /= 2.0
    while remaining < 0.5:
        values.append(0.5)
        remaining /= 0.5
    values.append(remaining)
    return ",".join(f"atempo={value:.12f}" for value in values)


def command_conform(args: argparse.Namespace) -> int:
    source = probe(args.source)
    result = probe(args.result)
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    video_factor = source["duration"] / result["duration"]
    video_filter = (
        f"setpts={video_factor:.12f}*PTS,"
        f"scale={source['width']}:{source['height']}:force_original_aspect_ratio=decrease,"
        f"pad={source['width']}:{source['height']}:(ow-iw)/2:(oh-ih)/2:black,"
        f"fps={source['fps']:.12f},setsar=1"
    )
    command = [ffmpeg_executable(), "-hide_banner", "-loglevel", "error", "-y", "-i", result["path"]]
    if result["has_audio"]:
        audio_factor = result["duration"] / source["duration"]
        command += [
            "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{atempo_chain(audio_factor)}[a]",
            "-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "192k",
        ]
    else:
        command += ["-vf", video_filter, "-an"]
    command += [
        "-t", f"{source['duration']:.9f}", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
    ]
    run(command, capture=True)
    print(json.dumps({"output": str(output), "source": source, "input_result": result, "conformed": probe(output)}, ensure_ascii=False, indent=2))
    return 0


PTS_PATTERN = re.compile(r"pts_time:([0-9.]+)")


def cut_candidates(path: str, threshold: float) -> list[float]:
    completed = subprocess.run(
        [
            ffmpeg_executable(), "-hide_banner", "-loglevel", "info", "-i", str(require_file(path)),
            "-filter:v", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        raise ContractError(detail[-1] if detail else "scene detection failed")
    return [float(match.group(1)) for match in PTS_PATTERN.finditer(completed.stderr)]


def unmatched_cuts(source_cuts: list[float], result_cuts: list[float], tolerance: float) -> list[float]:
    return [value for value in result_cuts if not any(abs(value - source) <= tolerance for source in source_cuts)]


def command_validate(args: argparse.Namespace) -> int:
    source = probe(args.source)
    result = probe(args.result)
    tolerance = args.cut_tolerance_frames / result["fps"]
    source_cuts = cut_candidates(source["path"], args.scene_threshold)
    result_cuts = cut_candidates(result["path"], args.scene_threshold)
    extra_cuts = unmatched_cuts(source_cuts, result_cuts, tolerance)
    duration_error = abs(result["duration"] - source["duration"])
    duration_tolerance = 1.0 / result["fps"]
    aspect_error = abs(result["aspect_ratio"] - source["aspect_ratio"])
    report = {
        "source": source,
        "result": result,
        "checks": {
            "duration_error_seconds": duration_error,
            "duration_tolerance_seconds": duration_tolerance,
            "duration_pass": duration_error <= duration_tolerance + 1e-6,
            "aspect_ratio_error": aspect_error,
            "aspect_ratio_pass": aspect_error <= args.aspect_tolerance,
            "source_cut_candidates": source_cuts,
            "result_cut_candidates": result_cuts,
            "result_only_cut_candidates": extra_cuts,
            "cut_preflight_pass": not extra_cuts,
        },
        "note": "Scene candidates require visual review; fast motion and occlusion can be false positives.",
    }
    report["hard_preflight_pass"] = all([
        report["checks"]["duration_pass"],
        report["checks"]["aspect_ratio_pass"],
        report["checks"]["cut_preflight_pass"],
    ])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["hard_preflight_pass"] else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="plan the nearest legal H3 frame grid")
    plan_parser.add_argument("--source", required=True)
    plan_parser.add_argument("--min-seconds", type=float, default=4.0)
    plan_parser.add_argument("--max-seconds", type=float, default=15.0)
    plan_parser.set_defaults(func=command_plan)

    prepare_parser = subparsers.add_parser("prepare-reference", help="retime a temporary H3 reference")
    prepare_parser.add_argument("--source", required=True)
    prepare_parser.add_argument("--output", required=True)
    prepare_parser.add_argument("--num-frames", required=True, type=int)
    prepare_parser.set_defaults(func=command_prepare)

    conform_parser = subparsers.add_parser("conform-result", help="map an H3 result back to the source timeline")
    conform_parser.add_argument("--source", required=True)
    conform_parser.add_argument("--result", required=True)
    conform_parser.add_argument("--output", required=True)
    conform_parser.set_defaults(func=command_conform)

    validate_parser = subparsers.add_parser("validate", help="run deterministic metadata and cut preflight")
    validate_parser.add_argument("--source", required=True)
    validate_parser.add_argument("--result", required=True)
    validate_parser.add_argument("--scene-threshold", type=float, default=0.35)
    validate_parser.add_argument("--cut-tolerance-frames", type=int, default=2)
    validate_parser.add_argument("--aspect-tolerance", type=float, default=0.001)
    validate_parser.set_defaults(func=command_validate)

    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except (ContractError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
