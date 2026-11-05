#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将结构化 JSON 渲染为公司速览 Markdown。

本工具完全离线、不抓取任何数据：它只负责把助手已经整理好、并打了证据标签的
事实材料按照固定的章节顺序铺排成 Markdown。

CLI：
    python build_brief_markdown.py <input.json> <output.md>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Sequence


# --------------------------------------------------------------------------
# 通用工具
# --------------------------------------------------------------------------


def _scrub(value: Any) -> str:
    """把任意单元格值压成单行字符串。"""
    if value is None:
        return ""
    return str(value).replace("\n", " ").strip()


def _pad_row(row: Sequence[Any], width: int) -> list[Any]:
    """让单行长度与表头一致：截多补少。"""
    materialized = list(row)
    if len(materialized) >= width:
        return materialized[:width]
    return materialized + [""] * (width - len(materialized))


def _md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    if not rows:
        return ""
    width = len(headers)
    header_line = "| " + " | ".join(headers) + " |"
    divider = "|" + "|".join(["---"] * width) + "|"
    body = [
        "| " + " | ".join(_scrub(cell) for cell in _pad_row(row, width)) + " |"
        for row in rows
    ]
    return "\n".join([header_line, divider, *body])


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


# --------------------------------------------------------------------------
# 渲染器
# --------------------------------------------------------------------------


