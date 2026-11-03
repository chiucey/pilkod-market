#!/usr/bin/env python3
"""Create a Template Imitation chrome profile from a rendered template image.

The profile is intentionally simple JSON: a full-slide chrome asset, reserved
zones in PptxGenJS inches, and named content regions. Vision can help choose the
source slide, but generated slide code should consume this structured profile.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import zipfile
from collections import deque
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

EMU_PER_INCH = 914400
PRESENTATION_NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}


def _round(value: float) -> float:
    return round(value, 4)


def _parse_rect(value: str, field: str) -> dict[str, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise ValueError(f"{field} must be formatted as x,y,w,h")
    x, y, w, h = [float(part) for part in parts]
    return {"x": _round(x), "y": _round(y), "w": _round(w), "h": _round(h)}


def _parse_reserved_zone(value: str) -> dict[str, Any]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) not in (5, 6):
        raise ValueError("reserved zone must be formatted as id,x,y,w,h[,compare]")
    zone = {
        "id": parts[0],
        "source": "manual",
        **_parse_rect(",".join(parts[1:5]), "reserved zone"),
    }
    if len(parts) == 6:
        zone["compare"] = parts[5].lower() not in {"0", "false", "no", "skip"}
    return zone


def _parse_content_region(value: str) -> dict[str, Any]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) not in (5, 6):
        raise ValueError("content region must be formatted as id,x,y,w,h[,role|role...]")
    region: dict[str, Any] = {
        "id": parts[0],
        "source": "manual",
        **_parse_rect(",".join(parts[1:5]), "content region"),
    }
    if len(parts) == 6 and parts[5]:
        region["roles"] = [role.strip() for role in parts[5].split("|") if role.strip()]
    return region


def _read_slide_size_from_pptx(template_path: str) -> tuple[float, float]:
    with zipfile.ZipFile(template_path, "r") as zf:
        root = ET.fromstring(zf.read("ppt/presentation.xml"))
    sld_sz = root.find("p:sldSz", PRESENTATION_NS)
    if sld_sz is None:
        raise ValueError("ppt/presentation.xml does not contain p:sldSz")
    cx = int(sld_sz.attrib["cx"])
    cy = int(sld_sz.attrib["cy"])
    return cx / EMU_PER_INCH, cy / EMU_PER_INCH


def _parse_slide_size(value: str) -> tuple[float, float]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 2:
        raise ValueError("slide size must be formatted as width,height")
    return float(parts[0]), float(parts[1])


def _load_image(path: str):
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit(
            "template_chrome_profile.py --auto-red-zones requires Pillow. "
            "Run with: uv run --with pillow template_chrome_profile.py ..."
        ) from exc
    return Image.open(path).convert("RGBA")


def _red_mask(pixel: tuple[int, int, int, int]) -> bool:
    r, g, b, a = pixel
    return a > 32 and r >= 140 and g <= 110 and b <= 110 and r >= max(g, b) * 1.35


def _component_boxes(mask: list[list[bool]], min_area: int) -> list[tuple[int, int, int, int, int]]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    seen = [[False] * width for _ in range(height)]
    boxes: list[tuple[int, int, int, int, int]] = []
    for y in range(height):
        for x in range(width):
            if seen[y][x] or not mask[y][x]:
                continue
            seen[y][x] = True
            queue: deque[tuple[int, int]] = deque([(x, y)])
            min_x = max_x = x
            min_y = max_y = y
            area = 0
            while queue:
                cx, cy = queue.popleft()
                area += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < width and 0 <= ny < height and not seen[ny][nx] and mask[ny][nx]:
                        seen[ny][nx] = True
                        queue.append((nx, ny))
            if area >= min_area:
                boxes.append((min_x, min_y, max_x + 1, max_y + 1, area))
    return boxes


def _merge_close_boxes(
    boxes: list[tuple[int, int, int, int, int]], gap_px: int
) -> list[tuple[int, int, int, int, int]]:
    merged = boxes[:]
    changed = True
    while changed:
        changed = False
        result: list[tuple[int, int, int, int, int]] = []
        used = [False] * len(merged)
        for i, box in enumerate(merged):
            if used[i]:
                continue
            x1, y1, x2, y2, area = box
            used[i] = True
            for j in range(i + 1, len(merged)):
                if used[j]:
                    continue
                ox1, oy1, ox2, oy2, oarea = merged[j]
                separated = (
                    ox1 > x2 + gap_px
                    or x1 > ox2 + gap_px
                    or oy1 > y2 + gap_px
                    or y1 > oy2 + gap_px
                )
                if not separated:
                    x1, y1 = min(x1, ox1), min(y1, oy1)
                    x2, y2 = max(x2, ox2), max(y2, oy2)
                    area += oarea
                    used[j] = True
                    changed = True
            result.append((x1, y1, x2, y2, area))
        merged = result
    return merged


def _detect_red_zones(
    image_path: str,
    slide_w: float,
    slide_h: float,
    min_area: int,
    merge_gap_px: int,
) -> list[dict[str, Any]]:
    image = _load_image(image_path)
    width, height = image.size
    pixels = image.load()
    mask = [[_red_mask(pixels[x, y]) for x in range(width)] for y in range(height)]
    boxes = _merge_close_boxes(_component_boxes(mask, min_area), merge_gap_px)
    zones: list[dict[str, Any]] = []
    for index, (x1, y1, x2, y2, area) in enumerate(boxes, start=1):
        zones.append(
            {
                "id": f"auto-red-{index}",
                "source": "auto-red",
                "pixelBox": {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1},
                "x": _round(x1 / width * slide_w),
                "y": _round(y1 / height * slide_h),
                "w": _round((x2 - x1) / width * slide_w),
                "h": _round((y2 - y1) / height * slide_h),
                "areaPx": area,
            }
        )
    return zones


def _infer_safe_area(
    slide_w: float, slide_h: float, zones: list[dict[str, Any]]
) -> dict[str, float]:
    top = 0.4
    bottom = slide_h - 0.4
    for zone in zones:
        center_y = zone["y"] + zone["h"] / 2
        if center_y < slide_h * 0.35:
            top = max(top, zone["y"] + zone["h"] + 0.15)
        if center_y > slide_h * 0.7:
            bottom = min(bottom, zone["y"] - 0.15)
    top = min(top, slide_h - 1.0)
    bottom = max(bottom, top + 1.0)
    return {
        "x": _round(0.65),
        "y": _round(top),
        "w": _round(slide_w - 1.3),
        "h": _round(bottom - top),
        "source": "inferred",
    }


def _vertical_overlap(y: float, h: float, zone: dict[str, Any]) -> float:
    return max(0.0, min(y + h, zone["y"] + zone["h"]) - max(y, zone["y"]))


def _largest_free_rect(
    slide_w: float,
    y: float,
    h: float,
    zones: list[dict[str, Any]],
    margin_x: float,
    gap: float = 0.15,
) -> dict[str, float]:
    left = max(0.0, margin_x)
    right = min(slide_w, slide_w - margin_x)
    intervals = [(left, right)]
    for zone in zones:
        if _vertical_overlap(y, h, zone) <= 0:
            continue
        block_left = max(left, zone["x"] - gap)
        block_right = min(right, zone["x"] + zone["w"] + gap)
        if block_right <= block_left:
            continue
        next_intervals: list[tuple[float, float]] = []
        for start, end in intervals:
            if block_right <= start or block_left >= end:
                next_intervals.append((start, end))
                continue
            if start < block_left:
                next_intervals.append((start, block_left))
            if block_right < end:
                next_intervals.append((block_right, end))
        intervals = next_intervals
    if not intervals:
        return {"x": _round(left), "y": _round(y), "w": _round(max(0.0, right - left)), "h": _round(h)}
    start, end = max(intervals, key=lambda item: item[1] - item[0])
    return {"x": _round(start), "y": _round(y), "w": _round(max(0.0, end - start)), "h": _round(h)}


def _infer_content_regions(
    slide_w: float,
    slide_h: float,
    zones: list[dict[str, Any]],
    safe_area: dict[str, float],
) -> dict[str, dict[str, Any]]:
    margin_x = min(max(float(safe_area.get("x", 0.65)), 0.35), 0.85)
    safe_y = float(safe_area.get("y", 0.4))
    safe_bottom = float(safe_area.get("y", 0.4)) + float(safe_area.get("h", slide_h - 0.8))

    header_zones = [zone for zone in zones if zone["y"] + zone["h"] / 2 < slide_h * 0.35]
    footer_zones = [zone for zone in zones if zone["y"] + zone["h"] / 2 > slide_h * 0.7]

    header_bottom = max((zone["y"] + zone["h"] for zone in header_zones), default=0.0)
    footer_top = min((zone["y"] for zone in footer_zones), default=slide_h)

    title_y = min(safe_y, max(0.18, header_bottom))
    title_h = max(0.45, min(0.9, max(0.6, header_bottom + 0.12 - title_y)))
    title_region = _largest_free_rect(slide_w, title_y, title_h, zones, margin_x)
    title_region["source"] = "inferred"

    body_y = max(safe_y, header_bottom + 0.2 if header_zones else safe_y)
    body_bottom = min(safe_bottom, footer_top - 0.15 if footer_zones else safe_bottom)
    if body_bottom <= body_y:
        body_y = min(max(safe_y, 0.9), slide_h - 1.0)
        body_bottom = max(body_y + 1.0, min(slide_h - 0.45, safe_bottom))
    body_region = _largest_free_rect(slide_w, body_y, body_bottom - body_y, zones, margin_x)
    body_region["source"] = "inferred"

    source_h = min(0.28, max(0.18, body_region["h"] * 0.08))
    source_y = max(body_region["y"], body_region["y"] + body_region["h"] - source_h)
    source_region = {
        "x": body_region["x"],
        "y": _round(source_y),
        "w": _round(body_region["w"]),
        "h": _round(source_h),
        "source": "inferred",
    }

    return {
        "title": title_region,
        "body": body_region,
        "source": source_region,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a template chrome profile JSON")
    parser.add_argument("--template", help="Template PPTX path, used to read slide size")
    parser.add_argument("--slide-size", help="Fallback slide size in inches: width,height")
    parser.add_argument("--chrome-image", help="Rendered full-slide chrome image to reuse")
    parser.add_argument("--chrome-source-slide", help="Template slide/page used to derive chrome")
    parser.add_argument(
        "--chrome-source-method",
        default="rendered-template-image",
        help="How the chrome asset was derived, e.g. rendered-template-image or masked-template-render",
    )
    parser.add_argument("--chrome-source-note", help="Free-form chrome provenance note")
    parser.add_argument("--out", required=True, help="Output template chrome profile JSON")
    parser.add_argument("--asset-dir", default="assets", help="Asset directory relative to profile")
    parser.add_argument("--no-copy-chrome-asset", action="store_true")
    parser.add_argument("--safe-area", help="Manual safe area in inches: x,y,w,h")
    parser.add_argument(
        "--content-region",
        action="append",
        default=[],
        help="Manual content region in inches: id,x,y,w,h[,role|role...]",
    )
    parser.add_argument(
        "--reserved-zone",
        action="append",
        default=[],
        help="Manual reserved zone in inches: id,x,y,w,h[,compare]",
    )
    parser.add_argument("--auto-red-zones", action="store_true")
    parser.add_argument("--red-min-area-px", type=int, default=120)
    parser.add_argument("--red-merge-gap-px", type=int, default=24)
    args = parser.parse_args()

    if args.template:
        slide_w, slide_h = _read_slide_size_from_pptx(args.template)
    elif args.slide_size:
        slide_w, slide_h = _parse_slide_size(args.slide_size)
    else:
        raise SystemExit("Provide --template or --slide-size")

    out_path = Path(args.out)
    out_dir = out_path.parent
    zones = [_parse_reserved_zone(value) for value in args.reserved_zone]

    if args.auto_red_zones:
        if not args.chrome_image:
            raise SystemExit("--auto-red-zones requires --chrome-image")
        zones.extend(
            _detect_red_zones(
                args.chrome_image,
                slide_w,
                slide_h,
                args.red_min_area_px,
                args.red_merge_gap_px,
            )
        )

    chrome: dict[str, Any] | None = None
    if args.chrome_image:
        chrome_image = Path(args.chrome_image)
        if args.no_copy_chrome_asset:
            asset_path = chrome_image
        else:
            asset_dir = out_dir / args.asset_dir
            asset_dir.mkdir(parents=True, exist_ok=True)
            asset_path = asset_dir / chrome_image.name
            if os.path.abspath(chrome_image) != os.path.abspath(asset_path):
                shutil.copy2(chrome_image, asset_path)
        chrome = {
            "kind": "full-slide-image",
            "asset": os.path.relpath(asset_path, out_dir),
            "source": {
                "image": str(chrome_image),
                "templateSlide": args.chrome_source_slide,
                "method": args.chrome_source_method,
                "note": args.chrome_source_note,
            },
            "placement": {"x": 0, "y": 0, "w": _round(slide_w), "h": _round(slide_h)},
            "opaque": True,
        }

    safe_area = _parse_rect(args.safe_area, "safe area") if args.safe_area else _infer_safe_area(slide_w, slide_h, zones)
    content_regions = _infer_content_regions(slide_w, slide_h, zones, safe_area)
    for region in [_parse_content_region(value) for value in args.content_region]:
        region_id = region.pop("id")
        content_regions[region_id] = region

    profile: dict[str, Any] = {
        "schema": "mavis.ppt_template_chrome.v1",
        "sourceTemplate": args.template,
        "slideSize": {"widthIn": _round(slide_w), "heightIn": _round(slide_h)},
        "chrome": chrome,
        "reservedZones": zones,
        "safeArea": safe_area,
        "contentRegions": content_regions,
        "rules": [
            "Add the full-slide chrome image before any content elements.",
            "Place meaningful content inside the appropriate named contentRegions entry.",
            "Use body/title/source contentRegions for layout; do not shrink the whole slide just because a logo appears in one band.",
            "Do not overlap reservedZones unless the element is part of the chrome itself.",
            "Use rendered crop diff QA to verify reserved zones are unchanged.",
            "Do not redraw or approximate template logo/ribbon/footer artwork.",
        ],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote template chrome profile: {out_path}")


if __name__ == "__main__":
    main()
