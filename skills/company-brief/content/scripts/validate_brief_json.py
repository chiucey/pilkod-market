#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量校验器：检查结构化的公司速览 JSON 文件是否符合本技能约定的字段与枚举。

只做静态字段/枚举/外键校验，不会判断来源真伪 —— 来源真伪与证据规则需由
助手在工作流中亲自审阅。

顶层 JSON 形如：
    {
        "entity": "ExampleCo",
        "profile_type": "public_company",
        "as_of_date": "2026-05-07",
        "sources": [{"source_id": "S1", "source_name": "...", ...}],
        "metrics": [{"metric": "Revenue", "period": "FY2025", ...}],
        "sections": {"one_line_view": "...", "business_snapshot": [...]}
    }
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


# --------------------------------------------------------------------------
# 字段与枚举常量
# --------------------------------------------------------------------------

EVIDENCE_VOCAB: frozenset[str] = frozenset(
    {
        "fact_source_reported",
        "fact_provider_standardized",
        "derived_calculation",
        "issuer_management_claim",
        "management_adjusted",
        "analyst_adjusted",
        "estimate_consensus",
        "analyst_interpretation",
        "assumption_user_provided",
        "assumption_inferred",
        "stale_source",
        "contradicted_source",
        "missing_required_source",
        "unknown",
    }
)

CONFIDENCE_VOCAB: frozenset[str] = frozenset({"high", "medium", "low"})

PROFILE_TYPE_VOCAB: frozenset[str] = frozenset(
    {"public_company", "equity_issuer_profile", "public_sector_peer"}
)

TOP_LEVEL_REQUIRED: tuple[str, ...] = ("entity", "profile_type", "as_of_date")
SOURCE_REQUIRED: tuple[str, ...] = ("source_id", "source_name", "source_type")
METRIC_REQUIRED: tuple[str, ...] = (
    "metric",
    "period",
    "value",
    "units",
    "source",
    "evidence",
    "confidence",
)


# --------------------------------------------------------------------------
# 结果对象
# --------------------------------------------------------------------------


@dataclass
class Findings:
    """聚合错误与告警。"""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def has_error(self) -> bool:
        return bool(self.errors)

    @property
    def has_warning(self) -> bool:
        return bool(self.warnings)

    def to_lines(self) -> list[str]:
        return [f"ERROR: {e}" for e in self.errors] + [
            f"WARNING: {w}" for w in self.warnings
        ]


# --------------------------------------------------------------------------
# 校验器
# --------------------------------------------------------------------------


class BriefValidator:
    """对 brief JSON 做分块校验。"""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.findings = Findings()
        self._known_source_ids: set[str] = set()

    # ---- 顶层 ----
    def _check_top_level(self) -> None:
        for key in TOP_LEVEL_REQUIRED:
            if not self.payload.get(key):
                self.findings.add_error(f"missing top-level field: {key}")
        ptype = self.payload.get("profile_type")
        if ptype and ptype not in PROFILE_TYPE_VOCAB:
            allowed = ", ".join(sorted(PROFILE_TYPE_VOCAB))
            self.findings.add_error(f"profile_type must be one of: {allowed}")

    # ---- sources ----
    def _check_sources(self) -> None:
        sources = self.payload.get("sources", [])
        if not isinstance(sources, list):
            self.findings.add_error("sources must be a list")
            return

        for position, item in enumerate(sources, start=1):
            if not isinstance(item, dict):
                self.findings.add_error(f"source {position} must be an object")
                continue

            missing = [f for f in SOURCE_REQUIRED if not item.get(f)]
            for field_name in missing:
                self.findings.add_error(f"source {position} missing field: {field_name}")

            sid = item.get("source_id")
            if sid:
                self._known_source_ids.add(str(sid))
            if not item.get("as_of_date"):
                self.findings.add_warning(f"source {position} missing as_of_date")

    # ---- metrics ----
    def _check_metrics(self) -> None:
        metrics = self.payload.get("metrics", [])
        if metrics and not isinstance(metrics, list):
            self.findings.add_error("metrics must be a list")
            return

        for position, item in enumerate(metrics, start=1):
            self._check_single_metric(position, item)

    def _check_single_metric(self, position: int, item: Any) -> None:
        if not isinstance(item, dict):
            self.findings.add_error(f"metric {position} must be an object")
            return

        for field_name in METRIC_REQUIRED:
            value = item.get(field_name) if field_name in item else None
            if field_name not in item or value in (None, ""):
                self.findings.add_error(
                    f"metric {position} missing field: {field_name}"
                )

        evidence = item.get("evidence")
        if evidence and evidence not in EVIDENCE_VOCAB:
            self.findings.add_error(
                f"metric {position} has invalid evidence label: {evidence}"
            )

        confidence = item.get("confidence")
        if confidence and confidence not in CONFIDENCE_VOCAB:
            self.findings.add_error(
                f"metric {position} has invalid confidence label: {confidence}"
            )

        # `source` 字段惯例：以 `S1 ...` / `S2 tab ...` 起始
        source_field = str(item.get("source", "")).strip()
        first_token = source_field.split()[0] if source_field else ""
        if first_token and self._known_source_ids and first_token not in self._known_source_ids:
            self.findings.add_warning(
                f"metric {position} source id not found in sources: {first_token}"
            )

        if not item.get("period"):
            self.findings.add_error(f"metric {position} missing period")

        # 推断假设应当与低置信度匹配
        if (
            item.get("evidence") == "assumption_inferred"
            and item.get("confidence") != "low"
        ):
            self.findings.add_warning(
                f"metric {position} inferred assumptions should usually be low confidence"
            )

    # ---- 数据质量 flags ----
    def _check_data_quality_flags(self) -> None:
        flags = self.payload.get("data_quality_flags", [])
        if flags and not isinstance(flags, list):
            self.findings.add_error("data_quality_flags must be a list")

    # ---- 入口 ----
    def run(self) -> Findings:
        for check in (
            self._check_top_level,
            self._check_sources,
            self._check_metrics,
            self._check_data_quality_flags,
        ):
            check()
        return self.findings


# --------------------------------------------------------------------------
# 文件读取
# --------------------------------------------------------------------------


def _read_json_file(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"cannot read file: {exc}") from exc

    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {exc}") from exc

    if not isinstance(loaded, dict):
        raise SystemExit("top-level json must be an object")
    return loaded


def _emit(messages: Iterable[str]) -> None:
    for line in messages:
        print(line)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _make_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate_brief_json",
        description="Validate a company brief JSON file",
    )
    parser.add_argument("input_json", type=Path, help="Path to brief JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _make_cli().parse_args(argv)

    payload = _read_json_file(args.input_json)
    validator = BriefValidator(payload)
    findings = validator.run()

    _emit(findings.to_lines())

    if findings.has_error or (args.strict and findings.has_warning):
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
