#!/usr/bin/env python3
"""Validate and analyze Level 1 / Level 2 equity market-depth snapshots."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


US_ACTIVE_STATES = {"regular", "pre_market", "post_market"}
US_VALID_STATES = US_ACTIVE_STATES | {"closed", "halted", "unknown"}
HK_ACTIVE_STATES = {"morning", "extended_morning", "afternoon"}
HK_VALID_STATES = HK_ACTIVE_STATES | {
    "pre_opening",
    "midday_break",
    "closing_auction",
    "closed",
    "halted",
    "unknown",
}
ACTIVE_STATES = US_ACTIVE_STATES | HK_ACTIVE_STATES
VALID_SCOPES = {"nbbo", "exchange_book", "aggregated", "single_venue", "unknown"}
EXECUTION_GRADE_SOURCE_KINDS = {"broker_exchange", "professional_vendor"}
MARKET_ALIASES = {
    "US": "US",
    "USA": "US",
    "NYSE": "US",
    "NASDAQ": "US",
    "HK": "HK",
    "HKG": "HK",
    "HKEX": "HK",
    "SEHK": "HK",
}
MARKET_STATE_ALIASES = {
    "open": "regular",
    "premarket": "pre_market",
    "pre-market": "pre_market",
    "postmarket": "post_market",
    "post-market": "post_market",
    "afterhours": "post_market",
    "after_hours": "post_market",
    "preopen": "pre_opening",
    "pre-open": "pre_opening",
    "lunch": "midday_break",
    "midday": "midday_break",
    "am": "morning",
    "pm": "afternoon",
    "cas": "closing_auction",
}
QUOTE_SCOPE_ALIASES = {
    "sip": "nbbo",
    "consolidated": "aggregated",
    "consolidated_book": "aggregated",
    "venue": "single_venue",
    "hkex": "exchange_book",
    "sehk": "exchange_book",
    "central_order_book": "exchange_book",
}
SYNTHETIC_MARKERS = {
    "synthetic",
    "simulated",
    "simulation",
    "sample",
    "demo",
    "mock",
    "random",
    "fabricated",
    "placeholder",
    "init",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


def parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO 8601: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone offset")
    return parsed


def finite_number(value: Any, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be numeric")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be finite")
    if positive and numeric <= 0:
        raise ValueError(f"{field} must be greater than zero")
    return numeric


def optional_number(value: Any, field: str) -> float | None:
    if value is None:
        return None
    return finite_number(value, field)


def normalize_market(value: Any) -> str:
    raw = str(value or "US").strip().upper()
    market = MARKET_ALIASES.get(raw)
    if market is None:
        raise ValueError("market must identify US or HK")
    return market


def rounded(value: float | None, digits: int = 6) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def imbalance(bid_value: float, ask_value: float) -> float | None:
    total = bid_value + ask_value
    if total <= 0:
        return None
    return (bid_value - ask_value) / total


def normalize_side_levels(
    raw_levels: Any,
    side: str,
    size_multiplier: float,
    warnings: list[str],
) -> list[dict[str, Any]]:
    if raw_levels is None:
        return []
    if not isinstance(raw_levels, list):
        raise ValueError(f"{side}s must be an array")
    if len(raw_levels) > 5000:
        raise ValueError(f"{side}s contains more than 5000 rows")

    aggregated: dict[float, dict[str, Any]] = {}
    original_prices: list[float] = []
    duplicate_prices: set[float] = set()
    for index, raw in enumerate(raw_levels, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"{side}s[{index}] must be an object")
        price = finite_number(raw.get("price"), f"{side}s[{index}].price", positive=True)
        size = finite_number(raw.get("size"), f"{side}s[{index}].size", positive=True)
        size_shares = size * size_multiplier
        order_count = raw.get("order_count")
        if order_count is not None:
            order_count = int(
                finite_number(order_count, f"{side}s[{index}].order_count", positive=True)
            )
        venue = raw.get("venue")
        if venue is not None and not isinstance(venue, str):
            raise ValueError(f"{side}s[{index}].venue must be text or null")
        original_prices.append(price)
        if price in aggregated:
            duplicate_prices.add(price)
            aggregated[price]["size_shares"] += size_shares
            if order_count is not None:
                aggregated[price]["order_count"] = (
                    aggregated[price].get("order_count") or 0
                ) + order_count
            if venue:
                aggregated[price]["venues"].add(venue)
        else:
            aggregated[price] = {
                "price": price,
                "size_shares": size_shares,
                "order_count": order_count,
                "venues": {venue} if venue else set(),
            }

    reverse = side == "bid"
    expected_prices = sorted(original_prices, reverse=reverse)
    if original_prices != expected_prices:
        warnings.append(f"{side} levels were not sorted; normalized by price")
    if duplicate_prices:
        warnings.append(
            f"{side} levels contained duplicate prices; aggregated {len(duplicate_prices)} prices"
        )

    levels: list[dict[str, Any]] = []
    for price in sorted(aggregated, reverse=reverse):
        row = aggregated[price]
        levels.append(
            {
                "price": price,
                "size_shares": row["size_shares"],
                "order_count": row["order_count"],
                "venues": sorted(row["venues"]),
            }
        )
    return levels


def top_level_fallback(payload: dict[str, Any]) -> tuple[Any, Any]:
    bids = payload.get("bids")
    asks = payload.get("asks")
    if bids is None and payload.get("bid") is not None:
        bids = [{"price": payload.get("bid"), "size": payload.get("bid_size")}]
    if asks is None and payload.get("ask") is not None:
        asks = [{"price": payload.get("ask"), "size": payload.get("ask_size")}]
    return bids, asks


def level_metrics(
    bids: list[dict[str, Any]], asks: list[dict[str, Any]], levels: int
) -> dict[str, Any]:
    bid_slice = bids[:levels]
    ask_slice = asks[:levels]
    bid_size = sum(float(row["size_shares"]) for row in bid_slice)
    ask_size = sum(float(row["size_shares"]) for row in ask_slice)
    bid_notional = sum(float(row["price"]) * float(row["size_shares"]) for row in bid_slice)
    ask_notional = sum(float(row["price"]) * float(row["size_shares"]) for row in ask_slice)

    weighted_bid = sum(
        float(row["size_shares"]) / index for index, row in enumerate(bid_slice, start=1)
    )
    weighted_ask = sum(
        float(row["size_shares"]) / index for index, row in enumerate(ask_slice, start=1)
    )
    return {
        "requested_levels": levels,
        "bid_levels_used": len(bid_slice),
        "ask_levels_used": len(ask_slice),
        "bid_size_shares": rounded(bid_size, 3),
        "ask_size_shares": rounded(ask_size, 3),
        "size_imbalance": rounded(imbalance(bid_size, ask_size)),
        "distance_weighted_imbalance": rounded(imbalance(weighted_bid, weighted_ask)),
        "bid_notional": rounded(bid_notional, 2),
        "ask_notional": rounded(ask_notional, 2),
    }


def band_metrics(
    bids: list[dict[str, Any]], asks: list[dict[str, Any]], mid: float, bps: int
) -> dict[str, Any]:
    lower = mid * (1 - bps / 10000)
    upper = mid * (1 + bps / 10000)
    bid_slice = [row for row in bids if float(row["price"]) >= lower]
    ask_slice = [row for row in asks if float(row["price"]) <= upper]
    bid_size = sum(float(row["size_shares"]) for row in bid_slice)
    ask_size = sum(float(row["size_shares"]) for row in ask_slice)
    return {
        "band_bps": bps,
        "bid_levels": len(bid_slice),
        "ask_levels": len(ask_slice),
        "bid_size_shares": rounded(bid_size, 3),
        "ask_size_shares": rounded(ask_size, 3),
        "size_imbalance": rounded(imbalance(bid_size, ask_size)),
        "bid_notional": rounded(
            sum(float(row["price"]) * float(row["size_shares"]) for row in bid_slice), 2
        ),
        "ask_notional": rounded(
            sum(float(row["price"]) * float(row["size_shares"]) for row in ask_slice), 2
        ),
    }


def normalize_trades(
    raw_trades: Any, size_multiplier: float, warnings: list[str]
) -> dict[str, Any] | None:
    if raw_trades is None:
        return None
    if not isinstance(raw_trades, list):
        raise ValueError("trades must be an array")

    buy_volume = 0.0
    sell_volume = 0.0
    unknown_volume = 0.0
    buy_notional = 0.0
    sell_notional = 0.0
    unknown_notional = 0.0
    for index, raw in enumerate(raw_trades, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"trades[{index}] must be an object")
        price = finite_number(raw.get("price"), f"trades[{index}].price", positive=True)
        size = finite_number(raw.get("size"), f"trades[{index}].size", positive=True)
        volume = size * size_multiplier
        side = str(raw.get("aggressor_side", "unknown")).strip().lower()
        if side in {"buy", "buyer", "at_ask"}:
            buy_volume += volume
            buy_notional += price * volume
        elif side in {"sell", "seller", "at_bid"}:
            sell_volume += volume
            sell_notional += price * volume
        else:
            unknown_volume += volume
            unknown_notional += price * volume

    classified = buy_volume + sell_volume
    total = classified + unknown_volume
    if unknown_volume:
        warnings.append(
            "some trades lack a reliable aggressor side; excluded from buy/sell imbalance"
        )
    return {
        "trade_count": len(raw_trades),
        "total_volume_shares": rounded(total, 3),
        "classified_volume_shares": rounded(classified, 3),
        "classification_coverage_pct": rounded(100 * classified / total, 3) if total else None,
        "aggressive_buy_volume_shares": rounded(buy_volume, 3),
        "aggressive_sell_volume_shares": rounded(sell_volume, 3),
        "unknown_volume_shares": rounded(unknown_volume, 3),
        "net_aggressive_delta_shares": rounded(buy_volume - sell_volume, 3),
        "trade_imbalance": rounded(imbalance(buy_volume, sell_volume)),
        "aggressive_buy_notional": rounded(buy_notional, 2),
        "aggressive_sell_notional": rounded(sell_notional, 2),
        "unknown_notional": rounded(unknown_notional, 2),
    }


def sweep_fill(
    levels: list[dict[str, Any]], shares: float, mid: float, side: str
) -> dict[str, Any]:
    remaining = shares
    cost = 0.0
    filled = 0.0
    worst_price: float | None = None
    for row in levels:
        available = float(row["size_shares"])
        take = min(remaining, available)
        if take <= 0:
            continue
        price = float(row["price"])
        cost += take * price
        filled += take
        remaining -= take
        worst_price = price
        if remaining <= 1e-12:
            break
    average = cost / filled if filled else None
    if average is None:
        slippage_bps = None
    elif side == "buy":
        slippage_bps = (average - mid) / mid * 10000
    else:
        slippage_bps = (mid - average) / mid * 10000
    return {
        "side": side,
        "requested_shares": rounded(shares, 3),
        "filled_shares": rounded(filled, 3),
        "fill_pct": rounded(100 * filled / shares, 3),
        "average_fill_price": rounded(average),
        "worst_displayed_price": rounded(worst_price),
        "slippage_vs_mid_bps": rounded(slippage_bps),
        "displayed_depth_sufficient": remaining <= 1e-12,
    }


def sweep_estimates(
    payload: dict[str, Any], bids: list[dict[str, Any]], asks: list[dict[str, Any]], mid: float
) -> list[dict[str, Any]]:
    raw_sizes = payload.get("sweep_sizes_shares")
    if raw_sizes is None:
        return []
    if not isinstance(raw_sizes, list) or len(raw_sizes) > 10:
        raise ValueError("sweep_sizes_shares must be an array of at most 10 values")
    results: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_sizes, start=1):
        shares = finite_number(raw, f"sweep_sizes_shares[{index}]", positive=True)
        results.append(sweep_fill(asks, shares, mid, "buy"))
        results.append(sweep_fill(bids, shares, mid, "sell"))
    return results


def pressure_summary(
    by_level: dict[str, dict[str, Any]], trade_flow: dict[str, Any] | None
) -> dict[str, Any]:
    values: list[tuple[float, float]] = []
    for key, weight in (("1", 0.2), ("5", 0.35), ("10", 0.45)):
        metric = by_level.get(key)
        if metric and metric.get("distance_weighted_imbalance") is not None:
            values.append((float(metric["distance_weighted_imbalance"]), weight))
    if not values:
        score = None
    else:
        total_weight = sum(weight for _, weight in values)
        score = sum(value * weight for value, weight in values) / total_weight

    trade_value = None
    if trade_flow and trade_flow.get("classification_coverage_pct", 0) >= 70:
        trade_value = trade_flow.get("trade_imbalance")

    combined = score
    if score is not None and trade_value is not None:
        combined = 0.65 * score + 0.35 * float(trade_value)

    if combined is None:
        label = "insufficient_data"
    elif combined >= 0.2:
        label = "bid_side_tactical_evidence_heavier"
    elif combined <= -0.2:
        label = "ask_side_tactical_evidence_heavier"
    else:
        label = "balanced_or_mixed"

    max_levels = max(
        (
            min(int(metric["bid_levels_used"]), int(metric["ask_levels_used"]))
            for metric in by_level.values()
        ),
        default=0,
    )
    evidence_strength = "low"
    if max_levels >= 10 and trade_value is not None:
        evidence_strength = "moderate"
    elif max_levels >= 5:
        evidence_strength = "low_to_moderate"

    return {
        "displayed_book_pressure_score": rounded(score),
        "classified_trade_flow_score": rounded(float(trade_value)) if trade_value is not None else None,
        "combined_tactical_score": rounded(combined),
        "label": label,
        "evidence_strength": evidence_strength,
        "use_limit": (
            "Snapshot evidence only. Displayed orders can be cancelled, hidden liquidity and "
            "off-exchange trades are not fully represented, and the score is not a standalone "
            "directional or buy/sell signal."
        ),
    }


def freshness_status(
    market_state: str,
    age_seconds: float,
    is_delayed: bool,
    delay_seconds: float | None,
) -> tuple[bool, int | None, list[str]]:
    warnings: list[str] = []
    threshold = {
        "regular": 60,
        "pre_market": 300,
        "post_market": 300,
        "morning": 60,
        "extended_morning": 60,
        "afternoon": 60,
    }.get(market_state)
    if age_seconds < -5:
        warnings.append("captured_at is later than analysis_timestamp; verify clock synchronization")
    effective_age = max(age_seconds, delay_seconds or 0)
    fresh = threshold is not None and effective_age <= threshold and age_seconds >= -5
    if market_state not in ACTIVE_STATES:
        warnings.append("market is not active; the book is historical and not execution-timing data")
    if is_delayed:
        warnings.append("quote is marked delayed; do not use it for current execution timing")
    if threshold is not None and effective_age > threshold:
        warnings.append(
            f"market-depth snapshot age/delay is {round(effective_age, 1)} seconds, "
            f"above the {threshold}-second active-session limit"
        )
    return fresh and not is_delayed, threshold, warnings


def detect_synthetic(payload: dict[str, Any], source: str) -> bool:
    if payload.get("is_synthetic") is True:
        return True
    source_kind = str(payload.get("source_kind", "")).lower()
    combined = f"{source.lower()} {source_kind}"
    tokens = set(re.findall(r"[a-z0-9]+", combined))
    return any(marker in tokens for marker in SYNTHETIC_MARKERS)


def chart_depth(
    output_path: Path,
    symbol: str,
    bids: list[dict[str, Any]],
    asks: list[dict[str, Any]],
    captured_at: str,
    source: str,
    max_levels: int,
) -> None:
    import os
    import tempfile

    matplotlib_config = Path(tempfile.gettempdir()) / "investment-analysis-matplotlib"
    matplotlib_config.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_config))
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ValueError("matplotlib is required for --chart-output") from exc

    bid_rows = bids[:max_levels]
    ask_rows = asks[:max_levels]
    fig, axes = plt.subplots(1, 2, figsize=(13, 7))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.86, wspace=0.26)

    prices = [float(row["price"]) for row in reversed(bid_rows)] + [
        float(row["price"]) for row in ask_rows
    ]
    sizes = [-float(row["size_shares"]) for row in reversed(bid_rows)] + [
        float(row["size_shares"]) for row in ask_rows
    ]
    colors = ["#178a55"] * len(bid_rows) + ["#c53c3c"] * len(ask_rows)
    labels = [f"{price:.4f}" for price in prices]
    positions = list(range(len(prices)))
    axes[0].barh(positions, sizes, color=colors, alpha=0.85)
    axes[0].set_yticks(positions, labels)
    axes[0].axvline(0, color="#555555", linewidth=0.8)
    axes[0].set_xlabel("Displayed size (shares): bid left / ask right")
    axes[0].set_ylabel("Price")
    axes[0].set_title("Displayed depth by price level")
    axes[0].grid(axis="x", alpha=0.2)

    bid_cumulative: list[float] = []
    running = 0.0
    for row in bid_rows:
        running += float(row["size_shares"])
        bid_cumulative.append(running)
    ask_cumulative: list[float] = []
    running = 0.0
    for row in ask_rows:
        running += float(row["size_shares"])
        ask_cumulative.append(running)
    axes[1].step(
        [float(row["price"]) for row in bid_rows],
        bid_cumulative,
        where="post",
        color="#178a55",
        label="Bid cumulative",
    )
    axes[1].step(
        [float(row["price"]) for row in ask_rows],
        ask_cumulative,
        where="post",
        color="#c53c3c",
        label="Ask cumulative",
    )
    axes[1].set_xlabel("Price")
    axes[1].set_ylabel("Cumulative displayed size (shares)")
    axes[1].set_title("Cumulative displayed depth")
    axes[1].grid(alpha=0.2)
    axes[1].legend()

    fig.suptitle(
        f"{symbol} market depth snapshot | {captured_at}",
        fontsize=15,
        fontweight="bold",
        y=0.965,
    )
    fig.text(
        0.08,
        0.035,
        f"Source: {source} | Snapshot only; displayed orders may be cancelled and hidden liquidity is excluded.",
        fontsize=8.5,
        color="#555555",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def analyze(payload: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    errors: list[str] = []

    symbol = str(payload.get("symbol", "")).strip().upper()
    if not symbol:
        raise ValueError("symbol is required")
    source = str(payload.get("source", "")).strip()
    if not source:
        raise ValueError("source is required")
    source_kind = str(payload.get("source_kind", "unknown")).strip().lower() or "unknown"
    market_hint = payload.get("market")
    if market_hint is None:
        exchange_hint = str(payload.get("exchange", "")).strip().upper()
        market_hint = exchange_hint if exchange_hint in MARKET_ALIASES else "US"
    market = normalize_market(market_hint)
    currency = str(payload.get("currency", "")).strip().upper()
    if not currency:
        raise ValueError("currency is required")
    market_state = str(payload.get("market_state", "unknown")).strip().lower()
    market_state = MARKET_STATE_ALIASES.get(market_state, market_state)
    valid_states = HK_VALID_STATES if market == "HK" else US_VALID_STATES
    active_states = HK_ACTIVE_STATES if market == "HK" else US_ACTIVE_STATES
    if market_state not in valid_states:
        raise ValueError("market_state is invalid for the selected US or HK market")
    quote_scope = str(payload.get("quote_scope", "unknown")).strip().lower()
    quote_scope = QUOTE_SCOPE_ALIASES.get(quote_scope, quote_scope)
    if quote_scope not in VALID_SCOPES:
        raise ValueError(
            "quote_scope must be nbbo, exchange_book, aggregated, single_venue, or unknown"
        )
    allowed_scopes = (
        {"exchange_book", "aggregated", "single_venue", "unknown"}
        if market == "HK"
        else {"nbbo", "aggregated", "single_venue", "unknown"}
    )
    if quote_scope not in allowed_scopes:
        raise ValueError("quote_scope is not valid for the selected US or HK market")

    captured = parse_timestamp(payload.get("captured_at"), "captured_at")
    analysis_time = parse_timestamp(payload.get("analysis_timestamp"), "analysis_timestamp")
    age_seconds = (analysis_time - captured).total_seconds()
    is_delayed = bool(payload.get("is_delayed", False))
    delay_seconds = optional_number(payload.get("delay_seconds"), "delay_seconds")
    if delay_seconds is not None and delay_seconds < 0:
        raise ValueError("delay_seconds cannot be negative")

    size_unit = str(payload.get("size_unit", "shares")).strip().lower()
    raw_round_lot_size = payload.get("round_lot_size")
    round_lot_size = (
        finite_number(raw_round_lot_size, "round_lot_size", positive=True)
        if raw_round_lot_size is not None
        else None
    )
    if (
        market == "HK"
        and round_lot_size is not None
        and not math.isclose(round_lot_size, round(round_lot_size))
    ):
        raise ValueError("HK round_lot_size must be a positive whole number of shares")
    if size_unit in {"shares", "share"}:
        size_multiplier = 1.0
        size_unit = "shares"
    elif size_unit in {"round_lots", "round_lot", "lots", "lot"}:
        if round_lot_size is None:
            raise ValueError(
                "round_lot_size is required when size_unit is round_lots"
            )
        size_multiplier = round_lot_size
        size_unit = "round_lots"
    else:
        raise ValueError("size_unit must be shares or round_lots")
    if "size_unit" not in payload:
        warnings.append("size_unit was not supplied; assumed shares")
    if market == "HK" and round_lot_size is None:
        warnings.append(
            "HK round_lot_size was not supplied; depth cannot be expressed in current board lots"
        )

    raw_bids, raw_asks = top_level_fallback(payload)
    bids = normalize_side_levels(raw_bids, "bid", size_multiplier, warnings)
    asks = normalize_side_levels(raw_asks, "ask", size_multiplier, warnings)
    if not bids or not asks:
        errors.append("both bid and ask levels with positive price and size are required")

    synthetic = detect_synthetic(payload, source)
    if synthetic:
        errors.append("synthetic, demo, random, or placeholder market-depth data is prohibited")

    best_bid = bids[0] if bids else None
    best_ask = asks[0] if asks else None
    mid = None
    spread = None
    spread_bps = None
    microprice = None
    market_quality = "unavailable"
    if best_bid and best_ask:
        bid_price = float(best_bid["price"])
        ask_price = float(best_ask["price"])
        if bid_price > ask_price:
            errors.append("crossed book: best bid is above best ask")
            market_quality = "crossed"
        else:
            mid = (bid_price + ask_price) / 2
            spread = ask_price - bid_price
            spread_bps = spread / mid * 10000 if mid else None
            market_quality = "locked" if bid_price == ask_price else "normal"
            if market_quality == "locked":
                warnings.append("locked market snapshot; verify venue aggregation and timestamps")
            bid_size = float(best_bid["size_shares"])
            ask_size = float(best_ask["size_shares"])
            microprice = (ask_price * bid_size + bid_price * ask_size) / (bid_size + ask_size)

    fresh_for_session, freshness_limit, freshness_warnings = freshness_status(
        market_state, age_seconds, is_delayed, delay_seconds
    )
    warnings.extend(freshness_warnings)
    if quote_scope == "single_venue" and market == "US":
        warnings.append("single-venue book is not the consolidated US market and may omit better prices or depth")
    elif quote_scope == "single_venue":
        warnings.append(
            "single-venue or broker-limited scope may omit HKEX market depth"
        )
    elif quote_scope == "unknown":
        warnings.append(
            "quote scope is unknown; do not describe the book as NBBO, HKEX exchange book, or full-market depth"
        )
    if market == "HK" and market_state in {
        "pre_opening",
        "midday_break",
        "closing_auction",
    }:
        warnings.append(
            "HK auction or midday state is not eligible for ordinary continuous-book execution timing"
        )
    source_execution_eligible = source_kind in EXECUTION_GRADE_SOURCE_KINDS
    if not source_execution_eligible and not synthetic:
        warnings.append(
            "source_kind is not broker_exchange or professional_vendor; snapshot is not execution-grade"
        )

    by_level: dict[str, dict[str, Any]] = {}
    if bids and asks:
        for count in (1, 5, 10):
            by_level[str(count)] = level_metrics(bids, asks, count)
    within_bps: dict[str, dict[str, Any]] = {}
    if mid is not None:
        for bps in (5, 10, 25):
            within_bps[str(bps)] = band_metrics(bids, asks, mid, bps)

    trade_flow = normalize_trades(payload.get("trades"), size_multiplier, warnings)
    sweeps = sweep_estimates(payload, bids, asks, mid) if mid is not None else []
    pressure = pressure_summary(by_level, trade_flow)

    max_complete_levels = min(len(bids), len(asks))
    quote_level = "level_2" if max_complete_levels >= 2 else "level_1"
    structure_valid = not errors and market_quality in {"normal", "locked"}
    scope_eligible = quote_scope in (
        {"exchange_book", "aggregated"}
        if market == "HK"
        else {"nbbo", "aggregated"}
    )
    execution_timing_eligible = (
        structure_valid
        and fresh_for_session
        and scope_eligible
        and source_execution_eligible
        and market_state in active_states
        and not synthetic
    )
    if not structure_valid:
        status = "unusable"
    elif execution_timing_eligible:
        status = "usable_current_snapshot"
    elif is_delayed or not fresh_for_session or market_state not in active_states:
        status = "usable_historical_or_delayed_snapshot"
    else:
        status = "usable_scope_limited_snapshot"

    if spread_bps is None:
        spread_class = "unavailable"
    elif spread_bps <= 5:
        spread_class = "tight"
    elif spread_bps <= 20:
        spread_class = "moderate"
    else:
        spread_class = "wide"

    return {
        "symbol": symbol,
        "snapshot": {
            "market": market,
            "captured_at": captured.isoformat(),
            "analysis_timestamp": analysis_time.isoformat(),
            "age_seconds": rounded(age_seconds, 3),
            "market_state": market_state,
            "source": source,
            "source_kind": source_kind,
            "quote_scope": quote_scope,
            "is_delayed": is_delayed,
            "delay_seconds": rounded(delay_seconds, 3),
            "exchange": payload.get("exchange"),
            "currency": currency,
            "input_size_unit": size_unit,
            "round_lot_size": rounded(round_lot_size, 3),
        },
        "data_quality": {
            "status": status,
            "quote_level": quote_level,
            "bid_levels": len(bids),
            "ask_levels": len(asks),
            "market_quality": market_quality,
            "freshness_limit_seconds": freshness_limit,
            "fresh_for_active_session": fresh_for_session,
            "scope_eligible_for_marketwide_timing": scope_eligible,
            "source_eligible_for_execution": source_execution_eligible,
            "execution_timing_eligible": execution_timing_eligible,
            "synthetic_data_detected": synthetic,
            "errors": errors,
            "warnings": warnings,
        },
        "top_of_book": {
            "best_bid": rounded(float(best_bid["price"])) if best_bid else None,
            "best_bid_size_shares": rounded(float(best_bid["size_shares"]), 3) if best_bid else None,
            "best_ask": rounded(float(best_ask["price"])) if best_ask else None,
            "best_ask_size_shares": rounded(float(best_ask["size_shares"]), 3) if best_ask else None,
            "mid": rounded(mid),
            "microprice": rounded(microprice),
            "spread": rounded(spread),
            "spread_bps": rounded(spread_bps),
            "spread_class": spread_class,
            "level_1_size_imbalance": rounded(
                imbalance(
                    float(best_bid["size_shares"]) if best_bid else 0,
                    float(best_ask["size_shares"]) if best_ask else 0,
                )
            ),
        },
        "depth": {
            "by_levels": by_level,
            "within_mid_bps": within_bps,
        },
        "trade_flow": trade_flow,
        "sweep_estimates": sweeps,
        "interpretation": pressure,
        "normalized_levels": {
            "bids": [
                {
                    "price": rounded(float(row["price"])),
                    "size_shares": rounded(float(row["size_shares"]), 3),
                    "order_count": row["order_count"],
                    "venues": row["venues"],
                }
                for row in bids
            ],
            "asks": [
                {
                    "price": rounded(float(row["price"])),
                    "size_shares": rounded(float(row["size_shares"]), 3),
                    "order_count": row["order_count"],
                    "venues": row["venues"],
                }
                for row in asks
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and analyze Level 1 / Level 2 equity market-depth snapshots."
    )
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", default="-", help="Output JSON path, or -")
    parser.add_argument("--chart-output", help="Optional PNG market-depth chart path")
    parser.add_argument("--chart-levels", type=int, default=10, help="Levels per side in chart")
    args = parser.parse_args()

    try:
        if args.chart_levels < 1 or args.chart_levels > 50:
            raise ValueError("chart-levels must be between 1 and 50")
        payload = load_json(Path(args.input))
        result = analyze(payload)
        if args.chart_output and result["data_quality"]["status"] != "unusable":
            chart_depth(
                Path(args.chart_output),
                result["symbol"],
                result["normalized_levels"]["bids"],
                result["normalized_levels"]["asks"],
                result["snapshot"]["captured_at"],
                result["snapshot"]["source"],
                args.chart_levels,
            )
            result["chart_output"] = str(Path(args.chart_output))
        text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
        if args.output == "-":
            print(text)
        else:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text + "\n", encoding="utf-8")
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
