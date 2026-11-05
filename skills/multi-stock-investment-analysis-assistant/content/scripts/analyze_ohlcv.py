#!/usr/bin/env python3
"""Calculate reproducible technical indicators from daily OHLCV CSV data."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


def normalize_header(value: str) -> str:
    return "".join(ch for ch in value.strip().lower() if ch.isalnum())


HEADER_ALIASES = {
    "date": {"date", "datetime", "timestamp", "time"},
    "open": {"open", "openprice"},
    "high": {"high", "highprice"},
    "low": {"low", "lowprice"},
    "close": {"close", "closeprice"},
    "volume": {"volume", "vol", "sharevolume"},
}


def parse_datetime(value: str) -> datetime:
    raw = value.strip()
    if not raw:
        raise ValueError("empty date")
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"unsupported date format: {raw}")


def parse_number(value: Optional[str], field: str, row_number: int) -> float:
    if value is None or not value.strip():
        raise ValueError(f"row {row_number}: missing {field}")
    cleaned = value.strip().replace(",", "")
    try:
        result = float(cleaned)
    except ValueError as exc:
        raise ValueError(f"row {row_number}: invalid {field} value {value!r}") from exc
    if not math.isfinite(result):
        raise ValueError(f"row {row_number}: non-finite {field}")
    return result


def resolve_columns(fieldnames: Iterable[str]) -> dict[str, Optional[str]]:
    normalized = {normalize_header(name): name for name in fieldnames if name}
    resolved: dict[str, Optional[str]] = {}
    for canonical, aliases in HEADER_ALIASES.items():
        resolved[canonical] = next(
            (normalized[alias] for alias in aliases if alias in normalized), None
        )
    missing = [name for name in ("date", "open", "high", "low", "close") if not resolved[name]]
    if missing:
        raise ValueError("missing required CSV columns: " + ", ".join(missing))
    return resolved


def read_ohlcv(path: Path) -> tuple[list[dict[str, float | str]], list[str]]:
    warnings: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        columns = resolve_columns(reader.fieldnames)
        rows_by_time: dict[datetime, dict[str, float | str]] = {}
        for row_number, raw in enumerate(reader, start=2):
            if not any((value or "").strip() for value in raw.values()):
                continue
            dt = parse_datetime(raw[columns["date"]] or "")
            row: dict[str, float | str] = {
                "date": dt.isoformat(),
                "open": parse_number(raw[columns["open"]], "open", row_number),
                "high": parse_number(raw[columns["high"]], "high", row_number),
                "low": parse_number(raw[columns["low"]], "low", row_number),
                "close": parse_number(raw[columns["close"]], "close", row_number),
            }
            volume_column = columns["volume"]
            if volume_column and raw[volume_column] and raw[volume_column].strip():
                row["volume"] = parse_number(raw[volume_column], "volume", row_number)
            else:
                row["volume"] = 0.0
            for price_field in ("open", "high", "low", "close"):
                if float(row[price_field]) <= 0:
                    raise ValueError(
                        f"row {row_number}: {price_field} must be greater than zero"
                    )
            if float(row["volume"]) < 0:
                raise ValueError(f"row {row_number}: volume cannot be negative")
            if row["low"] > row["high"]:
                raise ValueError(f"row {row_number}: low is greater than high")
            if row["high"] < max(row["open"], row["close"]) or row["low"] > min(
                row["open"], row["close"]
            ):
                warnings.append(
                    f"row {row_number}: OHLC relationship is inconsistent; inspect source data"
                )
            if dt in rows_by_time:
                warnings.append(f"duplicate timestamp {dt.isoformat()}; kept the last row")
            rows_by_time[dt] = row

    rows = [rows_by_time[key] for key in sorted(rows_by_time)]
    if len(rows) < 2:
        raise ValueError("at least two data rows are required")
    weekend_rows = sum(
        1
        for row in rows
        if parse_datetime(str(row["date"])).weekday() >= 5
    )
    if weekend_rows:
        warnings.append(
            f"daily US-equity data includes {weekend_rows} weekend rows; "
            "verify the security, frequency, and trading calendar before using indicators"
        )
    if not columns["volume"]:
        warnings.append("volume column not found; volume indicators are unavailable")
    if len(rows) < 252:
        warnings.append(
            f"only {len(rows)} rows supplied; MA200 and 52-week context may be unavailable or weak"
        )
    return rows, warnings


def sma(values: list[float], period: int) -> list[Optional[float]]:
    result: list[Optional[float]] = [None] * len(values)
    running = 0.0
    for index, value in enumerate(values):
        running += value
        if index >= period:
            running -= values[index - period]
        if index >= period - 1:
            result[index] = running / period
    return result


def ema(values: list[float], period: int) -> list[Optional[float]]:
    result: list[Optional[float]] = [None] * len(values)
    if len(values) < period:
        return result
    seed = sum(values[:period]) / period
    result[period - 1] = seed
    multiplier = 2.0 / (period + 1)
    previous = seed
    for index in range(period, len(values)):
        previous = (values[index] - previous) * multiplier + previous
        result[index] = previous
    return result


def ema_nullable(values: list[Optional[float]], period: int) -> list[Optional[float]]:
    result: list[Optional[float]] = [None] * len(values)
    available = [(index, value) for index, value in enumerate(values) if value is not None]
    if len(available) < period:
        return result
    seed_values = [float(value) for _, value in available[:period]]
    seed_index = available[period - 1][0]
    previous = sum(seed_values) / period
    result[seed_index] = previous
    multiplier = 2.0 / (period + 1)
    for index, value in available[period:]:
        previous = (float(value) - previous) * multiplier + previous
        result[index] = previous
    return result


def rsi_wilder(values: list[float], period: int = 14) -> list[Optional[float]]:
    result: list[Optional[float]] = [None] * len(values)
    if len(values) <= period:
        return result
    gains = [max(values[i] - values[i - 1], 0.0) for i in range(1, len(values))]
    losses = [max(values[i - 1] - values[i], 0.0) for i in range(1, len(values))]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    def to_rsi(gain: float, loss: float) -> float:
        if gain == 0 and loss == 0:
            return 50.0
        if loss == 0:
            return 100.0
        rs = gain / loss
        return 100.0 - 100.0 / (1.0 + rs)

    result[period] = to_rsi(avg_gain, avg_loss)
    for index in range(period + 1, len(values)):
        avg_gain = (avg_gain * (period - 1) + gains[index - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[index - 1]) / period
        result[index] = to_rsi(avg_gain, avg_loss)
    return result


def atr_wilder(
    highs: list[float], lows: list[float], closes: list[float], period: int = 14
) -> list[Optional[float]]:
    true_ranges: list[float] = []
    for index, high in enumerate(highs):
        if index == 0:
            true_ranges.append(high - lows[index])
        else:
            true_ranges.append(
                max(
                    high - lows[index],
                    abs(high - closes[index - 1]),
                    abs(lows[index] - closes[index - 1]),
                )
            )
    result: list[Optional[float]] = [None] * len(closes)
    if len(true_ranges) < period:
        return result
    previous = sum(true_ranges[:period]) / period
    result[period - 1] = previous
    for index in range(period, len(true_ranges)):
        previous = (previous * (period - 1) + true_ranges[index]) / period
        result[index] = previous
    return result


def bollinger(
    values: list[float], period: int = 20, deviations: float = 2.0
) -> tuple[list[Optional[float]], list[Optional[float]], list[Optional[float]]]:
    middle = sma(values, period)
    upper: list[Optional[float]] = [None] * len(values)
    lower: list[Optional[float]] = [None] * len(values)
    for index in range(period - 1, len(values)):
        window = values[index - period + 1 : index + 1]
        standard_deviation = statistics.pstdev(window)
        upper[index] = float(middle[index]) + deviations * standard_deviation
        lower[index] = float(middle[index]) - deviations * standard_deviation
    return middle, upper, lower


def kdj(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    period: int = 9,
    smoothing: int = 3,
) -> tuple[list[Optional[float]], list[Optional[float]], list[Optional[float]]]:
    k_values: list[Optional[float]] = [None] * len(closes)
    d_values: list[Optional[float]] = [None] * len(closes)
    j_values: list[Optional[float]] = [None] * len(closes)
    if len(closes) < period:
        return k_values, d_values, j_values
    previous_k = 50.0
    previous_d = 50.0
    alpha = 1.0 / smoothing
    for index in range(period - 1, len(closes)):
        highest = max(highs[index - period + 1 : index + 1])
        lowest = min(lows[index - period + 1 : index + 1])
        rsv = (
            (closes[index] - lowest) / (highest - lowest) * 100.0
            if highest != lowest
            else 50.0
        )
        current_k = previous_k * (1.0 - alpha) + rsv * alpha
        current_d = previous_d * (1.0 - alpha) + current_k * alpha
        current_j = 3.0 * current_k - 2.0 * current_d
        k_values[index] = current_k
        d_values[index] = current_d
        j_values[index] = current_j
        previous_k = current_k
        previous_d = current_d
    return k_values, d_values, j_values


def on_balance_volume(closes: list[float], volumes: list[float]) -> list[float]:
    result = [0.0] * len(closes)
    for index in range(1, len(closes)):
        if closes[index] > closes[index - 1]:
            result[index] = result[index - 1] + volumes[index]
        elif closes[index] < closes[index - 1]:
            result[index] = result[index - 1] - volumes[index]
        else:
            result[index] = result[index - 1]
    return result


def prior_average_ratio(values: list[float], period: int = 20) -> list[Optional[float]]:
    result: list[Optional[float]] = [None] * len(values)
    for index in range(period, len(values)):
        baseline = sum(values[index - period : index]) / period
        if baseline > 0:
            result[index] = values[index] / baseline
    return result


def rolling_extreme(values: list[float], period: int, mode: str) -> Optional[float]:
    if not values:
        return None
    window = values[-min(period, len(values)) :]
    return max(window) if mode == "high" else min(window)


def prior_extreme(values: list[float], period: int, mode: str) -> Optional[float]:
    if len(values) < 2:
        return None
    window = values[max(0, len(values) - period - 1) : -1]
    if not window:
        return None
    return max(window) if mode == "high" else min(window)


def pct_change(values: list[float], periods: int) -> Optional[float]:
    if len(values) <= periods or values[-periods - 1] == 0:
        return None
    return (values[-1] / values[-periods - 1] - 1.0) * 100.0


def rounded(value: Optional[float], digits: int = 6) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), digits)


def build_analysis(
    rows: list[dict[str, float | str]], warnings: list[str]
) -> tuple[dict[str, object], dict[str, list[Optional[float]]]]:
    opens = [float(row["open"]) for row in rows]
    highs = [float(row["high"]) for row in rows]
    lows = [float(row["low"]) for row in rows]
    closes = [float(row["close"]) for row in rows]
    volumes = [float(row["volume"]) for row in rows]

    zero_volume_rows = sum(1 for volume in volumes if volume == 0)
    possible_outliers: list[str] = []
    for index in range(1, len(closes)):
        move = abs(closes[index] / closes[index - 1] - 1.0)
        if move >= 0.40:
            possible_outliers.append(str(rows[index]["date"]))
    if possible_outliers:
        warnings.append(
            "one-day close moves of at least 40% were found; verify splits, "
            "corporate actions, or bad ticks before using technical levels: "
            + ", ".join(possible_outliers[:5])
        )

    ma5 = sma(closes, 5)
    ma10 = sma(closes, 10)
    ma20 = sma(closes, 20)
    ma50 = sma(closes, 50)
    ma200 = sma(closes, 200)
    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    macd: list[Optional[float]] = [
        (float(fast) - float(slow)) if fast is not None and slow is not None else None
        for fast, slow in zip(ema12, ema26)
    ]
    macd_signal = ema_nullable(macd, 9)
    macd_hist: list[Optional[float]] = [
        (float(line) - float(signal))
        if line is not None and signal is not None
        else None
        for line, signal in zip(macd, macd_signal)
    ]
    rsi14 = rsi_wilder(closes, 14)
    atr14 = atr_wilder(highs, lows, closes, 14)
    bb_mid, bb_upper, bb_lower = bollinger(closes, 20, 2.0)
    bb_bandwidth: list[Optional[float]] = [
        ((float(upper) - float(lower)) / float(middle) * 100.0)
        if upper is not None
        and lower is not None
        and middle is not None
        and float(middle) != 0
        else None
        for middle, upper, lower in zip(bb_mid, bb_upper, bb_lower)
    ]
    kdj_k, kdj_d, kdj_j = kdj(highs, lows, closes, 9, 3)
    volume_available = any(volume > 0 for volume in volumes)
    if not volume_available:
        warnings.append(
            "all volume values are zero; MAVOL, OBV, and relative volume are unavailable"
        )
    mavol5: list[Optional[float]] = (
        sma(volumes, 5) if volume_available else [None] * len(volumes)
    )
    mavol10: list[Optional[float]] = (
        sma(volumes, 10) if volume_available else [None] * len(volumes)
    )
    mavol20: list[Optional[float]] = (
        sma(volumes, 20) if volume_available else [None] * len(volumes)
    )
    obv_raw = on_balance_volume(closes, volumes) if volume_available else None
    obv: list[Optional[float]] = (
        [float(value) for value in obv_raw]
        if obv_raw is not None
        else [None] * len(closes)
    )
    obv_ma20: list[Optional[float]] = (
        sma(obv_raw, 20) if obv_raw is not None else [None] * len(closes)
    )
    relative_volume20 = prior_average_ratio(volumes, 20)

    latest_close = closes[-1]
    latest_atr = atr14[-1]
    prior_high20 = prior_extreme(highs, 20, "high")
    prior_low20 = prior_extreme(lows, 20, "low")

    if ma200[-1] is None:
        long_trend = "insufficient_data"
    elif latest_close > float(ma200[-1]):
        long_trend = "above_ma200"
    else:
        long_trend = "below_ma200"

    if ma50[-1] is None or ma20[-1] is None:
        medium_trend = "insufficient_data"
    elif latest_close > float(ma50[-1]) and float(ma20[-1]) > float(ma50[-1]):
        medium_trend = "bullish_alignment"
    elif latest_close < float(ma50[-1]) and float(ma20[-1]) < float(ma50[-1]):
        medium_trend = "bearish_alignment"
    else:
        medium_trend = "mixed"

    if ma5[-1] is None or ma10[-1] is None or ma20[-1] is None:
        short_trend = "insufficient_data"
    elif (
        latest_close > float(ma5[-1])
        and float(ma5[-1]) > float(ma10[-1])
        and float(ma10[-1]) > float(ma20[-1])
    ):
        short_trend = "bullish_alignment"
    elif (
        latest_close < float(ma5[-1])
        and float(ma5[-1]) < float(ma10[-1])
        and float(ma10[-1]) < float(ma20[-1])
    ):
        short_trend = "bearish_alignment"
    else:
        short_trend = "mixed"

    if rsi14[-1] is None:
        rsi_state = "insufficient_data"
    elif float(rsi14[-1]) >= 70:
        rsi_state = "strong_or_overbought"
    elif float(rsi14[-1]) > 50:
        rsi_state = "positive"
    elif float(rsi14[-1]) <= 30:
        rsi_state = "weak_or_oversold"
    else:
        rsi_state = "negative"

    if macd[-1] is None or macd_signal[-1] is None:
        macd_state = "insufficient_data"
    elif float(macd[-1]) > float(macd_signal[-1]):
        macd_state = "above_signal"
    else:
        macd_state = "below_signal"

    if kdj_k[-1] is None or kdj_d[-1] is None or kdj_j[-1] is None:
        kdj_state = "insufficient_data"
    elif float(kdj_j[-1]) > 100:
        kdj_state = "bullish_but_overextended"
    elif float(kdj_j[-1]) < 0:
        kdj_state = "bearish_but_oversold"
    elif float(kdj_k[-1]) > float(kdj_d[-1]):
        kdj_state = "bullish_alignment"
    else:
        kdj_state = "bearish_alignment"

    if obv[-1] is None or obv_ma20[-1] is None:
        obv_state = "insufficient_data"
    elif float(obv[-1]) > float(obv_ma20[-1]):
        obv_state = "above_ma20"
    elif float(obv[-1]) < float(obv_ma20[-1]):
        obv_state = "below_ma20"
    else:
        obv_state = "at_ma20"

    analysis: dict[str, object] = {
        "metadata": {
            "rows": len(rows),
            "start": rows[0]["date"],
            "end": rows[-1]["date"],
            "indicator_parameters": {
                "ma": "simple moving average: 5, 10, 20, 50, 200",
                "mavol": "simple volume moving average: 5, 10, 20",
                "macd": "EMA 12 minus EMA 26; signal EMA 9; histogram is DIF minus DEA",
                "rsi": "Wilder 14",
                "kdj": "9, 3, 3",
                "bollinger": "SMA 20 plus or minus 2 population standard deviations",
                "atr": "Wilder 14",
            },
            "assumption": (
                "OHLC columns must already share one split-adjusted basis; "
                "the script does not download or independently adjust prices."
            ),
        },
        "data_quality": {
            "volume_available": volume_available,
            "zero_volume_rows": zero_volume_rows,
            "zero_volume_rows_pct": rounded(
                zero_volume_rows / len(rows) * 100.0, 4
            ),
            "possible_corporate_action_or_outlier_dates": possible_outliers,
        },
        "latest": {
            "date": rows[-1]["date"],
            "open": rounded(opens[-1]),
            "high": rounded(highs[-1]),
            "low": rounded(lows[-1]),
            "close": rounded(latest_close),
            "volume": rounded(volumes[-1], 2),
            "mavol5": rounded(mavol5[-1], 2),
            "mavol10": rounded(mavol10[-1], 2),
            "mavol20": rounded(mavol20[-1], 2),
            "ma5": rounded(ma5[-1]),
            "ma10": rounded(ma10[-1]),
            "ma20": rounded(ma20[-1]),
            "ma50": rounded(ma50[-1]),
            "ma200": rounded(ma200[-1]),
            "macd": rounded(macd[-1]),
            "macd_signal": rounded(macd_signal[-1]),
            "macd_histogram": rounded(macd_hist[-1]),
            "rsi14": rounded(rsi14[-1]),
            "kdj_k": rounded(kdj_k[-1]),
            "kdj_d": rounded(kdj_d[-1]),
            "kdj_j": rounded(kdj_j[-1]),
            "atr14": rounded(latest_atr),
            "atr_pct": rounded(
                (float(latest_atr) / latest_close * 100.0)
                if latest_atr is not None and latest_close != 0
                else None
            ),
            "bollinger_middle": rounded(bb_mid[-1]),
            "bollinger_upper": rounded(bb_upper[-1]),
            "bollinger_lower": rounded(bb_lower[-1]),
            "bollinger_bandwidth_pct": rounded(bb_bandwidth[-1]),
            "obv": rounded(obv[-1], 2),
            "obv_ma20": rounded(obv_ma20[-1], 2),
            "relative_volume20": rounded(relative_volume20[-1]),
        },
        "returns_pct": {
            "1d": rounded(pct_change(closes, 1)),
            "5d": rounded(pct_change(closes, 5)),
            "20d": rounded(pct_change(closes, 20)),
            "63d": rounded(pct_change(closes, 63)),
            "126d": rounded(pct_change(closes, 126)),
            "252d": rounded(pct_change(closes, 252)),
        },
        "levels": {
            "low20": rounded(rolling_extreme(lows, 20, "low")),
            "high20": rounded(rolling_extreme(highs, 20, "high")),
            "low60": rounded(rolling_extreme(lows, 60, "low")),
            "high60": rounded(rolling_extreme(highs, 60, "high")),
            "low252": rounded(rolling_extreme(lows, 252, "low")),
            "high252": rounded(rolling_extreme(highs, 252, "high")),
            "prior_high20": rounded(prior_high20),
            "prior_low20": rounded(prior_low20),
        },
        "signals": {
            "long_trend": long_trend,
            "medium_trend": medium_trend,
            "short_trend": short_trend,
            "rsi_state": rsi_state,
            "macd_state": macd_state,
            "kdj_state": kdj_state,
            "obv_state": obv_state,
            "close_above_prior_high20": (
                latest_close > float(prior_high20) if prior_high20 is not None else None
            ),
            "close_below_prior_low20": (
                latest_close < float(prior_low20) if prior_low20 is not None else None
            ),
            "volume_at_least_1_5x_prior20": (
                float(relative_volume20[-1]) >= 1.5
                if relative_volume20[-1] is not None
                else None
            ),
        },
        "warnings": warnings,
    }

    series = {
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "ma50": ma50,
        "ma200": ma200,
        "mavol5": mavol5,
        "mavol10": mavol10,
        "mavol20": mavol20,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_histogram": macd_hist,
        "rsi14": rsi14,
        "kdj_k": kdj_k,
        "kdj_d": kdj_d,
        "kdj_j": kdj_j,
        "atr14": atr14,
        "bollinger_middle": bb_mid,
        "bollinger_upper": bb_upper,
        "bollinger_lower": bb_lower,
        "bollinger_bandwidth_pct": bb_bandwidth,
        "obv": obv,
        "obv_ma20": obv_ma20,
        "relative_volume20": relative_volume20,
    }
    return analysis, series


def write_enriched_csv(
    path: Path,
    rows: list[dict[str, float | str]],
    series: dict[str, list[Optional[float]]],
) -> None:
    fieldnames = ["date", "open", "high", "low", "close", "volume", *series.keys()]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, row in enumerate(rows):
            output_row = dict(row)
            for name, values in series.items():
                output_row[name] = "" if values[index] is None else rounded(values[index])
            writer.writerow(output_row)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate technical indicators from a local OHLCV CSV."
    )
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument(
        "--output", default="-", help="Output JSON path, or - for stdout"
    )
    parser.add_argument(
        "--enriched-output", help="Optional CSV path containing indicator series"
    )
    parser.add_argument(
        "--as-of",
        help="Optional ISO-8601 analysis timestamp used to check bar freshness",
    )
    args = parser.parse_args()

    try:
        rows, warnings = read_ohlcv(Path(args.input))
        analysis, series = build_analysis(rows, warnings)
        if args.as_of:
            as_of = parse_datetime(args.as_of)
            latest_bar = parse_datetime(str(analysis["metadata"]["end"]))
            age_days = (as_of.date() - latest_bar.date()).days
            if age_days < 0:
                raise ValueError("latest bar is later than --as-of")
            analysis["metadata"]["analysis_as_of"] = as_of.isoformat()
            analysis["metadata"]["latest_bar_age_calendar_days"] = age_days
            if age_days > 7:
                analysis["warnings"].append(
                    "latest completed bar is more than 7 calendar days old"
                )
            elif age_days > 4:
                analysis["warnings"].append(
                    "latest bar may be stale; verify holidays, suspension, and the latest completed session"
                )
        payload = json.dumps(analysis, ensure_ascii=False, indent=2)
        if args.output == "-":
            print(payload)
        else:
            Path(args.output).write_text(payload + "\n", encoding="utf-8")
        if args.enriched_output:
            write_enriched_csv(Path(args.enriched_output), rows, series)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
