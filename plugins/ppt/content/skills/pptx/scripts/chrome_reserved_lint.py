#!/usr/bin/env python3
"""Validate generated PPT element maps against template chrome reserved zones."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TITLE_ROLES = {"title", "pageTitle", "chapterTitle", "sectionTitle"}
SOURCE_ROLES = {"source", "footnote", "caption"}
FOOTER_ROLES = {"pageNum", "footer"}


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


def _area(rect: dict[str, float]) -> float:
    return max(0.0, rect["w"]) * max(0.0, rect["h"])


def _intersection(a: dict[str, float], b: dict[str, float]) -> float:
    x_overlap = max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
    y_overlap = max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
    return x_overlap * y_overlap


def _inside(inner: dict[str, float], outer: dict[str, float], epsilon: float = 1e-6) -> bool:
    return (
        inner["x"] + epsilon >= outer["x"]
        and inner["y"] + epsilon >= outer["y"]
        and inner["x"] + inner["w"] <= outer["x"] + outer["w"] + epsilon
        and inner["y"] + inner["h"] <= outer["y"] + outer["h"] + epsilon
    )


def _load_elements(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    elements: list[dict[str, Any]] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                elements.append({"slideNumber": item.get("slideNumber"), "element": item})
        return elements
    for slide in data.get("slides", []):
        for element in slide.get("elements", []):
            elements.append({"slideNumber": slide.get("slideNumber"), "element": element})
    return elements


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
    return regions


def _region_for_element(
    element: dict[str, Any], regions: dict[str, dict[str, float]]
) -> tuple[str, dict[str, float]] | None:
    role = element.get("role")
    if role in TITLE_ROLES and "title" in regions:
        return "title", regions["title"]
    if role in SOURCE_ROLES and "source" in regions:
        return "source", regions["source"]
    if role in FOOTER_ROLES and "footer" in regions:
        return "footer", regions["footer"]
    if "body" in regions:
        return "body", regions["body"]
    return next(iter(regions.items()), None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint PPT element maps against chrome zones")
    parser.add_argument("--profile", required=True, help="template chrome profile JSON")
    parser.add_argument("--element-map", required=True, help="mavis-ppt-map JSON")
    parser.add_argument("--ignore-role", action="append", default=[])
    parser.add_argument("--ignore-kind", action="append", default=[])
    parser.add_argument("--no-enforce-safe-area", action="store_true")
    parser.add_argument("--no-enforce-content-regions", action="store_true")
    parser.add_argument("--max-overlap-ratio", type=float, default=0.0)
    args = parser.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    zones = [_rect(zone) | {"id": zone.get("id", "reserved-zone")} for zone in profile.get("reservedZones", []) if _rect(zone)]
    safe_area = _rect(profile.get("safeArea", {}))
    content_regions = _content_regions(profile)
    ignore_roles = set(args.ignore_role)
    ignore_kinds = set(args.ignore_kind)

    failures: list[str] = []
    for item in _load_elements(Path(args.element_map)):
        element = item["element"]
        if element.get("role") in ignore_roles or element.get("kind") in ignore_kinds:
            continue
        rect = _rect(element.get("rectIn", element))
        if not rect:
            continue
        label = f"slide {item.get('slideNumber')} {element.get('elementId', '<unknown>')}"
        elem_area = max(_area(rect), 1e-9)
        for zone in zones:
            overlap_ratio = _intersection(rect, zone) / elem_area
            if overlap_ratio > args.max_overlap_ratio:
                failures.append(
                    f"{label} overlaps reserved zone {zone['id']} "
                    f"(ratio={overlap_ratio:.4f}, rect={rect})"
                )
        if (
            content_regions
            and not args.no_enforce_content_regions
            and not args.no_enforce_safe_area
        ):
            region_match = _region_for_element(element, content_regions)
            if region_match:
                region_name, region = region_match
                if not _inside(rect, region):
                    failures.append(
                        f"{label} is outside contentRegion {region_name} "
                        f"(rect={rect}, region={region})"
                    )
            continue
        if safe_area and not args.no_enforce_safe_area and not _inside(rect, safe_area):
            failures.append(f"{label} is outside safeArea (rect={rect}, safeArea={safe_area})")

    if failures:
        print("chrome_reserved_lint: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)
    print("chrome_reserved_lint: PASS")


if __name__ == "__main__":
    main()
