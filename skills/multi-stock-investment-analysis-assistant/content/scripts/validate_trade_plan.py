#!/usr/bin/env python3
"""Validate a staged equity trade plan for internal consistency and risk gates."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


US_ACTIVE_MARKET_STATES = {"pre_market", "regular", "post_market"}
US_VALID_MARKET_STATES = US_ACTIVE_MARKET_STATES | {"closed", "halted"}
HK_ACTIVE_MARKET_STATES = {"morning", "extended_morning", "afternoon"}
HK_VALID_MARKET_STATES = HK_ACTIVE_MARKET_STATES | {
    "pre_opening",
    "midday_break",
    "closing_auction",
    "closed",
    "halted",
}
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


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("input JSON must be an object")
    return payload


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


def optional_number(value: Any, name: str) -> float | None:
    return None if value is None else finite_number(value, name)


def normalize_market(value: Any) -> str:
    raw = str(value or "US").strip().upper()
    market = MARKET_ALIASES.get(raw)
    if market is None:
        raise ValueError("market must identify US or HK")
    return market


def non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def parse_timestamp(value: Any, name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty ISO-8601 timestamp")
    raw = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc


def price_is_above(left: float, right: float, side: str) -> bool:
    return left > right if side == "long" else left < right


def parse_barriers(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("known_barriers must be an array")
    barriers: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if isinstance(item, dict):
            price = finite_number(item.get("price"), f"known_barriers[{index}].price")
            label = str(item.get("label", f"barrier_{index + 1}"))
        else:
            price = finite_number(item, f"known_barriers[{index}]")
            label = f"barrier_{index + 1}"
        if price <= 0:
            raise ValueError(f"known_barriers[{index}] price must be positive")
        barriers.append({"price": price, "label": label})
    return barriers


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate staged entries, exits, data timing, and reward/risk gates."
    )
    parser.add_argument("--input", required=True, help="Input JSON path")
    parser.add_argument("--output", default="-", help="Output JSON path, or -")
    args = parser.parse_args()

    try:
        payload = load_json(Path(args.input))
        side = str(payload.get("side", "long")).lower()
        if side not in {"long", "short"}:
            raise ValueError("side must be long or short")

        data_context_raw = payload.get("data_context")
        market_context_raw = payload.get("market_context")
        market_hint = payload.get("market")
        if market_hint is None and isinstance(data_context_raw, dict):
            market_hint = data_context_raw.get("market")
        if market_hint is None and isinstance(market_context_raw, dict):
            market_hint = market_context_raw.get("market")
            if market_hint is None:
                exchange_hint = str(
                    market_context_raw.get("exchange", "")
                ).strip().upper()
                market_hint = (
                    exchange_hint if exchange_hint in MARKET_ALIASES else None
                )
        market = normalize_market(market_hint)

        errors: list[str] = []
        warnings: list[str] = []
        gates: dict[str, bool | None] = {
            "data": None,
            "structure": None,
            "risk": None,
            "reward": None,
            "event": None,
            "liquidity": None,
            "time": None,
            "consistency": None,
        }
        if market == "HK":
            gates["market_rules"] = None

        data_context = data_context_raw
        data_checks: dict[str, Any] = {}
        analysis_time: datetime | None = None
        if data_context is not None:
            if not isinstance(data_context, dict):
                raise ValueError("data_context must be an object")
            analysis_time = parse_timestamp(
                data_context.get("analysis_timestamp"),
                "data_context.analysis_timestamp",
            )
            quote_time = parse_timestamp(
                data_context.get("quote_timestamp"),
                "data_context.quote_timestamp",
            )
            indicator_time = parse_timestamp(
                data_context.get("indicator_date"),
                "data_context.indicator_date",
            )
            data_ok = True
            context_market = normalize_market(data_context.get("market", market))
            if context_market != market:
                errors.append("data_context.market conflicts with the plan market")
                data_ok = False
            market_state = str(data_context.get("market_state", "")).lower()
            market_state = MARKET_STATE_ALIASES.get(market_state, market_state)
            indicator_basis = str(data_context.get("indicator_basis", "")).lower()
            valid_states = (
                HK_VALID_MARKET_STATES if market == "HK" else US_VALID_MARKET_STATES
            )
            active_states = (
                HK_ACTIVE_MARKET_STATES if market == "HK" else US_ACTIVE_MARKET_STATES
            )
            if market_state not in valid_states:
                errors.append(
                    "market_state is invalid for the selected US or HK market"
                )
                data_ok = False
            if analysis_time.tzinfo is None or quote_time.tzinfo is None:
                errors.append("analysis_timestamp and quote_timestamp must include time zones")
                data_ok = False
                quote_age_minutes = None
            else:
                quote_age_minutes = (
                    analysis_time - quote_time
                ).total_seconds() / 60.0
            indicator_age_days = (analysis_time.date() - indicator_time.date()).days
            data_checks = {
                "market": market,
                "market_state": market_state,
                "indicator_basis": indicator_basis,
                "quote_age_minutes": (
                    round(quote_age_minutes, 2)
                    if quote_age_minutes is not None
                    else None
                ),
                "indicator_age_calendar_days": indicator_age_days,
                "quote_is_delayed": bool(data_context.get("quote_is_delayed", False)),
            }
            if quote_age_minutes is not None and quote_age_minutes < -1:
                errors.append("quote_timestamp is later than analysis_timestamp")
                data_ok = False
            if (
                quote_age_minutes is not None
                and market_state in active_states
                and quote_age_minutes > 60
            ):
                errors.append("active-session quote is more than 60 minutes old")
                data_ok = False
            elif quote_age_minutes is not None and quote_age_minutes > 30:
                warnings.append("quote is more than 30 minutes old; refresh before execution")
            if indicator_age_days < 0:
                errors.append("indicator_date is later than analysis_timestamp")
                data_ok = False
            elif (
                indicator_age_days == 0
                and market_state
                in (
                    {"pre_market", "regular", "halted"}
                    if market == "US"
                    else {
                        "pre_opening",
                        "morning",
                        "extended_morning",
                        "midday_break",
                        "afternoon",
                        "closing_auction",
                        "halted",
                    }
                )
            ):
                errors.append(
                    "indicator_date is the active or incomplete market date; use the latest completed session"
                )
                data_ok = False
            elif indicator_age_days > 7:
                errors.append("completed-session indicator data is more than 7 calendar days old")
                data_ok = False
            elif indicator_age_days > 4:
                warnings.append("indicator data may be stale; verify the latest completed session")
            if indicator_basis != "completed_session":
                errors.append("indicator_basis must be completed_session for a final trade plan")
                data_ok = False
            gates["data"] = data_ok

        entries_raw = payload.get("entries")
        if not isinstance(entries_raw, list) or not entries_raw:
            raise ValueError("entries must be a non-empty array")
        entries: list[dict[str, Any]] = []
        total_weight = 0.0
        timed_entries = True
        entry_triggers_ok = True
        for index, raw in enumerate(entries_raw):
            if not isinstance(raw, dict):
                raise ValueError(f"entries[{index}] must be an object")
            price = finite_number(raw.get("price"), f"entries[{index}].price")
            weight = finite_number(
                raw.get("weight_pct"), f"entries[{index}].weight_pct"
            )
            trigger = raw.get("trigger")
            execution_window = raw.get("execution_window")
            if price <= 0 or weight <= 0:
                raise ValueError(f"entries[{index}] price and weight_pct must be positive")
            if not isinstance(trigger, str) or not trigger.strip():
                errors.append(f"entries[{index}] is missing an observable trigger")
                entry_triggers_ok = False
            if not isinstance(execution_window, str) or not execution_window.strip():
                timed_entries = False
                errors.append(f"entries[{index}] is missing an execution_window")
            total_weight += weight
            entries.append(
                {
                    "name": str(raw.get("name", f"entry_{index + 1}")),
                    "price": price,
                    "weight_pct": weight,
                    "trigger": trigger,
                    "execution_window": execution_window,
                }
            )
        if abs(total_weight - 100.0) > 0.01:
            errors.append(f"entry weights must total 100%, got {total_weight:.4f}%")

        time_stop_raw = payload.get("time_stop")
        time_stop_ok = True
        time_stop_checks: dict[str, Any] = {
            "present": time_stop_raw is not None,
            "format": None,
            "horizon_present": False,
            "trigger_present": False,
            "action_present": False,
            "applies_to": None,
            "errors": [],
        }
        time_stop_errors: list[str] = time_stop_checks["errors"]
        if isinstance(time_stop_raw, str):
            time_stop_checks["format"] = "legacy_text"
            if time_stop_raw.strip():
                time_stop_checks["horizon_present"] = True
                time_stop_checks["trigger_present"] = True
                time_stop_checks["action_present"] = True
                warnings.append(
                    "time_stop is free text; prefer a structured horizon, trigger, action, and applies_to"
                )
            else:
                time_stop_errors.append("time_stop text must not be empty")
        elif isinstance(time_stop_raw, dict):
            time_stop_checks["format"] = "structured"
            max_trading_days = optional_number(
                time_stop_raw.get("max_trading_days"),
                "time_stop.max_trading_days",
            )
            deadline = time_stop_raw.get("deadline")
            horizon_present = False
            if max_trading_days is not None:
                if max_trading_days <= 0 or not math.isclose(
                    max_trading_days, round(max_trading_days)
                ):
                    time_stop_errors.append(
                        "time_stop.max_trading_days must be a positive whole number"
                    )
                else:
                    horizon_present = True
            if deadline is not None:
                if not non_empty_text(deadline):
                    time_stop_errors.append("time_stop.deadline must be non-empty text")
                else:
                    try:
                        deadline_time = datetime.fromisoformat(
                            str(deadline).strip().replace("Z", "+00:00")
                        )
                    except ValueError:
                        time_stop_errors.append(
                            "time_stop.deadline must be an ISO-8601 date or timestamp"
                        )
                    else:
                        if (
                            analysis_time is not None
                            and deadline_time.date() < analysis_time.date()
                        ):
                            time_stop_errors.append(
                                "time_stop.deadline is earlier than the analysis date"
                            )
                        else:
                            horizon_present = True
            if not horizon_present:
                time_stop_errors.append(
                    "time_stop requires max_trading_days or an ISO-8601 deadline"
                )
            trigger_present = non_empty_text(time_stop_raw.get("trigger"))
            action_present = non_empty_text(time_stop_raw.get("action"))
            applies_to = str(time_stop_raw.get("applies_to", "")).strip().lower()
            valid_scopes = {
                "trading_position",
                "trade_sleeve",
                "long_term_review",
                "investment_position",
            }
            if not trigger_present:
                time_stop_errors.append("time_stop.trigger is required")
            if not action_present:
                time_stop_errors.append("time_stop.action is required")
            if applies_to not in valid_scopes:
                time_stop_errors.append(
                    "time_stop.applies_to must identify a trading or investment position"
                )
            time_stop_checks.update(
                {
                    "horizon_present": horizon_present,
                    "max_trading_days": max_trading_days,
                    "deadline": deadline,
                    "trigger_present": trigger_present,
                    "action_present": action_present,
                    "applies_to": applies_to or None,
                }
            )
        elif time_stop_raw is None:
            time_stop_errors.append("time_stop is required for a final trade plan")
        else:
            time_stop_errors.append("time_stop must be text or an object")

        if time_stop_errors:
            errors.extend(time_stop_errors)
            time_stop_ok = False
        gates["time"] = timed_entries and time_stop_ok

        weighted_entry = sum(
            item["price"] * item["weight_pct"] for item in entries
        ) / total_weight
        stop = finite_number(payload.get("stop"), "stop")
        stop_basis = payload.get("stop_basis")
        if stop <= 0:
            raise ValueError("stop must be positive")
        stop_direction_ok = stop < min(item["price"] for item in entries)
        if side == "short":
            stop_direction_ok = stop > max(item["price"] for item in entries)
        structure_ok = stop_direction_ok and entry_triggers_ok
        if not stop_direction_ok:
            errors.append("stop is on the wrong side of one or more staged entry prices")
        if not isinstance(stop_basis, str) or not stop_basis.strip():
            errors.append("stop_basis is required and must identify the structural invalidation")
            structure_ok = False

        targets_raw = payload.get("targets")
        if not isinstance(targets_raw, list) or not targets_raw:
            raise ValueError("targets must be a non-empty array")
        targets: list[dict[str, Any]] = []
        exit_total = 0.0
        previous_target: float | None = None
        for index, raw in enumerate(targets_raw):
            if not isinstance(raw, dict):
                raise ValueError(f"targets[{index}] must be an object")
            price = finite_number(raw.get("price"), f"targets[{index}].price")
            exit_pct = finite_number(
                raw.get("exit_pct"), f"targets[{index}].exit_pct"
            )
            if price <= 0 or exit_pct <= 0:
                raise ValueError(f"targets[{index}] price and exit_pct must be positive")
            if not price_is_above(price, weighted_entry, side):
                errors.append(f"targets[{index}] is not profitable versus weighted entry")
                structure_ok = False
            if previous_target is not None and not price_is_above(
                price, previous_target, side
            ):
                errors.append("targets are not ordered in the trade direction")
                structure_ok = False
            previous_target = price
            exit_total += exit_pct
            targets.append(
                {
                    "name": str(raw.get("name", f"target_{index + 1}")),
                    "price": price,
                    "exit_pct": exit_pct,
                }
            )
        if exit_total > 100.01:
            errors.append(f"target exit percentages exceed 100%, got {exit_total:.4f}%")
            structure_ok = False
        runner_rule = payload.get("runner_exit_rule")
        if exit_total < 99.99 and (
            not isinstance(runner_rule, str) or not runner_rule.strip()
        ):
            errors.append("targets leave a runner but runner_exit_rule is missing")
            structure_ok = False
        gates["structure"] = structure_ok

        slippage_pct = finite_number(payload.get("slippage_pct", 0), "slippage_pct")
        round_trip_cost_pct = finite_number(
            payload.get("round_trip_cost_pct", 0), "round_trip_cost_pct"
        )
        round_trip_cost_per_share = finite_number(
            payload.get("round_trip_cost_per_share", 0),
            "round_trip_cost_per_share",
        )
        min_rr = finite_number(payload.get("min_reward_risk", 2), "min_reward_risk")
        if (
            slippage_pct < 0
            or round_trip_cost_pct < 0
            or round_trip_cost_per_share < 0
            or min_rr <= 0
        ):
            raise ValueError(
                "slippage and round-trip costs must be non-negative and min_reward_risk positive"
            )
        raw_risk = (
            weighted_entry - stop if side == "long" else stop - weighted_entry
        )
        modeled_transaction_cost_per_share = (
            weighted_entry * round_trip_cost_pct / 100.0
            + round_trip_cost_per_share
        )
        modeled_risk = (
            raw_risk
            + weighted_entry * slippage_pct / 100.0
            + modeled_transaction_cost_per_share
        )
        first_target = targets[0]["price"]
        first_raw_reward = (
            first_target - weighted_entry
            if side == "long"
            else weighted_entry - first_target
        )
        first_net_reward = first_raw_reward - modeled_transaction_cost_per_share
        first_rr = first_net_reward / modeled_risk if modeled_risk > 0 else None
        gates["reward"] = bool(first_rr is not None and first_rr >= min_rr)
        if gates["reward"] is False:
            rr_display = "N/A" if first_rr is None else f"{first_rr:.3f}"
            errors.append(
                f"first-target net reward/risk is {rr_display}, below required {min_rr:.3f}"
            )

        risk_ok = raw_risk > 0 and bool(stop_basis)
        atr = optional_number(payload.get("atr"), "atr")
        atr_multiple = None
        if atr is not None:
            if atr <= 0:
                raise ValueError("atr must be positive")
            atr_multiple = raw_risk / atr
            if atr_multiple < 0.5:
                warnings.append(
                    "stop distance is below 0.5 ATR; ordinary volatility may trigger it"
                )
            elif atr_multiple > 3:
                warnings.append(
                    "stop distance exceeds 3 ATR; position size may need to be reduced"
                )
        else:
            warnings.append("ATR was not supplied; stop noise tolerance was not checked")
        gates["risk"] = risk_ok

        consistency_ok = True
        for item in entries[1:]:
            if not price_is_above(first_target, item["price"], side):
                errors.append(
                    f"{item['name']} entry conflicts with or occurs beyond the first exit target"
                )
                consistency_ok = False

        barriers = parse_barriers(payload.get("known_barriers"))
        barriers_ahead = [
            item
            for item in barriers
            if price_is_above(item["price"], weighted_entry, side)
            and price_is_above(first_target, item["price"], side)
        ]
        if barriers_ahead:
            nearest = min(barriers_ahead, key=lambda item: abs(item["price"] - weighted_entry))
            tolerance = abs(nearest["price"]) * 0.01
            if all(abs(target["price"] - nearest["price"]) > tolerance for target in targets):
                errors.append(
                    f"first target skips nearer known barrier {nearest['label']} at {nearest['price']}"
                )
                consistency_ok = False
        gates["consistency"] = consistency_ok

        market_rule_checks: dict[str, Any] | None = None
        if market_context_raw is not None and not isinstance(
            market_context_raw, dict
        ):
            raise ValueError("market_context must be an object")
        if market == "HK":
            market_rule_errors: list[str] = []
            market_context = market_context_raw
            if market_context is None:
                market_rule_errors.append(
                    "HK plan requires market_context with current market rules"
                )
                market_context = {}

            exchange = str(market_context.get("exchange", "")).strip().upper()
            native_symbol = str(
                market_context.get("native_symbol", "")
            ).strip()
            counter_currency = str(
                market_context.get("counter_currency", "")
            ).strip().upper()
            if exchange not in {"HKEX", "SEHK"}:
                market_rule_errors.append("market_context.exchange must identify HKEX/SEHK")
            if not re.fullmatch(r"\d{5}", native_symbol):
                market_rule_errors.append(
                    "market_context.native_symbol must be the five-digit zero-padded HKEX code"
                )
            if not counter_currency:
                market_rule_errors.append(
                    "market_context.counter_currency is required"
                )
            trading_path = str(
                market_context.get("trading_path", "")
            ).strip().lower()
            valid_trading_paths = {
                "broker",
                "hong_kong_broker",
                "international_broker",
                "southbound_stock_connect",
                "stock_connect",
                "other",
            }
            if trading_path not in valid_trading_paths:
                market_rule_errors.append(
                    "market_context.trading_path must identify broker, Stock Connect, or other"
                )
            if not non_empty_text(market_context.get("trading_path_source")):
                market_rule_errors.append(
                    "market_context.trading_path_source is required"
                )
            if trading_path == "other" and not non_empty_text(
                market_context.get("trading_path_details")
            ):
                market_rule_errors.append(
                    "market_context.trading_path_details is required when trading_path is other"
                )
            if isinstance(data_context, dict):
                quote_currency = data_context.get("quote_currency")
                if quote_currency is not None and str(quote_currency).strip().upper() != counter_currency:
                    market_rule_errors.append(
                        "data_context.quote_currency conflicts with market_context.counter_currency"
                    )

            board_lot_size = optional_number(
                market_context.get("board_lot_size"),
                "market_context.board_lot_size",
            )
            if (
                board_lot_size is None
                or board_lot_size <= 0
                or not math.isclose(board_lot_size, round(board_lot_size))
            ):
                market_rule_errors.append(
                    "market_context.board_lot_size must be a positive whole number"
                )
            if not non_empty_text(market_context.get("board_lot_source")):
                market_rule_errors.append(
                    "market_context.board_lot_source is required"
                )

            required_rule_checks = (
                ("price_tick_checked", "price_tick_source"),
                ("fee_schedule_checked", "fee_schedule_source"),
                ("trading_calendar_checked", "trading_calendar_source"),
                ("settlement_cycle_checked", "settlement_cycle_source"),
                ("corporate_actions_checked", "corporate_actions_source"),
            )
            for checked_field, source_field in required_rule_checks:
                if market_context.get(checked_field) is not True:
                    market_rule_errors.append(
                        f"market_context.{checked_field} must be true"
                    )
                if not non_empty_text(market_context.get(source_field)):
                    market_rule_errors.append(
                        f"market_context.{source_field} is required"
                    )

            costs_supplied = (
                "round_trip_cost_pct" in payload
                or "round_trip_cost_per_share" in payload
            )
            if not costs_supplied:
                market_rule_errors.append(
                    "HK plan must explicitly supply modeled round-trip transaction costs"
                )

            planned_shares = optional_number(
                payload.get("planned_shares"), "planned_shares"
            )
            odd_lot_plan = market_context.get("odd_lot_plan")
            board_lot_multiple: bool | None = None
            if planned_shares is not None:
                if planned_shares <= 0 or not math.isclose(
                    planned_shares, round(planned_shares)
                ):
                    market_rule_errors.append(
                        "planned_shares must be a positive whole number"
                    )
                elif board_lot_size is not None and board_lot_size > 0:
                    remainder = planned_shares % board_lot_size
                    board_lot_multiple = math.isclose(
                        remainder, 0.0, abs_tol=1e-8
                    ) or math.isclose(
                        remainder, board_lot_size, abs_tol=1e-8
                    )
                    if not board_lot_multiple and not non_empty_text(odd_lot_plan):
                        market_rule_errors.append(
                            "planned_shares is not a board-lot multiple and market_context.odd_lot_plan is missing"
                        )

            short_eligibility_checked = market_context.get(
                "short_eligibility_checked"
            )
            if side == "short":
                if short_eligibility_checked is not True:
                    market_rule_errors.append(
                        "HK short plan requires short_eligibility_checked=true"
                    )
                if not non_empty_text(
                    market_context.get("short_eligibility_source")
                ):
                    market_rule_errors.append(
                        "HK short plan requires short_eligibility_source"
                    )

            if data_checks.get("market_state") in {
                "pre_opening",
                "midday_break",
                "closing_auction",
            }:
                warnings.append(
                    "HK non-continuous or auction state cannot use ordinary continuous-book timing"
                )

            market_rules_ok = not market_rule_errors
            gates["market_rules"] = market_rules_ok
            errors.extend(market_rule_errors)
            market_rule_checks = {
                "market": market,
                "exchange": exchange or None,
                "native_symbol": native_symbol or None,
                "counter_currency": counter_currency or None,
                "trading_path": trading_path or None,
                "board_lot_size": board_lot_size,
                "planned_shares": planned_shares,
                "board_lot_multiple": board_lot_multiple,
                "odd_lot_plan_present": non_empty_text(odd_lot_plan),
                "price_tick_checked": market_context.get(
                    "price_tick_checked"
                ),
                "fee_schedule_checked": market_context.get(
                    "fee_schedule_checked"
                ),
                "trading_calendar_checked": market_context.get(
                    "trading_calendar_checked"
                ),
                "settlement_cycle_checked": market_context.get(
                    "settlement_cycle_checked"
                ),
                "corporate_actions_checked": market_context.get(
                    "corporate_actions_checked"
                ),
                "transaction_costs_supplied": costs_supplied,
                "short_eligibility_checked": short_eligibility_checked,
                "source_validation_scope": (
                    "presence_and_internal_consistency_only; source content, freshness, "
                    "and applicability require external verification"
                ),
                "sources": {
                    "board_lot": market_context.get("board_lot_source"),
                    "price_tick": market_context.get("price_tick_source"),
                    "fee_schedule": market_context.get(
                        "fee_schedule_source"
                    ),
                    "trading_calendar": market_context.get(
                        "trading_calendar_source"
                    ),
                    "trading_path": market_context.get(
                        "trading_path_source"
                    ),
                    "settlement_cycle": market_context.get(
                        "settlement_cycle_source"
                    ),
                    "corporate_actions": market_context.get(
                        "corporate_actions_source"
                    ),
                    "short_eligibility": market_context.get(
                        "short_eligibility_source"
                    ),
                },
                "errors": market_rule_errors,
            }

        event_days = payload.get("event_trading_days")
        event_plan = payload.get("event_plan")
        if event_days is not None:
            event_days_value = finite_number(event_days, "event_trading_days")
            if event_days_value < 0:
                raise ValueError("event_trading_days cannot be negative")
            if event_days_value <= 5 and (
                not isinstance(event_plan, str) or not event_plan.strip()
            ):
                gates["event"] = False
                errors.append("major event is within 5 trading days but event_plan is missing")
            else:
                gates["event"] = True

        liquidity_checked = payload.get("liquidity_checked")
        if liquidity_checked is not None and not isinstance(liquidity_checked, bool):
            raise ValueError("liquidity_checked must be true, false, or null")
        requires_live_depth = payload.get("requires_live_market_depth", False)
        if not isinstance(requires_live_depth, bool):
            raise ValueError("requires_live_market_depth must be true or false")

        market_depth_checks: dict[str, Any] | None = None
        market_depth_context = payload.get("market_depth_context")
        liquidity_ok = liquidity_checked
        if market_depth_context is not None:
            if not isinstance(market_depth_context, dict):
                raise ValueError("market_depth_context must be an object")
            quality = market_depth_context.get("data_quality", market_depth_context)
            top = market_depth_context.get("top_of_book", market_depth_context)
            snapshot = market_depth_context.get("snapshot", market_depth_context)
            if not isinstance(quality, dict) or not isinstance(top, dict) or not isinstance(snapshot, dict):
                raise ValueError("market_depth_context nested values must be objects")

            status_value = str(quality.get("status", "unknown"))
            execution_eligible = bool(quality.get("execution_timing_eligible", False))
            synthetic_detected = bool(quality.get("synthetic_data_detected", False))
            quote_scope = str(snapshot.get("quote_scope", market_depth_context.get("quote_scope", "unknown")))
            spread_bps = optional_number(top.get("spread_bps"), "market_depth_context.spread_bps")
            max_spread_bps = optional_number(
                market_depth_context.get("max_spread_bps"),
                "market_depth_context.max_spread_bps",
            )
            displayed_depth_sufficient = market_depth_context.get("displayed_depth_sufficient")
            if displayed_depth_sufficient is not None and not isinstance(displayed_depth_sufficient, bool):
                raise ValueError("market_depth_context.displayed_depth_sufficient must be true, false, or null")

            depth_errors: list[str] = []
            if synthetic_detected:
                depth_errors.append("market-depth context is synthetic or simulated")
                gates["data"] = False
            if status_value == "unusable":
                depth_errors.append("market-depth context is unusable")
            if requires_live_depth and not execution_eligible:
                depth_errors.append("plan requires live market depth but execution_timing_eligible is false")
            if max_spread_bps is not None:
                if max_spread_bps <= 0:
                    raise ValueError("market_depth_context.max_spread_bps must be positive")
                if spread_bps is None:
                    depth_errors.append("spread_bps is required when max_spread_bps is set")
                elif spread_bps > max_spread_bps:
                    depth_errors.append(
                        f"market-depth spread is {spread_bps:.3f} bps, above maximum {max_spread_bps:.3f} bps"
                    )
            if displayed_depth_sufficient is False:
                depth_errors.append("displayed market depth is insufficient for the planned size")

            if quote_scope in {"single_venue", "unknown"}:
                warnings.append(
                    "market-depth scope is single-venue or unknown; it cannot prove full-market liquidity"
                )
            if depth_errors:
                errors.extend(depth_errors)
                liquidity_ok = False
            elif liquidity_ok is None:
                liquidity_ok = True

            market_depth_checks = {
                "status": status_value,
                "execution_timing_eligible": execution_eligible,
                "requires_live_market_depth": requires_live_depth,
                "synthetic_data_detected": synthetic_detected,
                "quote_scope": quote_scope,
                "spread_bps": spread_bps,
                "max_spread_bps": max_spread_bps,
                "displayed_depth_sufficient": displayed_depth_sufficient,
                "errors": depth_errors,
            }
        elif requires_live_depth:
            errors.append("plan requires live market depth but market_depth_context is missing")
            liquidity_ok = False

        gates["liquidity"] = liquidity_ok

        failed_gates = [name for name, value in gates.items() if value is False]
        unchecked_gates = [name for name, value in gates.items() if value is None]
        if failed_gates or errors:
            status = "revise_plan_or_wait"
        elif unchecked_gates:
            status = "analysis_only_until_checks_complete"
        else:
            status = "plan_passes_internal_checks"

        target_metrics = []
        for target in targets:
            raw_reward = (
                target["price"] - weighted_entry
                if side == "long"
                else weighted_entry - target["price"]
            )
            net_reward = raw_reward - modeled_transaction_cost_per_share
            target_metrics.append(
                {
                    **target,
                    "raw_reward_per_share": round(raw_reward, 6),
                    "net_reward_per_share": round(net_reward, 6),
                    "reward_per_share": round(net_reward, 6),
                    "reward_risk_ratio": (
                        round(net_reward / modeled_risk, 6)
                        if modeled_risk > 0
                        else None
                    ),
                }
            )

        result = {
            "status": status,
            "market": market,
            "side": side,
            "weighted_entry": round(weighted_entry, 6),
            "entry_weight_total_pct": round(total_weight, 6),
            "stop": stop,
            "raw_risk_per_share": round(raw_risk, 6),
            "modeled_transaction_cost_per_share": round(
                modeled_transaction_cost_per_share, 6
            ),
            "round_trip_cost_pct": round(round_trip_cost_pct, 6),
            "round_trip_cost_per_share": round(round_trip_cost_per_share, 6),
            "modeled_risk_per_share": round(modeled_risk, 6),
            "stop_distance_atr": round(atr_multiple, 6) if atr_multiple is not None else None,
            "minimum_reward_risk": min_rr,
            "targets": target_metrics,
            "data_checks": data_checks,
            "market_rule_checks": market_rule_checks,
            "market_depth_checks": market_depth_checks,
            "time_stop_checks": time_stop_checks,
            "gates": gates,
            "failed_gates": failed_gates,
            "unchecked_gates": unchecked_gates,
            "errors": errors,
            "warnings": warnings,
            "note": (
                "This checks arithmetic and plan consistency, not future outcomes. "
                "Gaps, partial fills, unmodeled taxes/fees, FX moves, and market impact "
                "can worsen results."
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
