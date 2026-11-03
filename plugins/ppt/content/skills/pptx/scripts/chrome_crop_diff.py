#!/usr/bin/env python3
"""Compare rendered reserved-zone crops against the template chrome reference."""

from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path
from typing import Any


def _load_pillow():
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError as exc:
        raise SystemExit(
            "chrome_crop_diff.py requires Pillow. Run with: "
            "uv run --with pillow chrome_crop_diff.py ..."
        ) from exc
    return Image, ImageChops, ImageStat


def _rect_to_px(zone: dict[str, Any], image_size: tuple[int, int], slide_size: dict[str, float]):
    width_px, height_px = image_size
    slide_w = float(slide_size.get("widthIn") or slide_size.get("w"))
    slide_h = float(slide_size.get("heightIn") or slide_size.get("h"))
    x1 = round(float(zone["x"]) / slide_w * width_px)
    y1 = round(float(zone["y"]) / slide_h * height_px)
    x2 = round((float(zone["x"]) + float(zone["w"])) / slide_w * width_px)
    y2 = round((float(zone["y"]) + float(zone["h"])) / slide_h * height_px)
    return (
        max(0, min(width_px, x1)),
        max(0, min(height_px, y1)),
        max(0, min(width_px, x2)),
        max(0, min(height_px, y2)),
    )


def _expand_inputs(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        matches = glob.glob(value)
        out.extend(matches or [value])
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare template chrome crops")
    parser.add_argument("--profile", required=True, help="template chrome profile JSON")
    parser.add_argument("--reference", help="reference chrome PNG; defaults to profile chrome asset")
    parser.add_argument("--rendered", action="append", required=True, help="rendered slide PNG or glob")
    parser.add_argument("--mean-threshold", type=float, default=3.0)
    parser.add_argument("--changed-ratio-threshold", type=float, default=0.02)
    parser.add_argument("--pixel-threshold", type=int, default=10)
    args = parser.parse_args()

    Image, ImageChops, ImageStat = _load_pillow()
    profile_path = Path(args.profile)
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    slide_size = profile["slideSize"]
    reference_path = args.reference
    if not reference_path:
        asset = profile.get("chrome", {}).get("asset") or profile.get("chromeAsset")
        if not asset:
            raise SystemExit("No --reference provided and profile has no chrome asset")
        reference_path = asset if os.path.isabs(asset) else str(profile_path.parent / asset)

    reference = Image.open(reference_path).convert("RGBA")
    zones = [zone for zone in profile.get("reservedZones", []) if zone.get("compare", True)]
    if not zones:
        raise SystemExit("Profile has no comparable reserved zones")

    failures: list[str] = []
    for rendered_path in _expand_inputs(args.rendered):
        rendered = Image.open(rendered_path).convert("RGBA")
        if rendered.size != reference.size:
            rendered = rendered.resize(reference.size)
        for zone in zones:
            box = _rect_to_px(zone, reference.size, slide_size)
            if box[2] <= box[0] or box[3] <= box[1]:
                continue
            ref_crop = reference.crop(box)
            rendered_crop = rendered.crop(box)
            diff = ImageChops.difference(ref_crop, rendered_crop)
            stat = ImageStat.Stat(diff)
            mean = sum(stat.mean[:3]) / 3
            diff_pixels = 0
            total = max(1, diff.width * diff.height)
            diff_bytes = diff.convert("RGB").tobytes()
            for index in range(0, len(diff_bytes), 3):
                if max(diff_bytes[index : index + 3]) > args.pixel_threshold:
                    diff_pixels += 1
            changed_ratio = diff_pixels / total
            if mean > args.mean_threshold or changed_ratio > args.changed_ratio_threshold:
                failures.append(
                    f"{rendered_path} zone {zone.get('id', '<zone>')} differs "
                    f"(mean={mean:.3f}, changedRatio={changed_ratio:.4f})"
                )

    if failures:
        print("chrome_crop_diff: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)
    print("chrome_crop_diff: PASS")


if __name__ == "__main__":
    main()
