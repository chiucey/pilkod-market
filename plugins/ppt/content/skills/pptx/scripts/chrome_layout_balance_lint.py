#!/usr/bin/env python3
"""Validate content balance inside template chrome content regions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_IGNORE_ROLES = {
    "title",
    "pageTitle",
    "subtitle",
    "source",
    "footnote",
    "caption",
    "pageNum",
    "footer",
}


def _rect(value: dict[str, Any]) -> dict[str, float] | None:
    try:
        return {
            "x": float(value["x"]),
            "y": float(value["y"]),
            "w": float(value["w"]),
            "h": float(value["h"]),
        }
    except (KeyError, TypeError, ValueError):
        return None


def _intersection(a: dict[str, float], b: dict[str, float]) -> float:
    x_overlap = max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
    y_overlap = max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
    return x_overlap * y_overlap


def _content_regions(profile: dict[str, Any]) -> dict[str, dict[str, float]]:
    raw = profile.get("contentRegions")
    regions: dict[str, dict[str, float]] = {}
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            name = item.get("id") or item.get("name")
            rect = _rect(item.get("region", item))
            if name and rect:
                regions[str(name)] = rect
    elif isinstance(raw, dict):
        for name, item in raw.items():
            if isinstance(item, dict):
                rect = _rect(item.get("region", item))
                if rect:
                    regions[str(name)] = rect

    if "body" not in regions:
        safe_area = _rect(profile.get("safeArea", {}))
        if safe_area:
            regions["body"] = safe_area
    return regions


def _load_slides(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [{"slideNumber": index + 1, "elements": [item]} for index, item in enumerate(data)]
    slides = data.get("slides", [])
    return [slide for slide in slides if isinstance(slide, dict)]


def _bbox(rects: list[dict[str, float]]) -> dict[str, float]:
    min_x = min(rect["x"] for rect in rects)
    min_y = min(rect["y"] for rect in rects)
    max_x = max(rect["x"] + rect["w"] for rect in rects)
    max_y = max(rect["y"] + rect["h"] for rect in rects)
    return {"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y}


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint generated content balance inside chrome regions")
    parser.add_argument("--profile", required=True, help="template chrome profile JSON")
    parser.add_argument("--element-map", required=True, help="mavis-ppt-map JSON")
    parser.add_argument("--region", default="body", help="content region to check")
    parser.add_argument("--ignore-role", action="append", default=[])
    parser.add_argument("--ignore-kind", action="append", default=[])
    parser.add_argument("--min-elements", type=int, default=3)
    parser.add_argument("--max-margin-imbalance-ratio", type=float, default=0.12)
    parser.add_argument("--min-width-utilization", type=float, default=0.82)
    args = parser.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    regions = _content_regions(profile)
    region = regions.get(args.region)
    if not region:
        raise SystemExit(f"content region '{args.region}' is missing from {args.profile}")

    ignore_roles = DEFAULT_IGNORE_ROLES | set(args.ignore_role)
    ignore_kinds = set(args.ignore_kind)
    failures: list[str] = []

    for slide in _load_slides(Path(args.element_map)):
        rects: list[dict[str, float]] = []
        for element in slide.get("elements", []):
            if not isinstance(element, dict):
                continue
            if element.get("role") in ignore_roles or element.get("kind") in ignore_kinds:
                continue
            rect = _rect(element.get("rectIn", element))
            if not rect or _intersection(rect, region) <= 0:
                continue
            rects.append(rect)

        if len(rects) < args.min_elements:
            continue

        bbox = _bbox(rects)
        left_gap = max(0.0, bbox["x"] - region["x"])
        right_gap = max(0.0, region["x"] + region["w"] - (bbox["x"] + bbox["w"]))
        width_utilization = bbox["w"] / max(region["w"], 1e-9)
        margin_imbalance = abs(right_gap - left_gap) / max(region["w"], 1e-9)
        label = f"slide {slide.get('slideNumber', '<unknown>')}"

        if margin_imbalance > args.max_margin_imbalance_ratio:
            failures.append(
                f"{label} content is visually imbalanced in {args.region} "
                f"(leftGap={left_gap:.3f}, rightGap={right_gap:.3f}, "
                f"imbalance={margin_imbalance:.3f}, region={region}, bbox={bbox})"
            )
        if width_utilization < args.min_width_utilization:
            failures.append(
                f"{label} underuses {args.region} width "
                f"(utilization={width_utilization:.3f}, minimum={args.min_width_utilization:.3f}, "
                f"region={region}, bbox={bbox})"
            )

    if failures:
        print("chrome_layout_balance_lint: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)
    print("chrome_layout_balance_lint: PASS")


if __name__ == "__main__":
    main()
