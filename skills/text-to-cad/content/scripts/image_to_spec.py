#!/usr/bin/env python3
"""
image_to_spec.py v2.0 - Image → DXF Spec JSON Converter (text-to-cad v5.0)
=========================================================================

v2.0 UPGRADES:
  1. BUG FIX: Arc center detection now uses actual contour moments
     (was hardcoded to [0,0] in v1.0)
  2. NEW: LLM Visual Semantic Layer — generates prompts for WorkBuddy Agent
     to add engineering context (entity recognition, annotations)
  3. NEW: Adaptive parameter tuning based on image characteristics
  4. NEW: Contour hierarchy analysis for nested shapes
  5. NEW: Line intersection detection for corner points

Architecture:
  Image → OpenCV Detection → Geometric Primitives → JSON Spec
                                             ↓
                                    LLM Semantic Layer (NEW)
                                             ↓
                                    Engineering Context
                                    (what is this shape?
                                     what should be annotated?)

Usage:
  python image_to_spec.py input.png -o spec.json
  python image_to_spec.py input.png --semantic   # Include LLM semantic layer
  python image_to_spec.py input.png --auto-tune  # Auto-adjust parameters

Dependencies: pip install opencv-python Pillow numpy ezdxf
"""

import argparse
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

# ─────────────────────────────────────────────────────────────────────────────
#  Core: Image → Spec
# ─────────────────────────────────────────────────────────────────────────────

