#!/usr/bin/env python3
"""Run a transparent constant-growth, multi-scenario free-cash-flow DCF."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def round_value(value: float) -> float:
    return round(value, 6)


def read_input(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


def normalize_margins(value: Any) -> list[float]:
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    margins = [finite_number(item, "margin_of_safety_pct") for item in values]
    for margin in margins:
        if margin < 0 or margin >= 100:
            raise ValueError("margin_of_safety_pct must be at least 0 and below 100")
    return margins


def calculate_scenario(
    base_fcf: float,
    shares: float,
    net_debt: float,
    years: int,
    scenario: dict[str, Any],
    margins: list[float],
) -> dict[str, Any]:
    name = str(scenario.get("name", "scenario")).strip() or "scenario"
    growth_pct = finite_number(scenario.get("growth_pct"), f"{name}.growth_pct")
    discount_pct = finite_number(
        scenario.get("discount_pct"), f"{name}.discount_pct"
    )
    terminal_growth_pct = finite_number(
        scenario.get("terminal_growth_pct"), f"{name}.terminal_growth_pct"
    )

    if growth_pct <= -100:
        raise ValueError(f"{name}: growth_pct must be greater than -100")
    if discount_pct <= 0:
        raise ValueError(f"{name}: discount_pct must be greater than 0")
    if terminal_growth_pct <= -100:
        raise ValueError(
            f"{name}: terminal_growth_pct must be greater than -100"
        )
    if discount_pct <= terminal_growth_pct:
        raise ValueError(
            f"{name}: discount_pct must be greater than terminal_growth_pct"
        )

    growth = growth_pct / 100.0
    discount = discount_pct / 100.0
    terminal_growth = terminal_growth_pct / 100.0

    yearly: list[dict[str, float | int]] = []
    projected_fcf = base_fcf
    pv_explicit = 0.0
    for year in range(1, years + 1):
        projected_fcf *= 1.0 + growth
        present_value = projected_fcf / ((1.0 + discount) ** year)
        pv_explicit += present_value
        yearly.append(
            {
                "year": year,
                "projected_fcf": round_value(projected_fcf),
                "present_value": round_value(present_value),
            }
        )

    terminal_value = (
        projected_fcf * (1.0 + terminal_growth) / (discount - terminal_growth)
    )
    pv_terminal = terminal_value / ((1.0 + discount) ** years)
    enterprise_value = pv_explicit + pv_terminal
    equity_value = enterprise_value - net_debt
    value_per_share = equity_value / shares
    terminal_contribution_pct = (
        pv_terminal / enterprise_value * 100.0 if enterprise_value != 0 else 0.0
    )

    warnings: list[str] = []
    if equity_value <= 0:
        warnings.append("equity value is non-positive under this scenario")
    if terminal_contribution_pct > 75:
        warnings.append(
            "terminal value contributes more than 75% of enterprise value; "
            "the result is highly sensitive to long-term assumptions"
        )

    margin_prices = {
        f"{margin:g}%": round_value(value_per_share * (1.0 - margin / 100.0))
        for margin in margins
    }

    return {
        "name": name,
        "assumptions": {
            "growth_pct": growth_pct,
            "discount_pct": discount_pct,
            "terminal_growth_pct": terminal_growth_pct,
        },
        "yearly_projection": yearly,
        "pv_explicit_period": round_value(pv_explicit),
        "terminal_value_at_final_year": round_value(terminal_value),
        "pv_terminal_value": round_value(pv_terminal),
        "terminal_contribution_pct": round_value(terminal_contribution_pct),
        "enterprise_value": round_value(enterprise_value),
        "net_debt": round_value(net_debt),
        "equity_value": round_value(equity_value),
        "value_per_share": round_value(value_per_share),
        "price_after_margin_of_safety": margin_prices,
        "warnings": warnings,
    }


def reverse_implied_growth(
    base_fcf: float,
    shares: float,
    net_debt: float,
    years: int,
    current_price: float,
    reverse_input: dict[str, Any],
) -> dict[str, Any]:
    discount_pct = finite_number(
        reverse_input.get("discount_pct"), "reverse_dcf.discount_pct"
    )
    terminal_growth_pct = finite_number(
        reverse_input.get("terminal_growth_pct"),
        "reverse_dcf.terminal_growth_pct",
    )
    lower_pct = finite_number(
        reverse_input.get("growth_lower_pct", -50),
        "reverse_dcf.growth_lower_pct",
    )
    upper_pct = finite_number(
        reverse_input.get("growth_upper_pct", 150),
        "reverse_dcf.growth_upper_pct",
    )
    if discount_pct <= terminal_growth_pct:
        raise ValueError(
            "reverse_dcf.discount_pct must exceed terminal_growth_pct"
        )
    if lower_pct <= -100 or lower_pct >= upper_pct:
        raise ValueError(
            "reverse_dcf growth bounds must be above -100 and lower than upper"
        )

    def scenario_at(growth_pct: float) -> dict[str, Any]:
        return calculate_scenario(
            base_fcf,
            shares,
            net_debt,
            years,
            {
                "name": "reverse_dcf",
                "growth_pct": growth_pct,
                "discount_pct": discount_pct,
                "terminal_growth_pct": terminal_growth_pct,
            },
            [],
        )

    lower_value = float(scenario_at(lower_pct)["value_per_share"])
    upper_value = float(scenario_at(upper_pct)["value_per_share"])
    if not (lower_value <= current_price <= upper_value):
        return {
            "solved": False,
            "current_price": round_value(current_price),
            "growth_search_range_pct": [lower_pct, upper_pct],
            "value_range_at_bounds": [lower_value, upper_value],
            "warning": (
                "current price is outside the selected growth search range; "
                "do not extrapolate an implied growth rate"
            ),
        }

    low = lower_pct
    high = upper_pct
    for _ in range(100):
        mid = (low + high) / 2.0
        mid_value = float(scenario_at(mid)["value_per_share"])
        if mid_value < current_price:
            low = mid
        else:
            high = mid
    implied_growth = (low + high) / 2.0
    solved = scenario_at(implied_growth)
    warnings: list[str] = []
    if implied_growth > 25:
        warnings.append(
            "implied constant FCF growth exceeds 25%; the market price requires an aggressive long-duration assumption"
        )
    if float(solved["terminal_contribution_pct"]) > 75:
        warnings.append(
            "reverse DCF is dominated by terminal value and is highly assumption-sensitive"
        )
    return {
        "solved": True,
        "current_price": round_value(current_price),
        "implied_constant_fcf_growth_pct": round_value(implied_growth),
        "projection_years": years,
        "discount_pct": discount_pct,
        "terminal_growth_pct": terminal_growth_pct,
        "terminal_contribution_pct": solved["terminal_contribution_pct"],
        "warnings": warnings,
        "interpretation": (
            "This is the constant annual FCF growth required for the simplified "
            "DCF to equal the current price, not a forecast."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate constant-growth DCF scenarios from a JSON input."
    )
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", default="-", help="Output JSON path, or -")
    args = parser.parse_args()

    try:
        payload = read_input(Path(args.input))
        base_fcf = finite_number(payload.get("base_fcf"), "base_fcf")
        shares = finite_number(payload.get("shares"), "shares")
        net_debt = finite_number(payload.get("net_debt", 0), "net_debt")
        years_raw = finite_number(
            payload.get("projection_years", 5), "projection_years"
        )
        years = int(years_raw)
        if years_raw != years or years < 1 or years > 20:
            raise ValueError("projection_years must be an integer from 1 to 20")
        if base_fcf <= 0:
            raise ValueError("base_fcf must be greater than zero")
        if shares <= 0:
            raise ValueError("shares must be greater than zero")

        scenarios = payload.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("scenarios must be a non-empty array")
        if not all(isinstance(item, dict) for item in scenarios):
            raise ValueError("each scenario must be an object")
        margins = normalize_margins(payload.get("margin_of_safety_pct"))

        current_price_raw = payload.get("current_price")
        current_price = None
        if current_price_raw is not None:
            current_price = finite_number(current_price_raw, "current_price")
            if current_price <= 0:
                raise ValueError("current_price must be greater than zero")

        scenario_results = [
            calculate_scenario(
                base_fcf, shares, net_debt, years, scenario, margins
            )
            for scenario in scenarios
        ]
        if current_price is not None:
            for result in scenario_results:
                value_per_share = float(result["value_per_share"])
                result["upside_downside_from_current_price_pct"] = round_value(
                    (value_per_share / current_price - 1.0) * 100.0
                )

        values = [float(item["value_per_share"]) for item in scenario_results]
        sensitivity_warnings: list[str] = []
        positive_values = [value for value in values if value > 0]
        spread_ratio = None
        if len(positive_values) >= 2:
            spread_ratio = max(positive_values) / min(positive_values)
            if spread_ratio > 3:
                sensitivity_warnings.append(
                    "scenario values span more than 3x; report a wide range and lower valuation confidence"
                )

        reverse_result = None
        reverse_input = payload.get("reverse_dcf")
        if reverse_input is not None:
            if current_price is None:
                raise ValueError("current_price is required when reverse_dcf is supplied")
            if not isinstance(reverse_input, dict):
                raise ValueError("reverse_dcf must be an object")
            reverse_result = reverse_implied_growth(
                base_fcf,
                shares,
                net_debt,
                years,
                current_price,
                reverse_input,
            )

        output = {
            "inputs": {
                "base_fcf": base_fcf,
                "shares": shares,
                "net_debt": net_debt,
                "projection_years": years,
                "margin_of_safety_pct": margins,
                "current_price": current_price,
            },
            "scenarios": scenario_results,
            "scenario_value_spread_ratio": (
                round_value(spread_ratio) if spread_ratio is not None else None
            ),
            "sensitivity_warnings": sensitivity_warnings,
            "reverse_dcf": reverse_result,
            "method_note": (
                "This is a simplified constant-growth DCF. Normalize base FCF, "
                "use diluted shares, and replace it with a year-by-year model "
                "when margins or growth change materially."
            ),
        }

        rendered = json.dumps(output, ensure_ascii=False, indent=2)
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
