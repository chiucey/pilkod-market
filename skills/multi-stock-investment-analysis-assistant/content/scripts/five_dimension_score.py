#!/usr/bin/env python3
"""Calculate weighted five-dimension stock-analysis score and gate status."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


DIMENSIONS = {
    "trend": {"label": "趋势", "weight": 25},
    "capital_volume": {"label": "资金与量价", "weight": 15},
    "fundamentals": {"label": "基本面", "weight": 25},
    "valuation": {"label": "估值", "weight": 20},
    "catalyst_expectations": {"label": "催化与预期", "weight": 15},
}

REQUIRED_GATES = (
    "data",
    "structure",
    "risk",
    "reward",
    "event",
    "liquidity",
    "time",
    "consistency",
)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


def parse_rating(value: Any, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{name}.rating must be one of -2, -1, 0, 1, 2, or null")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{name}.rating must be one of -2, -1, 0, 1, 2, or null"
        ) from exc
    if not math.isfinite(numeric) or numeric not in (-2, -1, 0, 1, 2):
        raise ValueError(f"{name}.rating must be one of -2, -1, 0, 1, 2, or null")
    return int(numeric)


def signal_label(score: float | None) -> str:
    if score is None:
        return "insufficient_data"
    if score >= 60:
        return "strong_positive"
    if score >= 25:
        return "positive"
    if score >= -24:
        return "neutral"
    if score >= -59:
        return "negative"
    return "strong_negative"


def suggested_action(
    signal: str,
    coverage: int,
    gates_complete: bool,
    failed_gates: list[str],
) -> str:
    if coverage < 50:
        return "wait_for_data"
    if failed_gates:
        return "wait_or_reduce_risk"
    if not gates_complete:
        return "analysis_only_until_all_gates_are_checked"
    return {
        "strong_positive": "eligible_for_staged_entry_or_add_if_user_risk_allows",
        "positive": "small_probe_or_hold_and_wait_for_confirmation",
        "neutral": "hold_qualified_positions_or_wait",
        "negative": "avoid_new_entry_and_consider_reduction_at_invalidation",
        "strong_negative": "exit_or_avoid_subject_to_execution_risk",
        "insufficient_data": "wait_for_data",
    }[signal]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate the skill's weighted five-dimension score."
    )
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", default="-", help="Output JSON path, or -")
    args = parser.parse_args()

    try:
        payload = load_json(Path(args.input))
        supplied_dimensions = payload.get("dimensions")
        if not isinstance(supplied_dimensions, dict):
            raise ValueError("dimensions must be an object")

        output_dimensions: dict[str, Any] = {}
        weighted_sum = 0.0
        coverage = 0
        for name, config in DIMENSIONS.items():
            raw = supplied_dimensions.get(name, {})
            if raw is None:
                raw = {}
            if not isinstance(raw, dict):
                raise ValueError(f"dimensions.{name} must be an object or null")
            rating = parse_rating(raw.get("rating"), f"dimensions.{name}")
            evidence = raw.get("evidence")
            counterevidence = raw.get("counterevidence")
            if evidence is not None and not isinstance(evidence, str):
                raise ValueError(f"dimensions.{name}.evidence must be text or null")
            if counterevidence is not None and not isinstance(counterevidence, str):
                raise ValueError(
                    f"dimensions.{name}.counterevidence must be text or null"
                )
            weight = int(config["weight"])
            contribution = None
            if rating is not None:
                coverage += weight
                contribution = weight * rating / 2.0
                weighted_sum += contribution
            output_dimensions[name] = {
                "label": config["label"],
                "weight_pct": weight,
                "rating": rating,
                "weighted_contribution": contribution,
                "evidence": evidence,
                "counterevidence": counterevidence,
            }

        score = 100.0 * weighted_sum / coverage if coverage else None
        signal = signal_label(score)

        raw_gates = payload.get("gates", {})
        if raw_gates is None:
            raw_gates = {}
        if not isinstance(raw_gates, dict):
            raise ValueError("gates must be an object")
        market_raw = str(payload.get("market", "")).strip().upper()
        hk_market = market_raw in {"HK", "HKG", "HKEX", "SEHK"}
        gate_names = list(REQUIRED_GATES)
        if hk_market or "market_rules" in raw_gates:
            gate_names.append("market_rules")
        gates: dict[str, bool | None] = {}
        for name in gate_names:
            value = raw_gates.get(name)
            if value is not None and not isinstance(value, bool):
                raise ValueError(f"gates.{name} must be true, false, or null")
            gates[name] = value
        failed_gates = [name for name, value in gates.items() if value is False]
        unchecked_gates = [name for name, value in gates.items() if value is None]
        gates_complete = not unchecked_gates

        if coverage >= 90:
            confidence_cap = "high_possible"
        elif coverage >= 70:
            confidence_cap = "medium_maximum"
        elif coverage >= 50:
            confidence_cap = "low_maximum"
        else:
            confidence_cap = "insufficient_for_precise_plan"

        if coverage < 50:
            execution_readiness = "insufficient_evidence"
        elif failed_gates:
            execution_readiness = "blocked_by_failed_gates"
        elif unchecked_gates:
            execution_readiness = "analysis_only_until_checks_complete"
        else:
            execution_readiness = "eligible_for_plan_consideration"

        result = {
            "market": market_raw or None,
            "dimensions": output_dimensions,
            "coverage_pct": coverage,
            "weighted_score": round(score, 2) if score is not None else None,
            "score_range": {"minimum": -100, "neutral": 0, "maximum": 100},
            "score_display": (
                f"{score:+.2f} on a -100 to +100 scale"
                if score is not None
                else None
            ),
            "signal": signal,
            "confidence_cap": confidence_cap,
            "evidence_confidence_cap": confidence_cap,
            "confidence_cap_scope": "evidence_coverage_only_not_execution_readiness",
            "execution_readiness": execution_readiness,
            "gates": gates,
            "failed_gates": failed_gates,
            "unchecked_gates": unchecked_gates,
            "suggested_action": suggested_action(
                signal, coverage, gates_complete, failed_gates
            ),
            "warning": (
                "The score organizes sourced evidence. It is not a standalone "
                "buy or sell signal; entry, timing, liquidity, event and user-risk "
                "conditions must still be checked."
            ),
        }

        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output == "-":
            print(rendered)
        else:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
