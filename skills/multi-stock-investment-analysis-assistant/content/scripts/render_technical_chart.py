#!/usr/bin/env python3
"""Render a reproducible multi-panel equity technical chart from local OHLCV."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Optional

sys.dont_write_bytecode = True
MPL_CONFIG = Path(os.environ.setdefault("MPLCONFIGDIR", "/tmp/investment-analysis-mpl"))
MPL_CONFIG.mkdir(parents=True, exist_ok=True)

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import FuncFormatter, MaxNLocator
except ImportError as exc:  # pragma: no cover - environment failure path
    print(f"error: matplotlib is required to render the chart: {exc}", file=sys.stderr)
    raise SystemExit(2)

from analyze_ohlcv import build_analysis, parse_datetime, read_ohlcv


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must contain a JSON object")
    return payload


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{label} must be a positive finite number")
    return result


def date_only(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a date or timestamp")
    return parse_datetime(value).date().isoformat()


def close_enough(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-8, abs_tol=1e-6)


def load_plan_annotations(
    plan_path: Optional[Path],
    validation_path: Optional[Path],
    latest_bar_date: str,
) -> Optional[dict[str, Any]]:
    if (plan_path is None) != (validation_path is None):
        raise ValueError("--plan-input and --plan-validation must be supplied together")
    if plan_path is None or validation_path is None:
        return None

    plan = load_json_object(plan_path, "plan input")
    validation = load_json_object(validation_path, "plan validation")
    if validation.get("status") != "plan_passes_internal_checks":
        raise ValueError(
            "strategy levels may be charted only when validation status is "
            "plan_passes_internal_checks"
        )

    context = plan.get("data_context")
    if not isinstance(context, dict):
        raise ValueError("plan input is missing data_context")
    indicator_date = date_only(context.get("indicator_date"), "indicator_date")
    if indicator_date != latest_bar_date:
        raise ValueError(
            f"plan indicator date {indicator_date} does not match chart bar {latest_bar_date}"
        )

    side = str(plan.get("side", "long")).lower()
    if side not in {"long", "short"}:
        raise ValueError("plan side must be long or short")
    if str(validation.get("side", "")).lower() != side:
        raise ValueError("plan and validation sides do not match")

    entries_raw = plan.get("entries")
    if not isinstance(entries_raw, list) or not entries_raw:
        raise ValueError("plan entries must be a non-empty array")
    entries: list[dict[str, float | str]] = []
    weighted_numerator = 0.0
    total_weight = 0.0
    for index, item in enumerate(entries_raw):
        if not isinstance(item, dict):
            raise ValueError(f"plan entry {index + 1} must be an object")
        price = finite_number(item.get("price"), f"entry {index + 1} price")
        weight = finite_number(item.get("weight_pct"), f"entry {index + 1} weight")
        entries.append({"label": f"E{index + 1}", "price": price})
        weighted_numerator += price * weight
        total_weight += weight
    weighted_entry = weighted_numerator / total_weight
    validated_entry = finite_number(validation.get("weighted_entry"), "validated entry")
    if not close_enough(weighted_entry, validated_entry):
        raise ValueError("weighted entry differs between plan and validation")

    stop = finite_number(plan.get("stop"), "plan stop")
    validated_stop = finite_number(validation.get("stop"), "validated stop")
    if not close_enough(stop, validated_stop):
        raise ValueError("stop differs between plan and validation")

    plan_targets = plan.get("targets")
    validated_targets = validation.get("targets")
    if not isinstance(plan_targets, list) or not isinstance(validated_targets, list):
        raise ValueError("plan and validation must contain target arrays")
    if len(plan_targets) != len(validated_targets):
        raise ValueError("target counts differ between plan and validation")
    targets: list[dict[str, float | str]] = []
    for index, (raw, checked) in enumerate(zip(plan_targets, validated_targets)):
        if not isinstance(raw, dict) or not isinstance(checked, dict):
            raise ValueError(f"target {index + 1} must be an object")
        raw_price = finite_number(raw.get("price"), f"target {index + 1} price")
        checked_price = finite_number(
            checked.get("price"), f"validated target {index + 1} price"
        )
        if not close_enough(raw_price, checked_price):
            raise ValueError(f"target {index + 1} differs between plan and validation")
        targets.append({"label": f"T{index + 1}", "price": raw_price})

    return {
        "side": side,
        "entries": entries,
        "weighted_entry": validated_entry,
        "stop": stop,
        "targets": targets,
    }


def compact_number(value: float, _position: int = 0) -> str:
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def nullable(values: list[Optional[float]]) -> list[float]:
    return [float("nan") if value is None else float(value) for value in values]


def has_values(values: list[Optional[float]]) -> bool:
    return any(value is not None and math.isfinite(float(value)) for value in values)


def configure_axis(axis: Any) -> None:
    axis.grid(axis="y", color="#d8dee9", linewidth=0.7, alpha=0.65)
    axis.set_facecolor("#fbfcfe")
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color("#94a3b8")
    axis.spines["bottom"].set_color("#94a3b8")
    axis.tick_params(colors="#475569", labelsize=8)


def plot_candles(
    axis: Any,
    rows: list[dict[str, float | str]],
    up_color: str,
    down_color: str,
) -> None:
    visible_range = max(float(row["high"]) for row in rows) - min(
        float(row["low"]) for row in rows
    )
    minimum_body = max(visible_range * 0.0015, 1e-9)
    for index, row in enumerate(rows):
        open_price = float(row["open"])
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        color = up_color if close >= open_price else down_color
        axis.vlines(index, low, high, color=color, linewidth=0.85, zorder=2)
        body_low = min(open_price, close)
        body_height = max(abs(close - open_price), minimum_body)
        axis.add_patch(
            Rectangle(
                (index - 0.31, body_low),
                0.62,
                body_height,
                facecolor=color,
                edgecolor=color,
                linewidth=0.6,
                zorder=3,
            )
        )


def add_price_line(
    axis: Any,
    price: float,
    label: str,
    color: str,
    style: str,
    visible_low: float,
    visible_high: float,
    x_end: int,
    off_chart: list[str],
    label_positions: list[float],
) -> None:
    span = max(visible_high - visible_low, visible_high * 0.01, 1e-6)
    if price < visible_low - span * 0.15 or price > visible_high + span * 0.15:
        off_chart.append(f"{label} {price:.2f}")
        return
    axis.axhline(price, color=color, linestyle=style, linewidth=1.0, alpha=0.9)
    label_y = price
    minimum_gap = span * 0.027
    direction = 1.0
    attempts = 0
    while any(abs(label_y - used) < minimum_gap for used in label_positions):
        attempts += 1
        direction = 1.0 if attempts % 2 else -1.0
        label_y = price + direction * math.ceil(attempts / 2) * minimum_gap
    label_positions.append(label_y)
    if not close_enough(label_y, price):
        axis.plot(
            [x_end + 0.05, x_end + 0.28],
            [price, label_y],
            color=color,
            linewidth=0.7,
            alpha=0.8,
            clip_on=False,
        )
    axis.text(
        x_end + 0.35,
        label_y,
        f"{label} {price:.2f}",
        color=color,
        fontsize=7.5,
        va="center",
        clip_on=False,
    )


def render_chart(args: argparse.Namespace) -> dict[str, Any]:
    rows, warnings = read_ohlcv(Path(args.input))
    if args.last_bar_status == "incomplete":
        if len(rows) < 3:
            raise ValueError("not enough rows remain after excluding the incomplete bar")
        removed = rows.pop()
        warnings.append(f"excluded incomplete last bar {removed['date']}")

    analysis, series = build_analysis(rows, warnings)
    latest_date = date_only(analysis["metadata"]["end"], "latest completed bar")
    if args.as_of:
        as_of = parse_datetime(args.as_of)
        latest = parse_datetime(str(analysis["metadata"]["end"]))
        age_days = (as_of.date() - latest.date()).days
        if age_days < 0:
            raise ValueError("latest completed bar is later than --as-of")
        if age_days > 7 and not args.allow_stale:
            raise ValueError(
                "latest completed bar is more than 7 calendar days old; "
                "refresh data or use --allow-stale only for historical work"
            )
        if age_days > 4:
            warnings.append(f"latest completed bar is {age_days} calendar days old")

    if args.bars < 20:
        raise ValueError("--bars must be at least 20")
    start = max(0, len(rows) - args.bars)
    chart_rows = rows[start:]
    chart_series = {name: values[start:] for name, values in series.items()}
    plan = load_plan_annotations(
        Path(args.plan_input) if args.plan_input else None,
        Path(args.plan_validation) if args.plan_validation else None,
        latest_date,
    )

    up_color, down_color = (
        ("#16a34a", "#dc2626")
        if args.color_convention == "us"
        else ("#dc2626", "#16a34a")
    )
    oscillator_enabled = args.oscillator != "none"
    ratios = [5.0, 1.45, 1.75] + ([1.55] if oscillator_enabled else [])
    height = 11.0 if oscillator_enabled else 9.2
    fig, raw_axes = plt.subplots(
        len(ratios),
        1,
        figsize=(15.5, height),
        sharex=True,
        gridspec_kw={"height_ratios": ratios},
    )
    axes = list(raw_axes) if hasattr(raw_axes, "__iter__") else [raw_axes]
    for axis in axes:
        configure_axis(axis)

    price_axis, volume_axis, macd_axis = axes[:3]
    oscillator_axis = axes[3] if oscillator_enabled else None
    x_values = list(range(len(chart_rows)))
    plot_candles(price_axis, chart_rows, up_color, down_color)

    ma_styles = {
        "ma5": ("MA5", "#d97706", 1.0),
        "ma10": ("MA10", "#2563eb", 1.0),
        "ma20": ("MA20", "#7c3aed", 1.15),
        "ma50": ("MA50", "#ea580c", 1.25),
        "ma200": ("MA200", "#111827", 1.45),
    }
    for key, (label, color, width) in ma_styles.items():
        values = chart_series[key]
        if has_values(values):
            price_axis.plot(
                x_values, nullable(values), label=label, color=color, linewidth=width
            )

    if args.bollinger:
        upper = chart_series["bollinger_upper"]
        lower = chart_series["bollinger_lower"]
        if has_values(upper) and has_values(lower):
            price_axis.plot(
                x_values,
                nullable(upper),
                color="#64748b",
                linestyle="--",
                linewidth=0.9,
                label="BOLL(20,2)",
            )
            price_axis.plot(
                x_values,
                nullable(lower),
                color="#64748b",
                linestyle="--",
                linewidth=0.9,
            )

    price_axis.set_ylabel(f"Price ({args.currency})", fontsize=9, color="#334155")
    price_axis.set_title(
        "Candlestick + moving averages", loc="left", fontsize=10, color="#0f172a"
    )
    price_axis.legend(loc="upper left", ncol=6, fontsize=7.5, frameon=False)

    visible_low = min(float(row["low"]) for row in chart_rows)
    visible_high = max(float(row["high"]) for row in chart_rows)
    off_chart: list[str] = []
    label_positions: list[float] = []
    levels = analysis.get("levels", {})
    prior_high = levels.get("prior_high20") if isinstance(levels, dict) else None
    prior_low = levels.get("prior_low20") if isinstance(levels, dict) else None
    if prior_high is not None:
        add_price_line(
            price_axis,
            float(prior_high),
            "R20",
            "#b91c1c",
            ":",
            visible_low,
            visible_high,
            len(chart_rows) - 1,
            off_chart,
            label_positions,
        )
    if prior_low is not None:
        add_price_line(
            price_axis,
            float(prior_low),
            "S20",
            "#15803d",
            ":",
            visible_low,
            visible_high,
            len(chart_rows) - 1,
            off_chart,
            label_positions,
        )

    if plan:
        for entry in plan["entries"][:3]:
            add_price_line(
                price_axis,
                float(entry["price"]),
                str(entry["label"]),
                "#2563eb",
                "--",
                visible_low,
                visible_high,
                len(chart_rows) - 1,
                off_chart,
                label_positions,
            )
        add_price_line(
            price_axis,
            float(plan["weighted_entry"]),
            "Avg",
            "#1d4ed8",
            "-",
            visible_low,
            visible_high,
            len(chart_rows) - 1,
            off_chart,
            label_positions,
        )
        add_price_line(
            price_axis,
            float(plan["stop"]),
            "Stop",
            "#b91c1c",
            "-.",
            visible_low,
            visible_high,
            len(chart_rows) - 1,
            off_chart,
            label_positions,
        )
        for target in plan["targets"][:3]:
            add_price_line(
                price_axis,
                float(target["price"]),
                str(target["label"]),
                "#047857",
                "--",
                visible_low,
                visible_high,
                len(chart_rows) - 1,
                off_chart,
                label_positions,
            )
    if off_chart:
        price_axis.text(
            0.995,
            0.02,
            "Off-chart: " + ", ".join(off_chart[:5]),
            transform=price_axis.transAxes,
            ha="right",
            va="bottom",
            fontsize=7,
            color="#64748b",
        )

    volumes = [float(row["volume"]) for row in chart_rows]
    volume_available = bool(analysis["data_quality"]["volume_available"])
    if volume_available:
        volume_colors = [
            up_color if float(row["close"]) >= float(row["open"]) else down_color
            for row in chart_rows
        ]
        volume_axis.bar(x_values, volumes, color=volume_colors, width=0.66, alpha=0.72)
        for key, label, color in (
            ("mavol5", "MAVOL5", "#d97706"),
            ("mavol10", "MAVOL10", "#2563eb"),
            ("mavol20", "MAVOL20", "#7c3aed"),
        ):
            values = chart_series[key]
            if has_values(values):
                volume_axis.plot(
                    x_values, nullable(values), label=label, color=color, linewidth=1.0
                )
        volume_axis.legend(loc="upper left", ncol=3, fontsize=7.5, frameon=False)
    else:
        volume_axis.text(
            0.5,
            0.5,
            "Volume unavailable; MAVOL not calculated",
            transform=volume_axis.transAxes,
            ha="center",
            va="center",
            color="#64748b",
            fontsize=9,
        )
        volume_axis.set_yticks([])
    volume_axis.set_ylabel("Volume", fontsize=9, color="#334155")
    volume_axis.set_title(
        "Volume + MAVOL", loc="left", fontsize=10, color="#0f172a"
    )
    volume_axis.yaxis.set_major_formatter(FuncFormatter(compact_number))
    volume_axis.yaxis.set_major_locator(MaxNLocator(nbins=4))

    macd = chart_series["macd"]
    signal = chart_series["macd_signal"]
    histogram = chart_series["macd_histogram"]
    valid_hist = [index for index, value in enumerate(histogram) if value is not None]
    if valid_hist:
        hist_values = [float(histogram[index]) for index in valid_hist]
        hist_colors = [up_color if value >= 0 else down_color for value in hist_values]
        macd_axis.bar(
            valid_hist, hist_values, color=hist_colors, width=0.66, alpha=0.72, label="HIST"
        )
    if has_values(macd):
        macd_axis.plot(
            x_values, nullable(macd), color="#2563eb", linewidth=1.15, label="DIF"
        )
    if has_values(signal):
        macd_axis.plot(
            x_values, nullable(signal), color="#d97706", linewidth=1.15, label="DEA"
        )
    if not has_values(signal):
        macd_axis.text(
            0.5,
            0.5,
            "Insufficient data for complete MACD(12,26,9)",
            transform=macd_axis.transAxes,
            ha="center",
            va="center",
            color="#64748b",
            fontsize=9,
        )
    macd_axis.axhline(0, color="#64748b", linewidth=0.8)
    macd_axis.set_ylabel("MACD", fontsize=9, color="#334155")
    macd_axis.set_title(
        "MACD (12,26,9; HIST = DIF - DEA)",
        loc="left",
        fontsize=10,
        color="#0f172a",
    )
    handles, labels = macd_axis.get_legend_handles_labels()
    if handles:
        macd_axis.legend(loc="upper left", ncol=3, fontsize=7.5, frameon=False)

    if oscillator_axis is not None:
        if args.oscillator == "rsi":
            values = chart_series["rsi14"]
            if has_values(values):
                oscillator_axis.plot(
                    x_values, nullable(values), color="#7c3aed", linewidth=1.2, label="RSI14"
                )
            else:
                oscillator_axis.text(
                    0.5,
                    0.5,
                    "Insufficient data for RSI14",
                    transform=oscillator_axis.transAxes,
                    ha="center",
                    va="center",
                    color="#64748b",
                )
            for level, style in ((70, "--"), (50, ":"), (30, "--")):
                oscillator_axis.axhline(level, color="#94a3b8", linestyle=style, linewidth=0.8)
            oscillator_axis.set_ylim(0, 100)
            oscillator_axis.set_ylabel("RSI", fontsize=9, color="#334155")
            oscillator_axis.set_title("RSI14", loc="left", fontsize=10, color="#0f172a")
        elif args.oscillator == "kdj":
            for key, label, color in (
                ("kdj_k", "K", "#2563eb"),
                ("kdj_d", "D", "#d97706"),
                ("kdj_j", "J", "#7c3aed"),
            ):
                values = chart_series[key]
                if has_values(values):
                    oscillator_axis.plot(
                        x_values, nullable(values), color=color, linewidth=1.0, label=label
                    )
            oscillator_axis.axhline(80, color="#94a3b8", linestyle="--", linewidth=0.8)
            oscillator_axis.axhline(20, color="#94a3b8", linestyle="--", linewidth=0.8)
            oscillator_axis.set_ylim(-20, 120)
            oscillator_axis.set_ylabel("KDJ", fontsize=9, color="#334155")
            oscillator_axis.set_title("KDJ (9,3,3)", loc="left", fontsize=10, color="#0f172a")
        else:
            obv = chart_series["obv"]
            obv_ma = chart_series["obv_ma20"]
            if has_values(obv):
                oscillator_axis.plot(
                    x_values, nullable(obv), color="#2563eb", linewidth=1.1, label="OBV"
                )
            if has_values(obv_ma):
                oscillator_axis.plot(
                    x_values,
                    nullable(obv_ma),
                    color="#d97706",
                    linewidth=1.1,
                    label="OBV-MA20",
                )
            if not has_values(obv):
                oscillator_axis.text(
                    0.5,
                    0.5,
                    "Volume unavailable; OBV not calculated",
                    transform=oscillator_axis.transAxes,
                    ha="center",
                    va="center",
                    color="#64748b",
                )
                oscillator_axis.set_yticks([])
            else:
                oscillator_axis.yaxis.set_major_formatter(FuncFormatter(compact_number))
            oscillator_axis.set_ylabel("OBV", fontsize=9, color="#334155")
            oscillator_axis.set_title("OBV + OBV-MA20", loc="left", fontsize=10, color="#0f172a")
        handles, labels = oscillator_axis.get_legend_handles_labels()
        if handles:
            oscillator_axis.legend(loc="upper left", ncol=3, fontsize=7.5, frameon=False)

    for axis in axes[:-1]:
        axis.tick_params(labelbottom=False)
    tick_count = min(7, len(chart_rows))
    tick_positions = sorted(
        {
            round(index * (len(chart_rows) - 1) / max(tick_count - 1, 1))
            for index in range(tick_count)
        }
    )
    tick_labels = [
        parse_datetime(str(chart_rows[index]["date"])).strftime("%Y-%m-%d")
        for index in tick_positions
    ]
    axes[-1].set_xticks(tick_positions)
    axes[-1].set_xticklabels(tick_labels, rotation=0, ha="center", fontsize=8)
    axes[-1].set_xlabel("Completed trading sessions", fontsize=9, color="#334155")
    for axis in axes:
        axis.set_xlim(-1, len(chart_rows) + 7)

    start_date = date_only(chart_rows[0]["date"], "chart start")
    symbol = args.symbol.strip().upper()
    fig.suptitle(
        f"{symbol} daily technical structure | {start_date} to {latest_date}",
        x=0.08,
        y=0.982,
        ha="left",
        fontsize=15,
        fontweight="bold",
        color="#0f172a",
    )
    subtitle = (
        f"{len(chart_rows)} displayed completed bars ({len(rows)} available) | "
        f"Color convention: {args.color_convention.upper()} | Latest completed bar: {latest_date}"
    )
    fig.text(0.08, 0.952, subtitle, ha="left", fontsize=8.5, color="#475569")
    footer = f"Source: {args.source_label.strip()} | Basis: {args.basis.strip()}"
    if warnings:
        footer += f" | Data warnings: {len(warnings)}"
    fig.text(0.08, 0.018, footer[:260], ha="left", fontsize=7.8, color="#64748b")
    fig.subplots_adjust(top=0.91, bottom=0.075, left=0.08, right=0.91, hspace=0.12)

    output = Path(args.output)
    if output.suffix.lower() not in {".png", ".svg"}:
        raise ValueError("--output must end in .png or .svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=args.dpi, facecolor="#ffffff", bbox_inches="tight")
    plt.close(fig)

    metadata = {
        "output": str(output.resolve()),
        "symbol": symbol,
        "latest_completed_bar": latest_date,
        "display_start": start_date,
        "displayed_bars": len(chart_rows),
        "available_bars": len(rows),
        "panels": ["candlestick_ma", "volume_mavol", "macd"]
        + ([args.oscillator] if oscillator_enabled else []),
        "volume_available": volume_available,
        "strategy_annotations": plan is not None,
        "basis": args.basis.strip(),
        "source_label": args.source_label.strip(),
        "currency": args.currency,
        "color_convention": args.color_convention,
        "warnings": warnings,
    }
    if args.metadata_output:
        Path(args.metadata_output).write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render candlestick/MA, volume/MAVOL, MACD, and an optional oscillator "
            "from a local daily OHLCV CSV."
        )
    )
    parser.add_argument("--input", required=True, help="Input OHLCV CSV")
    parser.add_argument("--output", required=True, help="Output .png or .svg")
    parser.add_argument("--symbol", required=True, help="Ticker shown in the title")
    parser.add_argument("--source-label", required=True, help="Actual OHLCV data source")
    parser.add_argument("--basis", required=True, help="Adjustment/basis description")
    parser.add_argument(
        "--last-bar-status",
        required=True,
        choices=("completed", "incomplete"),
        help="Whether the final CSV row is a completed daily bar",
    )
    parser.add_argument("--bars", type=int, default=120, help="Displayed completed bars")
    parser.add_argument(
        "--oscillator",
        choices=("rsi", "kdj", "obv", "none"),
        default="rsi",
        help="Fourth panel",
    )
    parser.add_argument("--bollinger", action="store_true", help="Overlay Bollinger bands")
    parser.add_argument(
        "--color-convention",
        choices=("us", "cn"),
        required=True,
        help="US: green up/red down; CN: red up/green down",
    )
    parser.add_argument(
        "--currency",
        required=True,
        help="Explicit price-axis currency label, for example USD, HKD, or CNY",
    )
    parser.add_argument("--as-of", help="ISO-8601 timestamp for freshness checking")
    parser.add_argument(
        "--allow-stale",
        action="store_true",
        help="Allow bars older than seven days for explicitly historical work",
    )
    parser.add_argument("--plan-input", help="Trade-plan JSON used for validation")
    parser.add_argument("--plan-validation", help="Passing validation result JSON")
    parser.add_argument("--metadata-output", help="Optional chart metadata JSON")
    parser.add_argument("--dpi", type=int, default=160, help="PNG output DPI")
    return parser.parse_args()


def main() -> int:
    try:
        metadata = render_chart(parse_args())
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