class BriefRenderer:
    """逐段铺排 brief Markdown。每个 `_section_*` 方法负责产出一段。"""

    HEADER_TABLE_SNAPSHOT = ("Field", "Detail", "Source", "Evidence", "Confidence")
    HEADER_TABLE_METRICS = (
        "Metric",
        "Period",
        "Value",
        "Units",
        "Source",
        "Evidence",
        "Confidence",
    )
    HEADER_TABLE_SOURCES = ("ID", "Source", "Type", "As of", "Freshness", "Location")

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.sections = _as_dict(payload.get("sections"))
        self._buffer: list[str] = []

    # 辅助：读 sections.X 优先，否则回退到 payload.X
    def _pick(self, key: str, default: Any = None) -> Any:
        if key in self.sections:
            return self.sections[key]
        return self.payload.get(key, default)

    def _emit_block(self, *parts: str) -> None:
        for part in parts:
            if part is None:
                continue
            self._buffer.append(part)

    # ----- 各段 -----

    def _section_header(self) -> None:
        raw_entity = self.payload.get("entity", "Entity")
        # entity 可以是 dict({name, ticker, ...}) 或字符串两种形态;
        # dict 形态取 name,字符串形态直接用,空值兜底为 "Entity"。
        if isinstance(raw_entity, dict):
            entity_label = _scrub(raw_entity.get("name") or raw_entity.get("ticker") or "Entity")
            ticker = _scrub(raw_entity.get("ticker", ""))
        else:
            entity_label = _scrub(raw_entity) or "Entity"
            ticker = ""
        ptype = _scrub(self.payload.get("profile_type", "profile"))
        header_title = f"{entity_label} ({ticker})" if ticker else entity_label
        self._emit_block(f"# {header_title} Brief")
        self._emit_block(f"**Profile type:** {ptype}  ")

        meta_pairs = (
            ("As of", self.payload.get("as_of_date", "")),
            ("Scope", self.payload.get("scope", "")),
            ("Source caveat", self.payload.get("source_caveat", "")),
        )
        for label, raw in meta_pairs:
            value = _scrub(raw)
            if value:
                self._emit_block(f"**{label}:** {value}  ")

    def _section_one_line(self) -> None:
        one_line = self._pick("one_line_view")
        if one_line:
            self._emit_block("", "## One-line view", _scrub(one_line))

    def _section_business_snapshot(self) -> None:
        snapshot = self._pick("business_snapshot", [])
        rows: list[list[Any]] = []
        for item in _as_list(snapshot):
            if not isinstance(item, dict):
                continue
            rows.append(
                [
                    item.get("field", ""),
                    item.get("detail", ""),
                    item.get("source", ""),
                    item.get("evidence", ""),
                    item.get("confidence", ""),
                ]
            )
        if rows:
            self._emit_block(
                "",
                "## Business snapshot",
                _md_table(self.HEADER_TABLE_SNAPSHOT, rows),
            )

    def _section_metrics(self) -> None:
        metrics = self.payload.get("metrics", [])
        rows: list[list[Any]] = []
        for entry in _as_list(metrics):
            if not isinstance(entry, dict):
                continue
            rows.append(
                [
                    entry.get("metric", ""),
                    entry.get("period", ""),
                    entry.get("value", ""),
                    entry.get("units", ""),
                    entry.get("source", ""),
                    entry.get("evidence", ""),
                    entry.get("confidence", ""),
                ]
            )
        if rows:
            self._emit_block(
                "",
                "## Key metrics",
                _md_table(self.HEADER_TABLE_METRICS, rows),
            )

    def _section_recent_developments(self) -> None:
        events = self._pick("recent_developments", [])
        events_list = _as_list(events)
        if not events_list:
            return
        self._emit_block("", "## Recent developments")
        for event in events_list:
            self._emit_block(f"- {_scrub(event)}")

    def _section_relevance(self) -> None:
        relevance = self._pick("workflow_relevance", [])
        if isinstance(relevance, list) and relevance:
            self._emit_block("", "## Relevance for this workflow")
            for item in relevance:
                self._emit_block(f"- {_scrub(item)}")
        elif relevance:
            self._emit_block("", "## Relevance for this workflow", _scrub(relevance))

    def _section_risks(self) -> None:
        risks = self._pick("risks_gaps_flags")
        if risks is None:
            risks = self.payload.get("data_quality_flags", [])
        if isinstance(risks, list) and risks:
            self._emit_block("", "## Risks, gaps, and evidence flags")
            for risk in risks:
                self._emit_block(f"- {_scrub(risk)}")
        elif risks:
            self._emit_block(
                "", "## Risks, gaps, and evidence flags", _scrub(risks)
            )

    def _section_sources(self) -> None:
        sources = self.payload.get("sources", [])
        rows: list[list[Any]] = []
        for src in _as_list(sources):
            if not isinstance(src, dict):
                continue
            rows.append(
                [
                    src.get("source_id", ""),
                    src.get("source_name", ""),
                    src.get("source_type", ""),
                    src.get("as_of_date", ""),
                    src.get("freshness_status", ""),
                    src.get("source_location", ""),
                ]
            )
        if rows:
            self._emit_block(
                "",
                "## Source notes",
                _md_table(self.HEADER_TABLE_SOURCES, rows),
            )

    def _section_next_step(self) -> None:
        nxt = self.payload.get("recommended_next_step") or self.sections.get(
            "recommended_next_step"
        )
        if nxt:
            self._emit_block("", "## Recommended next step", _scrub(nxt))

    # ----- 入口 -----

    def render(self) -> str:
        ordered_sections: tuple[callable, ...] = (
            self._section_header,
            self._section_one_line,
            self._section_business_snapshot,
            self._section_metrics,
            self._section_recent_developments,
            self._section_relevance,
            self._section_risks,
            self._section_sources,
            self._section_next_step,
        )
        for fn in ordered_sections:
            fn()
        return "\n".join(self._buffer).rstrip() + "\n"


# 兼容旧调用：保留模块级 build_markdown(dict) -> str
def build_markdown(data: dict[str, Any]) -> str:
    return BriefRenderer(data).render()


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _load_payload(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("top-level json must be an object")
    return data


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="build_brief_markdown",
        description="Build markdown company brief from JSON",
    )
    parser.add_argument("input_json", type=Path, help="Path to brief JSON")
    parser.add_argument("output_md", type=Path, help="Output markdown path")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_cli().parse_args(list(argv) if argv is not None else None)
    payload = _load_payload(args.input_json)
    rendered = build_markdown(payload)
    args.output_md.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