def image_to_spec(
    image_path: str = None,
    np_image: np.ndarray = None,
    *,
    dpi: int = 300,
    min_line_length: float = 30,
    min_circle_radius: float = 8,
    simplify_epsilon: float = 3.0,
    detection_mode: str = "auto",
    description: str = "Image-derived drawing",
    enable_semantic: bool = False,
    auto_tune: bool = False,
) -> dict:
    """
    Convert an image to a DXF Spec JSON.

    v2.0: Added enable_semantic (LLM context) and auto_tune parameters.
    """
    # ── 1. Load image ────────────────────────────────────────────────────
    if np_image is not None:
        gray = _to_grayscale(np_image)
        orig_h, orig_w = np_image.shape[:2]
    else:
        pil_img = Image.open(image_path)
        pil_img = pil_img.convert("L")
        orig_w, orig_h = pil_img.size
        gray = np.array(pil_img)
        np_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    px_per_mm = float(dpi) / 25.4

    # ── 2. Auto-tune parameters based on image (v2.0 NEW) ───────────────
    if auto_tune:
        min_line_length, min_circle_radius, simplify_epsilon = \
            _auto_tune_params(gray, px_per_mm)

    # ── 3. Preprocess ───────────────────────────────────────────────────
    blurred = cv2.GaussianBlur(gray, (5, 5), 1.5)
    thresh_type = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    binary = cv2.adaptiveThreshold(
        blurred, 255, thresh_type, cv2.THRESH_BINARY_INV, 11, 4
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

    # ── 4. Edge detection ───────────────────────────────────────────────
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    # ── 5. Detect lines ─────────────────────────────────────────────────
    lines = []
    if detection_mode in ("auto", "all", "line"):
        raw_lines = cv2.HoughLinesP(
            edges, 1, math.pi / 180,
            threshold=30,
            minLineLength=int(min_line_length * px_per_mm),
            maxLineGap=15,
        )
        if raw_lines is not None:
            merged = _merge_collinear_lines(raw_lines, px_per_mm)
            lines = [
                {
                    "type": "line",
                    "start": [round(pt[0] / px_per_mm, 2),
                               round((orig_h - pt[1]) / px_per_mm, 2)],
                    "end":   [round(pt[2] / px_per_mm, 2),
                               round((orig_h - pt[3]) / px_per_mm, 2)],
                    "layer": "DETECTED",
                }
                for pt in merged
                if _line_length(pt) >= min_line_length
            ]

    # ── 6. Detect circles ───────────────────────────────────────────────
    circles = []
    if detection_mode in ("auto", "all", "circle"):
        raw_circles = cv2.HoughCircles(
            blurred, cv2.HOUGH_GRADIENT, dp=1.2,
            minDist=int(min_circle_radius * px_per_mm * 1.5),
            param1=60, param2=30,
            minRadius=int(min_circle_radius * px_per_mm),
            maxRadius=int(200 * px_per_mm),
        )
        if raw_circles is not None:
            merged_circles = _merge_nearby_circles(raw_circles[0])
            circles = [
                {
                    "type": "circle",
                    "center": [
                        round(cx / px_per_mm, 2),
                        round((orig_h - cy) / px_per_mm, 2),
                    ],
                    "radius": round(r / px_per_mm, 2),
                    "layer": "DETECTED",
                }
                for (cx, cy, r) in merged_circles
                if r / px_per_mm >= min_circle_radius
            ]

    # ── 7. Detect contours / polygons ──────────────────────────────────
    contours_raw, hierarchy = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    polygons = []
    for idx, cnt in enumerate(contours_raw):
        area = cv2.contourArea(cnt)
        if area < 100:
            continue
        perimeter = cv2.arcLength(cnt, closed=True)
        if perimeter < 1:
            continue

        epsilon = simplify_epsilon * px_per_mm
        approx = cv2.approxPolyDP(cnt, epsilon, closed=True)
        n_vertices = len(approx)

        pts_px = approx.reshape(-1, 2)
        pts_mm = [
            [round(x / px_per_mm, 2), round((orig_h - y) / px_per_mm, 2)]
            for (x, y) in pts_px
        ]

        # Check hierarchy for nested shapes (v2.0)
        is_nested = False
        if hierarchy is not None:
            parent = hierarchy[0][idx][3]
            is_nested = parent >= 0

        if n_vertices == 4:
            (x, y, w, h) = cv2.boundingRect(cnt)
            aspect = max(w, h) / (min(w, h) + 1e-9)
            if 0.85 <= aspect <= 1.15:
                polygons.append({
                    "type": "rectangle",
                    "origin": [round(x / px_per_mm, 2),
                                round((orig_h - y - h) / px_per_mm, 2)],
                    "width":  round(w / px_per_mm, 2),
                    "height": round(h / px_per_mm, 2),
                    "layer": "DETECTED",
                    "_nested": is_nested,
                })
            else:
                polygons.append({
                    "type": "polyline",
                    "points": pts_mm + [pts_mm[0]],
                    "closed": True,
                    "layer": "DETECTED",
                })
        elif n_vertices >= 5:
            (cx_px, cy_px), (ma, MA), angle = cv2.fitEllipse(cnt)
            a, b = MA / 2 / px_per_mm, ma / 2 / px_per_mm
            cx_mm = round(cx_px / px_per_mm, 2)
            cy_mm = round((orig_h - cy_px) / px_per_mm, 2)
            if 0.3 <= b / (a + 1e-9) <= 1.0:
                polygons.append({
                    "type": "ellipse",
                    "center": [cx_mm, cy_mm],
                    "major_radius": round(a, 2),
                    "minor_radius": round(b, 2),
                    "rotation": round(angle, 1),
                    "layer": "DETECTED",
                })
            else:
                avg_r = (a + b) / 2
                polygons.append({
                    "type": "circle",
                    "center": [cx_mm, cy_mm],
                    "radius": round(avg_r, 2),
                    "layer": "DETECTED",
                })
        else:
            polygons.append({
                "type": "polyline",
                "points": pts_mm + [pts_mm[0]],
                "closed": n_vertices == len(pts_mm) and cv2.isContourConvex(approx),
                "layer": "DETECTED",
            })

    # ── 8. Detect arcs (BUG FIXED in v2.0) ─────────────────────────────
    # v1.0 BUG: center was hardcoded to [0,0]
    # v2.0 FIX: Use contour moments to compute actual center
    arcs = []
    for cnt in contours_raw:
        arc_len = cv2.arcLength(cnt, closed=False)
        if 20 < arc_len < 500:
            M = cv2.moments(cnt)
            if M["m00"] > 0:
                # v2.0 FIX: Compute actual center from moments
                actual_cx = M["m10"] / M["m00"]
                actual_cy = M["m01"] / M["m00"]

                # Convert to mm
                cx_mm = round(actual_cx / px_per_mm, 2)
                cy_mm = round((orig_h - actual_cy) / px_per_mm, 2)

                # Compute radius from arc length (approximation for partial arcs)
                approx_radius = arc_len / (2 * math.pi)

                # Try to fit an ellipse for better radius estimation
                if len(cnt) >= 5:
                    try:
                        (ecx, ecy), (ma, MA), angle = cv2.fitEllipse(cnt)
                        approx_radius = (ma + MA) / 4  # average of semi-axes
                        cx_mm = round(ecx / px_per_mm, 2)
                        cy_mm = round((orig_h - ecy) / px_per_mm, 2)
                    except cv2.error:
                        pass  # Keep moment-based center

                arcs.append({
                    "type": "arc",
                    "center": [cx_mm, cy_mm],
                    "radius": round(approx_radius, 2),
                    "start_angle": 0,
                    "end_angle": 180,
                    "layer": "DETECTED",
                })

    # ── 9. Line intersection detection (v2.0 NEW) ──────────────────────
    intersections = _detect_intersections(lines)

    # ── 10. Assemble spec ───────────────────────────────────────────────
    all_entities = lines + circles + polygons + arcs

    # Add intersection points as optional markers
    for pt in intersections[:20]:  # Limit to top 20
        all_entities.append({
            "type": "circle",
            "center": pt,
            "radius": 1.0,
            "layer": "CENTER",
            "_annotation": "intersection",
        })

    if not all_entities:
        all_entities = [
            {
                "type": "rectangle",
                "origin": [0, 0],
                "width":  round(orig_w / px_per_mm, 1),
                "height": round(orig_h / px_per_mm, 1),
                "layer": "OUTLINE",
            }
        ]

    spec = _to_python_types({
        "dxf_version": "R2010",
        "description": description,
        "layers": [
            {"name": "DETECTED", "color": 1},
            {"name": "CENTER",   "color": 4, "linetype": "CENTER"},
            {"name": "DIM",       "color": 3},
            {"name": "TEXT",      "color": 2},
            {"name": "OUTLINE",   "color": 7},
        ],
        "entities": all_entities,
        "_meta": {
            "source_image": image_path or "numpy_array",
            "image_size_px": [orig_w, orig_h],
            "dpi": dpi,
            "px_per_mm": round(px_per_mm, 2),
            "detection_stats": {
                "lines": len(lines),
                "circles": len(circles),
                "polygons": len(polygons),
                "arcs": len(arcs),
                "intersections": len(intersections),
                "total": len(all_entities),
            },
        },
    })

    # ── 11. LLM Semantic Layer (v2.0 NEW) ─────────────────────────────
    if enable_semantic:
        spec["_semantic"] = _generate_semantic_context(spec, description)

    return spec


# ─────────────────────────────────────────────────────────────────────────────
#  v2.0 NEW: LLM Visual Semantic Context
# ─────────────────────────────────────────────────────────────────────────────

def _generate_semantic_context(spec: dict, description: str) -> dict:
    """
    Generate context for LLM to add engineering semantics.

    This doesn't call the LLM directly — it prepares the data structure
    that the WorkBuddy LLM Agent uses to understand what the image contains.
    """
    stats = spec.get("_meta", {}).get("detection_stats", {})
    entities = spec.get("entities", [])

    # Analyze composition
    has_circles = stats.get("circles", 0) > 0
    has_lines = stats.get("lines", 0) > 0
    has_rects = any(e["type"] == "rectangle" for e in entities)
    has_arcs = stats.get("arcs", 0) > 0

    # Heuristic: guess what type of drawing this might be
    possible_types = []
    if has_circles and has_lines:
        if stats["circles"] > 3 and stats["lines"] > 5:
            possible_types.extend(["flange", "bearing", "pump"])
        elif stats["circles"] >= 1 and stats["lines"] >= 2:
            possible_types.extend(["shaft", "hole_pattern", "gear"])
    if has_rects and not has_circles:
        possible_types.extend(["architectural", "floor_plan"])
    if stats["lines"] > 10 and stats["circles"] == 0:
        possible_types.extend(["schematic", "wiring_diagram"])
    if has_arcs:
        possible_types.extend(["spring", "cam", "door_arc"])

    # Calculate bounding box
    xs = []
    ys = []
    for e in entities:
        if e["type"] == "line":
            xs.extend([e["start"][0], e["end"][0]])
            ys.extend([e["start"][1], e["end"][1]])
        elif e["type"] in ("circle", "arc"):
            cx, cy = e["center"]
            r = e.get("radius", 0)
            xs.extend([cx - r, cx + r])
            ys.extend([cy - r, cy + r])
        elif e["type"] == "rectangle":
            x, y = e["origin"]
            xs.extend([x, x + e["width"]])
            ys.extend([y, y + e["height"]])

    bbox = {
        "x_min": round(min(xs), 1) if xs else 0,
        "x_max": round(max(xs), 1) if xs else 100,
        "y_min": round(min(ys), 1) if ys else 0,
        "y_max": round(max(ys), 1) if ys else 100,
        "width": round(max(xs) - min(xs), 1) if xs else 100,
        "height": round(max(ys) - min(ys), 1) if ys else 100,
    } if xs and ys else {}

    # Generate LLM prompt for semantic enrichment
    llm_prompt = f'''=== Visual Semantic Enrichment Request ===

Image Analysis Results:
  Lines: {stats.get("lines", 0)}
  Circles: {stats.get("circles", 0)}
  Polygons: {stats.get("polygons", 0)}
  Arcs: {stats.get("arcs", 0)}
  Bounding Box: {bbox.get("width", "?")} x {bbox.get("height", "?")} mm

Possible Drawing Types: {possible_types}

Description: {description}

Task for LLM Agent:
  1. Review the detected geometric primitives
  2. Identify what engineering object this might represent
  3. Add semantic annotations (labels, dimensions, notes)
  4. If a type is recognized but not in our entity system,
     use evolution_engine.py to generate a new drawing function
  5. Enhance the spec with proper layers and engineering context
'''

    return {
        "possible_types": possible_types,
        "bounding_box": bbox,
        "composition": {
            "has_circles": has_circles,
            "has_lines": has_lines,
            "has_rectangles": has_rects,
            "has_arcs": has_arcs,
        },
        "llm_prompt": llm_prompt,
        "confidence": round(len(possible_types) / max(len(set(possible_types)), 1), 2),
    }


def _auto_tune_params(gray: np.ndarray, px_per_mm: float) -> tuple:
    """Auto-tune detection parameters based on image characteristics."""
    h, w = gray.shape
    area_mm = (w / px_per_mm) * (h / px_per_mm)

    # Larger images → more detail → smaller thresholds
    if area_mm > 500 * 500:
        return (15, 4, 2.0)
    elif area_mm > 200 * 200:
        return (25, 6, 2.5)
    else:
        return (30, 8, 3.0)


def _detect_intersections(lines: list, tol: float = 5.0) -> list:
    """Detect line-line intersection points (v2.0 NEW)."""
    intersections = []
    line_data = []
    for l in lines:
        if l["type"] == "line":
            line_data.append((l["start"], l["end"]))

    for i in range(len(line_data)):
        for j in range(i + 1, min(len(line_data), i + 20)):
            pt = _line_intersection(line_data[i], line_data[j])
            if pt:
                # Check if this intersection is near existing ones
                is_dup = any(
                    math.sqrt((pt[0] - ip[0])**2 + (pt[1] - ip[1])**2) < tol
                    for ip in intersections
                )
                if not is_dup:
                    intersections.append(pt)

    return intersections


def _line_intersection(line1: tuple, line2: tuple) -> Optional[tuple]:
    """Calculate intersection point of two line segments."""
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-10:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return (round(ix, 2), round(iy, 2))
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers (kept from v1.0)
# ─────────────────────────────────────────────────────────────────────────────

def _to_python_types(obj):
    import numbers
    if isinstance(obj, dict):
        return {k: _to_python_types(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_python_types(x) for x in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, numbers.Integral):
        return int(obj)
    if isinstance(obj, numbers.Real):
        return float(obj)
    return obj


def _to_grayscale(np_image: np.ndarray) -> np.ndarray:
    if len(np_image.shape) == 2:
        return np_image
    if np_image.shape[2] == 4:
        return cv2.cvtColor(np_image, cv2.COLOR_BGRA2GRAY)
    return cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)


def _line_length(pt) -> float:
    return math.sqrt((pt[2] - pt[0]) ** 2 + (pt[3] - pt[1]) ** 2)


def _merge_collinear_lines(lines, px_per_mm: float, angle_tol: float = 3.0,
                            gap_tol: float = 20.0) -> list:
    if lines is None or len(lines) == 0:
        return []
    merged = []
    used = set()
    pts = [(l[0][0], l[0][1], l[0][2], l[0][3]) for l in lines]
    for i, p1 in enumerate(pts):
        if i in used:
            continue
        group = [p1]
        angle1 = math.degrees(math.atan2(p1[3] - p1[1], p1[2] - p1[0]))
        for j, p2 in enumerate(pts[i + 1:], i + 1):
            if j in used:
                continue
            angle2 = math.degrees(math.atan2(p2[3] - p2[1], p2[2] - p2[0]))
            if abs(angle1 - angle2) > angle_tol:
                continue
            dist = _point_line_distance(p2[:2], p1) + _point_line_distance(p2[2:], p1)
            if dist < gap_tol * px_per_mm:
                group.append(p2)
                used.add(j)
        merged.append(group[0])
    return [g for g in merged]


def _merge_nearby_circles(circles: np.ndarray, dist_tol: float = 0.5) -> list:
    if len(circles) == 0:
        return []
    result = []
    used = set()
    for i, (cx, cy, r) in enumerate(circles):
        if i in used:
            continue
        group = [(cx, cy, r)]
        for j, (cx2, cy2, r2) in enumerate(circles[i + 1:], i + 1):
            if j in used:
                continue
            if math.sqrt((cx - cx2) ** 2 + (cy - cy2) ** 2) < dist_tol * r:
                group.append((cx2, cy2, r2))
                used.add(j)
        result.append(tuple(
            sum(g[k] for g in group) / len(group) for k in range(3)
        ))
    return result


def _point_line_distance(point, line_pt) -> float:
    x0, y0 = point
    x1, y1, x2, y2 = line_pt
    A = x0 - x1; B = y0 - y1
    C = x2 - x1; D = y2 - y1
    dot = A * C + B * D
    len_sq = C * C + D * D + 1e-9
    return abs(dot) / math.sqrt(len_sq)


# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Image → DXF Spec v2.0")
    ap.add_argument("image", nargs="?", help="Input image file")
    ap.add_argument("-o", "--output", default=None, help="Output spec JSON")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--min-line", type=float, default=30)
    ap.add_argument("--min-circle", type=float, default=8)
    ap.add_argument("--simplify", type=float, default=3.0)
    ap.add_argument("--mode", default="auto",
                    choices=["auto", "all", "line", "circle", "contour"])
    ap.add_argument("--semantic", action="store_true",
                    help="Enable LLM visual semantic layer")
    ap.add_argument("--auto-tune", action="store_true",
                    help="Auto-tune detection parameters")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    if args.demo:
        spec = _generate_demo_spec()
    elif args.image:
        spec = image_to_spec(
            args.image, dpi=args.dpi,
            min_line_length=args.min_line,
            min_circle_radius=args.min_circle,
            simplify_epsilon=args.simplify,
            detection_mode=args.mode,
            description=f"Derived from {Path(args.image).name}",
            enable_semantic=args.semantic,
            auto_tune=args.auto_tune,
        )
    else:
        ap.print_help()
        sys.exit(1)

    out_path = args.output or (
        args.image.replace(Path(args.image).suffix, "_spec.json")
        if args.image else "demo_spec.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(_to_python_types(spec), f, indent=2, ensure_ascii=False)
    print(f"[OK] Spec written to: {out_path}")
    stats = spec.get("_meta", {}).get("detection_stats", {})
    print(f"[INFO] Lines: {stats.get('lines',0)}, "
          f"Circles: {stats.get('circles',0)}, "
          f"Polygons: {stats.get('polygons',0)}, "
          f"Arcs: {stats.get('arcs',0)}, "
          f"Total: {stats.get('total',0)}")

    if args.semantic and "_semantic" in spec:
        sem = spec["_semantic"]
        print(f"[SEMANTIC] Possible types: {sem['possible_types']}")
        print(f"[SEMANTIC] LLM prompt generated for enrichment")


def _generate_demo_spec() -> dict:
    return {
        "dxf_version": "R2010",
        "description": "Demo v2.0: synthetic shapes with arc fix",
        "layers": [
            {"name": "DETECTED", "color": 1},
            {"name": "CENTER",   "color": 4, "linetype": "CENTER"},
            {"name": "OUTLINE",  "color": 7},
        ],
        "entities": [
            {"type": "rectangle", "origin": [0, 0],     "width": 100, "height": 80},
            {"type": "circle",    "center": [50, 40],    "radius": 20},
            {"type": "circle",    "center": [15, 15],    "radius": 5},
            {"type": "circle",    "center": [85, 15],    "radius": 5},
            {"type": "circle",    "center": [15, 65],    "radius": 5},
            {"type": "circle",    "center": [85, 65],    "radius": 5},
            {"type": "line",      "start": [30, 40],     "end": [70, 40]},
            {"type": "line",      "start": [50, 20],     "end": [50, 60]},
            {"type": "arc",       "center": [50, 40],    "radius": 35,
             "start_angle": 0, "end_angle": 180},
        ],
        "_meta": {
            "source_image": "demo",
            "detection_stats": {"lines": 2, "circles": 5, "polygons": 1,
                                "arcs": 1, "total": 9},
        },
    }


if __name__ == "__main__":
    main()
