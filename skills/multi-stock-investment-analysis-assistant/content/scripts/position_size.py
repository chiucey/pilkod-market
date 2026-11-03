#!/usr/bin/env python3
"""Calculate risk-budgeted equity size with lot, cost, and FX constraints."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_FLOOR


def decimal_arg(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"invalid number: {value}") from exc
    if not parsed.is_finite():
        raise argparse.ArgumentTypeError(f"number must be finite: {value}")
    return parsed


def floor_to_step(value: Decimal, step: Decimal) -> Decimal:
    return (value / step).to_integral_value(rounding=ROUND_FLOOR) * step


def as_number(value: Decimal, places: int = 8) -> int | float:
    quantizer = Decimal(1).scaleb(-places)
    rounded = value.quantize(quantizer).normalize()
    if rounded == rounded.to_integral_value():
        return int(rounded)
    return float(rounded)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate equity position size from account risk and allocation limits."
    )
    parser.add_argument("--account", required=True, type=decimal_arg)
    parser.add_argument(
        "--account-currency",
        help="Account equity currency, for example USD or HKD",
    )
    parser.add_argument("--entry", required=True, type=decimal_arg)
    parser.add_argument("--stop", required=True, type=decimal_arg)
    parser.add_argument(
        "--quote-currency",
        help="Security trading/quote currency, for example USD, HKD, or CNY",
    )
    parser.add_argument(
        "--fx-quote-per-account",
        type=decimal_arg,
        help="Quote-currency units per one account-currency unit; required when currencies differ",
    )
    parser.add_argument("--risk-pct", required=True, type=decimal_arg)
    parser.add_argument(
        "--max-allocation-pct", required=True, type=decimal_arg
    )
    parser.add_argument("--side", choices=("long", "short"), default="long")
    parser.add_argument("--target", type=decimal_arg)
    parser.add_argument(
        "--lot-step",
        "--board-lot-size",
        dest="lot_step",
        type=decimal_arg,
        default=Decimal("1"),
        help="Share increment: US whole/fractional step or the current HKEX board-lot size",
    )
    parser.add_argument(
        "--slippage-pct",
        type=decimal_arg,
        default=Decimal("0"),
        help="Additional adverse move as a percentage of entry",
    )
    parser.add_argument(
        "--round-trip-fee-per-share",
        type=decimal_arg,
        default=Decimal("0"),
    )
    parser.add_argument(
        "--round-trip-fee-pct",
        type=decimal_arg,
        default=Decimal("0"),
        help="Estimated all-in round-trip costs as a percentage of entry notional",
    )
    parser.add_argument("--output", default="-", help="JSON path, or - for stdout")
    args = parser.parse_args()

    try:
        if args.account <= 0 or args.entry <= 0:
            raise ValueError("account and entry must be greater than zero")
        if args.risk_pct <= 0 or args.risk_pct > 100:
            raise ValueError("risk-pct must be greater than 0 and at most 100")
        if args.max_allocation_pct <= 0 or args.max_allocation_pct > 100:
            raise ValueError(
                "max-allocation-pct must be greater than 0 and at most 100"
            )
        if args.lot_step <= 0:
            raise ValueError("lot-step must be greater than zero")
        if (
            args.slippage_pct < 0
            or args.round_trip_fee_per_share < 0
            or args.round_trip_fee_pct < 0
        ):
            raise ValueError("slippage and fees cannot be negative")

        account_currency = (
            args.account_currency.strip().upper() if args.account_currency else None
        )
        quote_currency = (
            args.quote_currency.strip().upper() if args.quote_currency else None
        )
        if bool(account_currency) != bool(quote_currency):
            raise ValueError(
                "account-currency and quote-currency must be supplied together"
            )
        fx_quote_per_account = args.fx_quote_per_account
        if account_currency and quote_currency and account_currency != quote_currency:
            if fx_quote_per_account is None or fx_quote_per_account <= 0:
                raise ValueError(
                    "fx-quote-per-account must be positive when account and quote currencies differ"
                )
        else:
            if fx_quote_per_account is None:
                fx_quote_per_account = Decimal("1")
            elif fx_quote_per_account != 1:
                raise ValueError(
                    "fx-quote-per-account must equal 1 when currencies match or are omitted"
                )
        if args.side == "long" and args.stop >= args.entry:
            raise ValueError("for a long position, stop must be below entry")
        if args.side == "short" and args.stop <= args.entry:
            raise ValueError("for a short position, stop must be above entry")

        raw_price_risk = (
            args.entry - args.stop
            if args.side == "long"
            else args.stop - args.entry
        )
        slippage_per_share = args.entry * args.slippage_pct / Decimal("100")
        percentage_fee_per_share = (
            args.entry * args.round_trip_fee_pct / Decimal("100")
        )
        transaction_cost_per_share = (
            percentage_fee_per_share + args.round_trip_fee_per_share
        )
        risk_per_share = (
            raw_price_risk
            + slippage_per_share
            + transaction_cost_per_share
        )
        risk_budget_account = args.account * args.risk_pct / Decimal("100")
        allocation_budget_account = (
            args.account * args.max_allocation_pct / Decimal("100")
        )
        risk_budget_quote = risk_budget_account * fx_quote_per_account
        allocation_budget_quote = (
            allocation_budget_account * fx_quote_per_account
        )

        quantity_by_risk = floor_to_step(
            risk_budget_quote / risk_per_share, args.lot_step
        )
        quantity_by_allocation = floor_to_step(
            allocation_budget_quote / args.entry, args.lot_step
        )
        quantity = min(quantity_by_risk, quantity_by_allocation)
        below_minimum_lot = quantity <= 0

        capital_used_quote = quantity * args.entry
        capital_used_account = capital_used_quote / fx_quote_per_account
        estimated_loss_at_stop_quote = quantity * risk_per_share
        estimated_loss_at_stop_account = (
            estimated_loss_at_stop_quote / fx_quote_per_account
        )
        actual_risk_pct = (
            estimated_loss_at_stop_account / args.account * Decimal("100")
        )
        allocation_used_pct = (
            capital_used_account / args.account * Decimal("100")
        )

        target_payload: dict[str, int | float | None] = {
            "target": None,
            "raw_reward_per_share": None,
            "reward_per_share": None,
            "reward_risk_ratio": None,
        }
        if args.target is not None:
            if args.side == "long" and args.target <= args.entry:
                raise ValueError("for a long position, target must be above entry")
            if args.side == "short" and args.target >= args.entry:
                raise ValueError("for a short position, target must be below entry")
            raw_reward_per_share = (
                args.target - args.entry
                if args.side == "long"
                else args.entry - args.target
            )
            reward_per_share = raw_reward_per_share - transaction_cost_per_share
            target_payload = {
                "target": as_number(args.target),
                "raw_reward_per_share": as_number(raw_reward_per_share),
                "reward_per_share": as_number(reward_per_share),
                "reward_risk_ratio": as_number(
                    reward_per_share / risk_per_share
                ),
            }

        result = {
            "status": (
                "wait_below_minimum_lot"
                if below_minimum_lot
                else "position_size_available"
            ),
            "action": "wait" if below_minimum_lot else "size_within_limits",
            "side": args.side,
            "units": {
                "account_currency": account_currency,
                "quote_currency": quote_currency,
                "quantity": "shares",
                "risk_budget": "account_currency",
                "allocation_budget": "account_currency",
                "capital_used": "quote_currency",
                "estimated_loss_at_stop": "quote_currency",
            },
            "inputs": {
                "account": as_number(args.account),
                "account_currency": account_currency,
                "entry": as_number(args.entry),
                "stop": as_number(args.stop),
                "quote_currency": quote_currency,
                "fx_quote_per_account": as_number(fx_quote_per_account),
                "risk_pct": as_number(args.risk_pct),
                "max_allocation_pct": as_number(args.max_allocation_pct),
                "lot_step": as_number(args.lot_step),
                "slippage_pct": as_number(args.slippage_pct),
                "round_trip_fee_per_share": as_number(
                    args.round_trip_fee_per_share
                ),
                "round_trip_fee_pct": as_number(args.round_trip_fee_pct),
            },
            "risk_budget": as_number(risk_budget_account),
            "allocation_budget": as_number(allocation_budget_account),
            "risk_budget_account_currency": as_number(risk_budget_account),
            "risk_budget_quote_currency": as_number(risk_budget_quote),
            "allocation_budget_account_currency": as_number(
                allocation_budget_account
            ),
            "allocation_budget_quote_currency": as_number(
                allocation_budget_quote
            ),
            "raw_price_risk_per_share": as_number(raw_price_risk),
            "slippage_per_share": as_number(slippage_per_share),
            "modeled_transaction_cost_per_share": as_number(
                transaction_cost_per_share
            ),
            "modeled_risk_per_share": as_number(risk_per_share),
            "quantity_by_risk": as_number(quantity_by_risk),
            "quantity_by_allocation": as_number(quantity_by_allocation),
            "quantity": as_number(quantity),
            "capital_used": as_number(capital_used_quote),
            "capital_used_quote_currency": as_number(capital_used_quote),
            "capital_used_account_currency": as_number(capital_used_account),
            "allocation_used_pct": as_number(allocation_used_pct),
            "estimated_loss_at_stop": as_number(
                estimated_loss_at_stop_quote
            ),
            "estimated_loss_at_stop_quote_currency": as_number(
                estimated_loss_at_stop_quote
            ),
            "estimated_loss_at_stop_account_currency": as_number(
                estimated_loss_at_stop_account
            ),
            "actual_account_risk_pct": as_number(actual_risk_pct),
            **target_payload,
            "note": (
                (
                    "Risk or allocation budget is below one permitted lot; do not round "
                    "up beyond the supplied limits. "
                    if below_minimum_lot
                    else ""
                )
                + "Stops can gap and fill worse than modeled. Taxes and fees are only "
                "included to the extent entered. Borrow costs, partial fills, market "
                "impact, and FX movement after the supplied snapshot are not modeled."
            ),
        }

        payload = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output == "-":
            print(payload)
        else:
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write(payload + "\n")
    except (OSError, ValueError, InvalidOperation) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
