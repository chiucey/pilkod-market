#!/usr/bin/env python3
"""Turn line-oriented natural language into a drawio-flowchart JSON spec."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

TITLE_RE = re.compile(r"^(?:标题|title)\s*[:：]\s*(.+)$", re.IGNORECASE)
LANE_RE = re.compile(r"^(?:泳道|角色|参与角色|参与方|actors|lanes)\s*[:：]\s*(.+)$", re.IGNORECASE)
BULLET_RE = re.compile(r"^\s*(?:[-*•]|(?:\d+[\.\)]))\s*")
ARROW_SPLIT_RE = re.compile(r"\s*(?:->|→|=>|⟶|然后|接着|随后|之后|最后)\s*")

BRANCH_LABELS = {
    "通过": "通过",
    "同意": "通过",
    "批准": "通过",
    "驳回": "驳回",
    "拒绝": "驳回",
    "否则": "驳回",
    "未通过": "驳回",
    "不通过": "驳回",
    "是": "是",
    "否": "否",
    "成功": "成功",
    "失败": "失败",
    "异常": "异常",
    "超时": "超时",
}

COMMON_ACTORS = [
    "申请人",
    "用户",
    "员工",
    "主管",
    "经理",
    "审批人",
    "财务",
    "人事",
    "HR",
    "客服",
    "仓库",
    "采购",
    "运营",
    "系统",
    "服务",
    "接口",
    "平台",
    "供应商",
]

START_WORDS = ("开始", "发起", "启动", "触发")
END_WORDS = ("结束", "完成", "归档完成", "终止", "关闭")
DECISION_WORDS = ("是否", "审批", "审核", "判断", "校验", "检查", "确认", "网关")
PARALLEL_WORDS = ("并行", "同时", "会签", "拆分")
INCLUSIVE_WORDS = ("可选", "包含", "任一", "汇总", "汇聚", "合流", "归并")


@dataclass
class ParserState:
    title: str | None = None
    lanes: dict[str, None] = field(default_factory=dict)
    nodes: list[dict[str, Any]] = field(default_factory=list)
    node_lookup: dict[str, dict[str, Any]] = field(default_factory=dict)
    edges: list[dict[str, Any]] = field(default_factory=list)
    active_sources: list[str] = field(default_factory=list)
    current_gateway_id: str | None = None
    pending_branch_targets: list[str] = field(default_factory=list)
    node_ids: set[str] = field(default_factory=set)
    edge_keys: set[tuple[str, str, str, str]] = field(default_factory=set)
    node_counter: int = 0


def strip_bullet_prefix(line: str) -> str:
    return BULLET_RE.sub("", line).strip()


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace("→", " -> ").replace("=>", " -> ")
    normalized = normalized.replace("；", "\n").replace(";", "\n")
    normalized = re.sub(r"[，,]\s*(通过|同意|批准|是|成功)\s*(?:则|:|：)", r"\n\1 -> ", normalized)
    normalized = re.sub(r"[，,]\s*(驳回|拒绝|否则|未通过|不通过|否|失败)\s*(?:则|:|：)?", r"\n\1 -> ", normalized)
    normalized = re.sub(r"([。！？!?])\s*", r"\1\n", normalized)
    return normalized


def split_list_values(raw: str) -> list[str]:
    parts = re.split(r"\s*(?:\||,|，|/|、)\s*", raw.strip())
    return [part for part in (item.strip() for item in parts) if part]


def looks_like_title(line: str) -> bool:
    return (
        len(line) <= 30
        and "->" not in line
        and ":" not in line
        and "：" not in line
        and any(keyword in line for keyword in ("流程", "审批", "图"))
    )


def branch_label_for(text: str) -> str | None:
    candidate = text.strip().rstrip("：:")
    return BRANCH_LABELS.get(candidate)


def split_segments(line: str) -> list[str]:
    parts = [part.strip() for part in ARROW_SPLIT_RE.split(line) if part.strip()]
    return parts or [line.strip()]


def starts_with_branch(line: str) -> bool:
    first = split_segments(line)[0]
    if branch_label_for(first):
        return True
    match = re.match(r"^(.+?)\s*(?:->|:|：|则)\s*(.+)$", first)
    return bool(match and branch_label_for(match.group(1)))


def canonical_actor_names(known_lanes: list[str]) -> list[str]:
    names = list(dict.fromkeys(known_lanes + COMMON_ACTORS))
    return sorted(names, key=len, reverse=True)


def extract_actor_and_body(segment: str, known_lanes: list[str]) -> tuple[str | None, str]:
    match = re.match(r"^(?P<actor>[^:：]{1,30})[:：]\s*(?P<body>.+)$", segment)
    if match:
        actor = match.group("actor").strip()
        body = match.group("body").strip()
        return actor or None, body

    for actor in canonical_actor_names(known_lanes):
        if segment.startswith(actor) and len(segment) > len(actor):
            body = segment[len(actor) :].lstrip("：:，, ")
            if body:
                return actor, body
    return None, segment.strip()


def slug_token(text: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", text.lower())
    return "_".join(tokens)


def ensure_lane(state: ParserState, actor: str | None) -> None:
    if actor and actor not in state.lanes:
        state.lanes[actor] = None


def infer_node_type(text: str, actor: str | None = None) -> str:
    stripped = text.strip()
    if any(word == stripped or stripped.endswith(word) for word in END_WORDS):
        return "end_event"
    if stripped in START_WORDS:
        return "start_event"
    if "子流程" in stripped or ("进入" in stripped and "流程" in stripped):
        return "subprocess"
    if any(word in stripped for word in PARALLEL_WORDS):
        return "gateway_parallel"
    if any(word in stripped for word in INCLUSIVE_WORDS):
        return "gateway_inclusive"
    if "?" in stripped or "？" in stripped or any(word in stripped for word in DECISION_WORDS):
        return "gateway_exclusive"
    if any(word in stripped for word in ("短信", "邮件", "消息", "通知")) and any(
        word in stripped for word in ("发送", "接收", "收到", "推送")
    ):
        return "message_event"
    if any(word in stripped for word in ("等待", "超时", "定时", "到期", "延时", "倒计时")):
        return "timer_event"
    if any(word in stripped for word in ("人工", "手工", "线下")):
        return "manual_task"
    if actor and any(word in actor for word in ("系统", "服务", "接口", "平台", "API")):
        return "service_task"
    if actor:
        return "user_task"
    return "task"


def next_node_id(state: ParserState, actor: str | None, text: str) -> str:
    state.node_counter += 1
    parts = [slug_token(actor or ""), slug_token(text)]
    seed = "_".join(part for part in parts if part)
    if not seed:
        seed = f"node_{state.node_counter}"
    candidate = seed
    suffix = 2
    while candidate in state.node_ids:
        candidate = f"{seed}_{suffix}"
        suffix += 1
    state.node_ids.add(candidate)
    return candidate


def add_node(state: ParserState, actor: str | None, text: str) -> dict[str, Any]:
    ensure_lane(state, actor)
    node = {
        "id": next_node_id(state, actor, text),
        "text": text.strip(),
        "type": infer_node_type(text, actor),
        "lane": actor,
    }
    state.nodes.append(node)
    state.node_lookup[node["id"]] = node
    return node


def add_edge(state: ParserState, source: str, target: str, label: str = "", edge_type: str = "sequence") -> None:
    key = (source, target, label, edge_type)
    if key in state.edge_keys:
        return
    state.edge_keys.add(key)
    state.edges.append({"from": source, "to": target, "label": label, "type": edge_type})


def dedupe_ids(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def flush_pending_branches(state: ParserState) -> None:
    if state.pending_branch_targets:
        state.active_sources = dedupe_ids(state.pending_branch_targets)
        state.pending_branch_targets.clear()
        state.current_gateway_id = None


def unanimous_lane(state: ParserState, source_ids: list[str]) -> str | None:
    lanes = {
        state.node_lookup[source_id]["lane"]
        for source_id in source_ids
        if source_id in state.node_lookup and state.node_lookup[source_id].get("lane")
    }
    if len(lanes) == 1:
        return next(iter(lanes))
    return None


def handle_segment(
    state: ParserState,
    segment: str,
    pending_label: str | None,
    branch_targets: list[str],
) -> tuple[str | None, list[str]]:
    segment = segment.strip()
    if not segment:
        return pending_label, branch_targets

    direct_branch = re.match(r"^(.+?)\s*(?:->|:|：|则)\s*(.+)$", segment)
    if direct_branch and branch_label_for(direct_branch.group(1)):
        pending_label = branch_label_for(direct_branch.group(1))
        segment = direct_branch.group(2).strip()
    elif branch_label_for(segment):
        return branch_label_for(segment), branch_targets

    actor, body = extract_actor_and_body(segment, list(state.lanes.keys()))
    if pending_label:
        fallback_sources = [state.current_gateway_id] if state.current_gateway_id else state.active_sources[-1:]
    else:
        fallback_sources = state.active_sources
    if actor is None:
        actor = unanimous_lane(state, fallback_sources)
    node = add_node(state, actor, body)

    if pending_label:
        source = state.current_gateway_id or (state.active_sources[-1] if state.active_sources else None)
        if source:
            add_edge(state, source, node["id"], label=pending_label)
        branch_targets.append(node["id"])
        state.active_sources = [node["id"]]
        pending_label = None
    else:
        for source in state.active_sources:
            add_edge(state, source, node["id"])
        state.active_sources = [node["id"]]

    if node["type"].startswith("gateway_"):
        state.current_gateway_id = node["id"]
    return pending_label, branch_targets


def parse_content_line(state: ParserState, line: str) -> None:
    line = strip_bullet_prefix(line)
    if not line:
        return

    if state.pending_branch_targets and not starts_with_branch(line):
        flush_pending_branches(state)

    segments = split_segments(line)
    pending_label: str | None = None
    branch_targets: list[str] = []

    for segment in segments:
        pending_label, branch_targets = handle_segment(state, segment, pending_label, branch_targets)

    if branch_targets:
        state.pending_branch_targets.extend(branch_targets)


def postprocess_nodes(state: ParserState) -> None:
    outgoing: dict[str, list[dict[str, Any]]] = {}
    for edge in state.edges:
        outgoing.setdefault(edge["from"], []).append(edge)

    for node in state.nodes:
        edges = outgoing.get(node["id"], [])
        if len(edges) > 1:
            if any(word in node["text"] for word in PARALLEL_WORDS):
                node["type"] = "gateway_parallel"
            elif any(word in node["text"] for word in INCLUSIVE_WORDS):
                node["type"] = "gateway_inclusive"
            else:
                node["type"] = "gateway_exclusive"
        if not edges and any(word == node["text"] or node["text"].endswith(word) for word in END_WORDS):
            node["type"] = "end_event"


def build_spec(state: ParserState) -> dict[str, Any]:
    postprocess_nodes(state)
    layout = "swimlane" if len(state.lanes) >= 2 else "flowchart"

    nodes = []
    for node in state.nodes:
        item = {"id": node["id"], "text": node["text"], "type": node["type"]}
        if layout == "swimlane" and node.get("lane"):
            item["lane"] = node["lane"]
        nodes.append(item)

    spec = {
        "title": state.title or "流程图",
        "layout": layout,
        "nodes": nodes,
        "edges": state.edges,
    }

    if layout == "swimlane":
        spec["lanes"] = [{"id": lane, "label": lane} for lane in state.lanes.keys()]
    else:
        spec["lanes"] = []

    return spec


def text_to_spec(text: str, title: str | None = None) -> dict[str, Any]:
    normalized = normalize_text(text)
    lines = [strip_bullet_prefix(line) for line in normalized.splitlines()]
    lines = [line for line in lines if line]

    state = ParserState(title=title)
    content_lines: list[str] = []

    for index, line in enumerate(lines):
        title_match = TITLE_RE.match(line)
        if title_match:
            state.title = title_match.group(1).strip()
            continue
        lane_match = LANE_RE.match(line)
        if lane_match:
            for lane in split_list_values(lane_match.group(1)):
                state.lanes.setdefault(lane, None)
            continue
        if index == 0 and not state.title and looks_like_title(line):
            state.title = line
            continue
        content_lines.append(line)

    for line in content_lines:
        parse_content_line(state, line)

    flush_pending_branches(state)
    return build_spec(state)


def load_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    return Path(args.input).read_text(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Turn natural language into a drawio-flowchart JSON spec.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Path to a UTF-8 text file.")
    group.add_argument("--text", help="Inline natural language text.")
    parser.add_argument("--title", help="Optional title override.")
    parser.add_argument("--output", help="Optional output JSON path. Prints to stdout when omitted.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spec = text_to_spec(load_text(args), title=args.title)
    payload = json.dumps(spec, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
        print(f"[OK] Wrote {output_path}")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
