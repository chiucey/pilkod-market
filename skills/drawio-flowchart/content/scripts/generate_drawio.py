#!/usr/bin/env python3
"""Generate an editable .drawio document from a compact JSON or BPMN-style spec."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LEFT_MARGIN = 40
RIGHT_MARGIN = 40
TITLE_Y = 16
TITLE_HEIGHT = 36
LANE_HEADER_Y = 64
LANE_HEADER_HEIGHT = 30
CONTENT_TOP = 108
PHASE_PADDING = 14
PHASE_GAP = 36
ITEM_GAP = 18
BOTTOM_MARGIN = 40
DEFAULT_LANE_WIDTH = 220
DEFAULT_COLUMN_WIDTH = 220
MIN_PHASE_HEIGHT = 76

NODE_TYPE_ALIASES = {
    "activity": "task",
    "annotation": "note",
    "data": "data_object",
    "decision": "gateway_exclusive",
    "document": "document",
    "doc": "document",
    "end": "end_event",
    "end_event": "end_event",
    "event": "intermediate_event",
    "exclusive_gateway": "gateway_exclusive",
    "gateway": "gateway_exclusive",
    "gateway_exclusive": "gateway_exclusive",
    "gateway_inclusive": "gateway_inclusive",
    "gateway_parallel": "gateway_parallel",
    "inclusive_gateway": "gateway_inclusive",
    "intermediate": "intermediate_event",
    "intermediate_event": "intermediate_event",
    "manual": "manual_task",
    "manual_task": "manual_task",
    "message": "message_event",
    "message_event": "message_event",
    "note": "note",
    "parallel_gateway": "gateway_parallel",
    "process": "task",
    "service": "service_task",
    "service_task": "service_task",
    "start": "start_event",
    "start_event": "start_event",
    "step": "task",
    "sub_process": "subprocess",
    "subprocess": "subprocess",
    "system_task": "service_task",
    "task": "task",
    "terminate": "terminate_end",
    "terminate_end": "terminate_end",
    "time_event": "timer_event",
    "timer": "timer_event",
    "timer_event": "timer_event",
    "user": "user_task",
    "user_task": "user_task",
}

EDGE_TYPE_ALIASES = {
    "association": "association",
    "default": "sequence",
    "message": "message",
    "message_flow": "message",
    "sequence": "sequence",
}

TYPE_SIZES = {
    "start_event": (88, 56),
    "intermediate_event": (96, 64),
    "message_event": (104, 64),
    "timer_event": (104, 64),
    "end_event": (88, 56),
    "terminate_end": (88, 56),
    "task": (170, 60),
    "user_task": (170, 60),
    "service_task": (170, 60),
    "manual_task": (170, 60),
    "subprocess": (190, 68),
    "gateway_exclusive": (96, 96),
    "gateway_parallel": (96, 96),
    "gateway_inclusive": (96, 96),
    "data_object": (160, 60),
    "document": (160, 60),
    "note": (220, 120),
}

TYPE_STYLES = {
    "start_event": "ellipse;fillColor=#ECFDF5;strokeColor=#16A34A;strokeWidth=2.5;",
    "intermediate_event": "ellipse;double=1;fillColor=#FFFFFF;strokeColor=#2563EB;strokeWidth=2;",
    "message_event": "ellipse;double=1;fillColor=#EFF6FF;strokeColor=#2563EB;strokeWidth=2;fontColor=#1D4ED8;",
    "timer_event": "ellipse;double=1;fillColor=#EEF2FF;strokeColor=#4F46E5;strokeWidth=2;fontColor=#4338CA;",
    "end_event": "ellipse;fillColor=#FEF2F2;strokeColor=#DC2626;strokeWidth=4;",
    "terminate_end": "ellipse;fillColor=#111827;strokeColor=#111827;strokeWidth=4;fontColor=#FFFFFF;",
    "task": "rounded=1;arcSize=12;fillColor=#FFFFFF;strokeColor=#111827;strokeWidth=2;",
    "user_task": "rounded=1;arcSize=12;fillColor=#EFF6FF;strokeColor=#2563EB;strokeWidth=2;",
    "service_task": "rounded=1;arcSize=12;fillColor=#ECFDF5;strokeColor=#16A34A;strokeWidth=2;",
    "manual_task": "rounded=1;arcSize=12;fillColor=#FFF7ED;strokeColor=#EA580C;strokeWidth=2;",
    "subprocess": "rounded=1;arcSize=12;fillColor=#F8FAFC;strokeColor=#475569;strokeWidth=2.5;dashed=1;",
    "gateway_exclusive": "rhombus;fillColor=#FFF7ED;strokeColor=#EA580C;strokeWidth=2.5;",
    "gateway_parallel": "rhombus;fillColor=#EEF2FF;strokeColor=#4F46E5;strokeWidth=2.5;fontStyle=1;",
    "gateway_inclusive": "rhombus;fillColor=#ECFDF5;strokeColor=#059669;strokeWidth=2.5;fontStyle=1;",
    "data_object": "shape=parallelogram;fillColor=#F8FAFC;strokeColor=#475569;strokeWidth=2;",
    "document": "shape=document;fillColor=#FFFFFF;strokeColor=#475569;strokeWidth=2;",
    "note": (
        "shape=note;align=left;verticalAlign=top;spacing=8;"
        "fillColor=#FFF2CC;strokeColor=#D6B656;fontSize=11;"
    ),
}

BASE_NODE_STYLE = (
    "whiteSpace=wrap;html=1;fontSize=12;fontFamily=Helvetica;"
    "align=center;verticalAlign=middle;"
)

BASE_EDGE_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
    "html=1;strokeColor=#111827;strokeWidth=2;fontSize=11;labelBackgroundColor=#FFFFFF;"
)

EDGE_TYPE_STYLES = {
    "sequence": "endArrow=block;endFill=1;",
    "message": "dashed=1;dashPattern=8 4;endArrow=open;endFill=0;",
    "association": "dashed=1;dashPattern=4 4;endArrow=none;",
}

TITLE_STYLE = (
    "text;html=1;strokeColor=none;fillColor=none;align=center;"
    "verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=20;fontStyle=1;"
)

HEADER_STYLE = (
    "text;html=1;strokeColor=none;fillColor=none;align=center;"
    "verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=12;fontStyle=1;"
)

LANE_STYLE = (
    "swimlane;horizontal=0;container=1;collapsible=0;dropTarget=0;"
    "pointerEvents=0;portConstraint=eastwest;fillColor=none;"
    "strokeColor=#9CA3AF;size=30;fontSize=12;"
)


def fail(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def xml_escape(value: Any) -> str:
    text = str(value)
    text = (
        text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return text.replace("\n", "&#xa;")


def normalize_token(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.:-]+", "-", value).strip("-")
    return cleaned or "item"


def unique_id(prefix: str, raw: str, used: set[str]) -> str:
    base = f"{prefix}-{normalize_token(raw)}"
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def load_spec(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Spec file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in spec file: {exc}")
    if not isinstance(data, dict):
        fail("Spec root must be a JSON object.")
    return data


def canonical_node_type(raw_type: Any) -> str:
    key = str(raw_type or "task").strip().lower().replace("-", "_").replace(" ", "_")
    canonical = NODE_TYPE_ALIASES.get(key, key)
    if canonical not in TYPE_STYLES:
        fail(f"Unsupported node type `{raw_type}`.")
    return canonical


def canonical_edge_type(raw_type: Any) -> str:
    key = str(raw_type or "sequence").strip().lower().replace("-", "_").replace(" ", "_")
    canonical = EDGE_TYPE_ALIASES.get(key, key)
    if canonical not in EDGE_TYPE_STYLES:
        fail(f"Unsupported edge type `{raw_type}`.")
    return canonical


def normalize_lanes(spec: dict[str, Any], nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_lanes = spec.get("lanes") or []
    lanes: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add_lane(raw: Any) -> None:
        if isinstance(raw, str):
            label = raw.strip()
            lane_id = label
            width = DEFAULT_LANE_WIDTH
        elif isinstance(raw, dict):
            label = str(raw.get("label") or raw.get("id") or "").strip()
            if not label:
                fail("Each lane object needs `label` or `id`.")
            lane_id = str(raw.get("id") or label).strip()
            width = int(raw.get("width", DEFAULT_LANE_WIDTH))
        else:
            fail("Each lane must be a string or object.")
        if not lane_id:
            fail("Lane id cannot be empty.")
        if lane_id in seen:
            fail(f"Duplicate lane id: {lane_id}")
        seen.add(lane_id)
        lanes.append({"id": lane_id, "label": label, "width": max(160, width)})

    for item in raw_lanes:
        add_lane(item)

    if not lanes:
        for node in nodes:
            lane = node.get("lane")
            if lane and lane not in seen:
                seen.add(lane)
                lanes.append({"id": lane, "label": lane, "width": DEFAULT_LANE_WIDTH})

    return lanes


def normalize_nodes(spec: dict[str, Any]) -> list[dict[str, Any]]:
    raw_nodes = spec.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        fail("`nodes` must be a non-empty array.")

    nodes: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_nodes, start=1):
        if not isinstance(raw, dict):
            fail("Each node must be an object.")
        node_id = str(raw.get("id") or "").strip()
        text = str(raw.get("text") or "").strip()
        if not node_id:
            fail(f"Node #{index} is missing `id`.")
        if not text:
            fail(f"Node `{node_id}` is missing `text`.")
        if node_id in seen_ids:
            fail(f"Duplicate node id: {node_id}")
        seen_ids.add(node_id)
        nodes.append(
            {
                "id": node_id,
                "text": text,
                "type": canonical_node_type(raw.get("type", "task")),
                "lane": str(raw["lane"]).strip() if raw.get("lane") is not None else None,
                "phase": int(raw["phase"]) if raw.get("phase") is not None else None,
                "column": raw.get("column", 0),
                "width": int(raw["width"]) if raw.get("width") is not None else None,
                "height": int(raw["height"]) if raw.get("height") is not None else None,
                "style": str(raw.get("style", "")).strip(),
            }
        )
    return nodes


def normalize_edges(spec: dict[str, Any], valid_node_ids: set[str]) -> list[dict[str, Any]]:
    raw_edges = spec.get("edges")
    if not isinstance(raw_edges, list):
        fail("`edges` must be an array.")

    edges: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_edges, start=1):
        if not isinstance(raw, dict):
            fail("Each edge must be an object.")
        source = str(raw.get("from") or "").strip()
        target = str(raw.get("to") or "").strip()
        if not source or not target:
            fail(f"Edge #{index} needs both `from` and `to`.")
        if source not in valid_node_ids:
            fail(f"Edge #{index} references unknown source node `{source}`.")
        if target not in valid_node_ids:
            fail(f"Edge #{index} references unknown target node `{target}`.")
        edges.append(
            {
                "from": source,
                "to": target,
                "label": str(raw.get("label", "")).strip(),
                "type": canonical_edge_type(raw.get("type", "sequence")),
                "dashed": bool(raw.get("dashed", False)),
                "style": str(raw.get("style", "")).strip(),
            }
        )
    return edges


def resolve_layout(spec: dict[str, Any], lanes: list[dict[str, Any]]) -> str:
    layout = str(spec.get("layout") or ("swimlane" if lanes else "flowchart")).strip().lower()
    if layout not in {"flowchart", "swimlane"}:
        fail("`layout` must be `flowchart` or `swimlane`.")
    if layout == "flowchart" and lanes:
        fail("`lanes` may only be used with `swimlane` layout.")
    return layout


def default_size(node_type: str) -> tuple[int, int]:
    return TYPE_SIZES[node_type]


def node_size(node: dict[str, Any]) -> tuple[int, int]:
    width, height = default_size(node["type"])
    return (
        max(80, int(node["width"] or width)),
        max(36, int(node["height"] or height)),
    )


def compute_phases(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, int]:
    parents: dict[str, list[str]] = {node["id"]: [] for node in nodes}
    children: dict[str, list[str]] = defaultdict(list)
    indegree: dict[str, int] = {node["id"]: 0 for node in nodes}
    order = [node["id"] for node in nodes]

    for edge in edges:
        source = edge["from"]
        target = edge["to"]
        parents[target].append(source)
        children[source].append(target)
        indegree[target] += 1

    queue = deque(node_id for node_id in order if indegree[node_id] == 0)
    topo: list[str] = []
    while queue:
        node_id = queue.popleft()
        topo.append(node_id)
        for child in children[node_id]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    if len(topo) != len(order):
        topo = order

    lookup = {node["id"]: node for node in nodes}
    phases: dict[str, int] = {}
    for node_id in topo:
        explicit = lookup[node_id]["phase"]
        if explicit is not None:
            phases[node_id] = explicit
            continue
        inferred = 0
        for parent_id in parents[node_id]:
            inferred = max(inferred, phases.get(parent_id, 0) + 1)
        phases[node_id] = inferred
    return phases


def ordered_unique(values: list[Any]) -> list[Any]:
    seen = set()
    result = []
    for value in values:
        marker = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if marker in seen:
            continue
        seen.add(marker)
        result.append(value)
    return result


def sort_group_keys(values: list[Any]) -> list[Any]:
    if all(isinstance(value, int) for value in values):
        return sorted(set(values))
    return ordered_unique(values)


def build_swimlane_layout(
    title: str,
    lanes: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    phases: dict[str, int],
) -> dict[str, Any]:
    lane_ids = [lane["id"] for lane in lanes]
    if not lane_ids:
        fail("Swimlane layout requires at least one lane.")

    for node in nodes:
        if len(lane_ids) > 1 and not node["lane"]:
            fail(f"Node `{node['id']}` is missing `lane` for swimlane layout.")
        if node["lane"] is None:
            node["lane"] = lane_ids[0]
        if node["lane"] not in lane_ids:
            fail(f"Node `{node['id']}` references unknown lane `{node['lane']}`.")

    groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        groups[(phases[node["id"]], node["lane"])].append(node)

    phase_values = sorted(set(phases.values()))
    phase_heights: dict[int, int] = {}
    for phase in phase_values:
        tallest = MIN_PHASE_HEIGHT
        for lane_id in lane_ids:
            lane_nodes = groups.get((phase, lane_id), [])
            if not lane_nodes:
                continue
            total = 0
            for lane_node in lane_nodes:
                _, height = node_size(lane_node)
                total += height
            total += max(0, len(lane_nodes) - 1) * ITEM_GAP
            total += PHASE_PADDING * 2
            tallest = max(tallest, total)
        phase_heights[phase] = tallest

    lane_offsets: dict[str, int] = {}
    cursor_x = LEFT_MARGIN
    for lane in lanes:
        lane_offsets[lane["id"]] = cursor_x
        cursor_x += lane["width"]
    page_width = cursor_x + RIGHT_MARGIN

    positions: dict[str, dict[str, int]] = {}
    cursor_y = CONTENT_TOP
    for phase in phase_values:
        band_height = phase_heights[phase]
        for lane in lanes:
            lane_nodes = groups.get((phase, lane["id"]), [])
            if not lane_nodes:
                continue
            total = 0
            sizes: dict[str, tuple[int, int]] = {}
            for lane_node in lane_nodes:
                sizes[lane_node["id"]] = node_size(lane_node)
                total += sizes[lane_node["id"]][1]
            total += max(0, len(lane_nodes) - 1) * ITEM_GAP
            start_y = cursor_y + max(PHASE_PADDING, (band_height - total) // 2)
            for lane_node in lane_nodes:
                width, height = sizes[lane_node["id"]]
                x = lane_offsets[lane["id"]] + (lane["width"] - width) // 2
                positions[lane_node["id"]] = {"x": x, "y": start_y, "width": width, "height": height}
                start_y += height + ITEM_GAP
        cursor_y += band_height + PHASE_GAP

    page_height = cursor_y + BOTTOM_MARGIN
    lane_height = page_height - LANE_HEADER_Y - 20

    return {
        "title": title,
        "page_width": page_width,
        "page_height": page_height,
        "positions": positions,
        "lane_offsets": lane_offsets,
        "lanes": lanes,
        "lane_height": lane_height,
        "edges": edges,
        "nodes": nodes,
    }


def build_flowchart_layout(
    title: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    phases: dict[str, int],
) -> dict[str, Any]:
    column_values = sort_group_keys([node.get("column", 0) for node in nodes])
    groups: dict[tuple[int, Any], list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        groups[(phases[node["id"]], node.get("column", 0))].append(node)

    column_widths: dict[Any, int] = {}
    for column in column_values:
        max_width = 0
        for node in nodes:
            if node.get("column", 0) != column:
                continue
            width, _ = node_size(node)
            max_width = max(max_width, width)
        column_widths[column] = max(DEFAULT_COLUMN_WIDTH, max_width + 80)

    column_offsets: dict[Any, int] = {}
    cursor_x = LEFT_MARGIN + 40
    for column in column_values:
        column_offsets[column] = cursor_x
        cursor_x += column_widths[column]
    page_width = max(520, cursor_x + RIGHT_MARGIN)

    phase_values = sorted(set(phases.values()))
    phase_heights: dict[int, int] = {}
    for phase in phase_values:
        tallest = MIN_PHASE_HEIGHT
        for column in column_values:
            column_nodes = groups.get((phase, column), [])
            if not column_nodes:
                continue
            total = 0
            for column_node in column_nodes:
                _, height = node_size(column_node)
                total += height
            total += max(0, len(column_nodes) - 1) * ITEM_GAP
            total += PHASE_PADDING * 2
            tallest = max(tallest, total)
        phase_heights[phase] = tallest

    positions: dict[str, dict[str, int]] = {}
    cursor_y = CONTENT_TOP - 16
    for phase in phase_values:
        band_height = phase_heights[phase]
        for column in column_values:
            column_nodes = groups.get((phase, column), [])
            if not column_nodes:
                continue
            total = 0
            sizes: dict[str, tuple[int, int]] = {}
            for column_node in column_nodes:
                sizes[column_node["id"]] = node_size(column_node)
                total += sizes[column_node["id"]][1]
            total += max(0, len(column_nodes) - 1) * ITEM_GAP
            start_y = cursor_y + max(PHASE_PADDING, (band_height - total) // 2)
            for column_node in column_nodes:
                width, height = sizes[column_node["id"]]
                x = column_offsets[column] + (column_widths[column] - width) // 2
                positions[column_node["id"]] = {"x": x, "y": start_y, "width": width, "height": height}
                start_y += height + ITEM_GAP
        cursor_y += band_height + PHASE_GAP

    page_height = cursor_y + BOTTOM_MARGIN
    return {
        "title": title,
        "page_width": page_width,
        "page_height": page_height,
        "positions": positions,
        "edges": edges,
        "nodes": nodes,
    }


def vertex_cell(cell_id: str, value: str, style: str, x: int, y: int, width: int, height: int) -> str:
    return (
        f'        <mxCell id="{xml_escape(cell_id)}" value="{xml_escape(value)}" '
        f'style="{xml_escape(style)}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry" />\n'
        f"        </mxCell>"
    )


def edge_cell(cell_id: str, value: str, style: str, source: str, target: str) -> str:
    return (
        f'        <mxCell id="{xml_escape(cell_id)}" value="{xml_escape(value)}" '
        f'style="{xml_escape(style)}" edge="1" parent="1" '
        f'source="{xml_escape(source)}" target="{xml_escape(target)}">\n'
        '          <mxGeometry relative="1" as="geometry" />\n'
        "        </mxCell>"
    )


def node_style(node: dict[str, Any]) -> str:
    style = BASE_NODE_STYLE + TYPE_STYLES[node["type"]]
    if node["style"]:
        style += node["style"]
        if not style.endswith(";"):
            style += ";"
    return style


def edge_style(edge: dict[str, Any]) -> str:
    style = BASE_EDGE_STYLE + EDGE_TYPE_STYLES[edge["type"]]
    if edge["dashed"] and "dashed=1;" not in style:
        style += "dashed=1;dashPattern=5 3;"
    if edge["style"]:
        style += edge["style"]
        if not style.endswith(";"):
            style += ";"
    return style


def build_xml(layout: dict[str, Any], mode: str) -> str:
    used_ids: set[str] = {"0", "1"}
    node_cell_ids: dict[str, str] = {}
    parts = []

    title_width = min(420, max(180, len(layout["title"]) * 18))
    title_x = max(LEFT_MARGIN, (layout["page_width"] - title_width) // 2)
    parts.append(vertex_cell("title", layout["title"], TITLE_STYLE, title_x, TITLE_Y, title_width, TITLE_HEIGHT))

    if mode == "swimlane":
        for lane in layout["lanes"]:
            lane_cell_id = unique_id("lane", lane["id"], used_ids)
            x = layout["lane_offsets"][lane["id"]]
            parts.append(
                vertex_cell(
                    lane_cell_id,
                    "",
                    LANE_STYLE,
                    x,
                    LANE_HEADER_Y,
                    lane["width"],
                    layout["lane_height"],
                )
            )
            header_id = unique_id("header", lane["id"], used_ids)
            parts.append(
                vertex_cell(
                    header_id,
                    lane["label"],
                    HEADER_STYLE,
                    x,
                    LANE_HEADER_Y,
                    lane["width"],
                    LANE_HEADER_HEIGHT,
                )
            )

    for node in layout["nodes"]:
        cell_id = unique_id("node", node["id"], used_ids)
        node_cell_ids[node["id"]] = cell_id
        pos = layout["positions"][node["id"]]
        parts.append(
            vertex_cell(
                cell_id,
                node["text"],
                node_style(node),
                pos["x"],
                pos["y"],
                pos["width"],
                pos["height"],
            )
        )

    for edge in layout["edges"]:
        edge_id = unique_id("edge", f"{edge['from']}-{edge['to']}", used_ids)
        parts.append(
            edge_cell(
                edge_id,
                edge["label"],
                edge_style(edge),
                node_cell_ids[edge["from"]],
                node_cell_ids[edge["to"]],
            )
        )

    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    body = "\n".join(parts)
    return (
        f'<mxfile host="app.diagrams.net" modified="{modified}" agent="Codex" version="24.7.17" type="device">\n'
        f'  <diagram name="{xml_escape(layout["title"])}" id="flowchart-1">\n'
        f'    <mxGraphModel dx="{layout["page_width"]}" dy="{layout["page_height"]}" grid="1" gridSize="10" guides="1" '
        f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="{layout["page_width"] + 80}" pageHeight="{layout["page_height"] + 80}" math="0" shadow="0">\n'
        "      <root>\n"
        '        <mxCell id="0" />\n'
        '        <mxCell id="1" parent="0" />\n'
        f"{body}\n"
        "      </root>\n"
        "    </mxGraphModel>\n"
        "  </diagram>\n"
        "</mxfile>\n"
    )


def build_layout_from_spec(spec: dict[str, Any]) -> tuple[dict[str, Any], str]:
    nodes = normalize_nodes(spec)
    node_ids = {node["id"] for node in nodes}
    edges = normalize_edges(spec, node_ids)
    lanes = normalize_lanes(spec, nodes)
    layout_mode = resolve_layout(spec, lanes)
    phases = compute_phases(nodes, edges)
    title = str(spec.get("title") or "Flowchart").strip() or "Flowchart"

    if layout_mode == "swimlane":
        layout = build_swimlane_layout(title, lanes, nodes, edges, phases)
    else:
        layout = build_flowchart_layout(title, nodes, edges, phases)
    return layout, layout_mode


def generate_from_spec(spec: dict[str, Any], output_path: Path) -> Path:
    layout, layout_mode = build_layout_from_spec(spec)
    xml = build_xml(layout, layout_mode)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(xml, encoding="utf-8")
    print(f"[OK] Wrote {output_path}")
    return output_path


def generate(spec_path: Path, output_path: Path) -> Path:
    spec = load_spec(spec_path)
    return generate_from_spec(spec, output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a draw.io document from a JSON flowchart spec.")
    parser.add_argument("--spec", required=True, help="Path to the JSON spec file.")
    parser.add_argument("--output", required=True, help="Path to the output .drawio file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate(Path(args.spec), Path(args.output))


if __name__ == "__main__":
    main()
