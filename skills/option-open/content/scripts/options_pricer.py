#!/usr/bin/env python3
"""期权定价与策略分析工具（Black-Scholes）— option_open skill 核心

用法:
  # 单腿定价（含 greeks）
  python3 options_pricer.py price --spot 334.98 --strike 335 --days 22 --iv 0.31 --type call

  # 由市场价格反推 IV
  python3 options_pricer.py iv --spot 334.98 --strike 335 --days 22 --price 10.16 --type call

  # 策略分析（净支出/收租、到期最大盈亏、盈亏平衡、短腿 delta、到期损益曲线）
  #   legs 格式: direction_type:strike:days:premium，多腿逗号分隔
  python3 options_pricer.py strategy --legs buy_call:335:22:10.16,sell_call:345:22:5.96 --spot 334.98 --iv 0.31

  # 持仓状态评估（option_close 场景：现价下的浮盈浮亏、短腿 delta 铁律检查）
  #   --days 为各腿剩余天数（覆盖 legs 里的 days），--entry 为开仓净收租(+)/净支出(-)
  python3 options_pricer.py status --legs sell_call:63:16:0.89,sell_put:53:16:0.90 --spot 63.5 --iv 0.45 --entry 1.79

约定:
  - 无风险利率默认 4%（r 可调）；美式期权按欧式近似（短周期误差可忽略）
  - premium 指该腿当前市价（per share），策略分析里同时给出理论价对比
"""
import argparse
import json
import sys

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

R = 0.04


def bs_all(S, K, T, sigma, r=R):
    """返回 (call价, put价, call_delta, put_delta, gamma, theta_call/day, vega)"""
    if T <= 0 or sigma <= 0:
        ic = max(S - K, 0.0)
        ip = max(K - S, 0.0)
        return ic, ip, float(S > K), -float(S < K), 0.0, 0.0, 0.0
    sq = sigma * np.sqrt(T)
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / sq
    d2 = d1 - sq
    call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    delta_c = norm.cdf(d1)
    delta_p = -norm.cdf(-d1)
    gamma = norm.pdf(d1) / (S * sq)
    theta_c = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
               - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365.0
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100.0
    return call, put, delta_c, delta_p, gamma, theta_c, vega


def implied_vol(S, K, T, price, opt_type, r=R):
    def f(sig):
        c, p, *_ = bs_all(S, K, T, sig, r)
        return (c if opt_type == "call" else p) - price
    try:
        return brentq(f, 1e-4, 5.0, xtol=1e-6)
    except Exception:
        return None


def parse_legs(spec):
    legs = []
    for part in spec.split(","):
        dir_type, strike, days, prem = part.split(":")
        d, t = dir_type.split("_")
        legs.append({"direction": d, "type": t, "strike": float(strike),
                     "days": float(days), "premium": float(prem)})
    return legs


def payoff_at_expiry(legs, S):
    """到期损益（per share，正=盈利）"""
    total = 0.0
    for lg in legs:
        sign = 1 if lg["direction"] == "buy" else -1
        intrinsic = max(S - lg["strike"], 0.0) if lg["type"] == "call" else max(lg["strike"] - S, 0.0)
        total += sign * (intrinsic - lg["premium"])
    return total


def analyze_strategy(legs, spot, iv, r=R):
    net = sum((1 if l["direction"] == "buy" else -1) * l["premium"] for l in legs)
    # 到期损益曲线扫描
    los = min(l["strike"] for l in legs) * 0.6
    his = max(l["strike"] for l in legs) * 1.4
    grid = np.linspace(los, his, 4001)
    po = np.array([payoff_at_expiry(legs, s) for s in grid])
    max_pl, min_pl = po.max(), po.min()
    # 盈亏平衡点（符号变化处线性插值）
    bes = []
    for i in range(1, len(grid)):
        if po[i - 1] == 0:
            bes.append(grid[i - 1])
        elif po[i - 1] * po[i] < 0:
            bes.append(grid[i - 1] + (0 - po[i - 1]) / (po[i] - po[i - 1]) * (grid[i] - grid[i - 1]))
    # 理论价与短腿 delta（用统一 IV 建模，用于 sanity check 与风控）
    theo_net = 0.0
    leg_details = []
    for lg in legs:
        T = lg["days"] / 365.0
        c, p, dc, dp, g, th, v = bs_all(spot, lg["strike"], T, iv, r)
        px, dl = (c, dc) if lg["type"] == "call" else (p, dp)
        sign = 1 if lg["direction"] == "buy" else -1
        theo_net += sign * px
        leg_details.append({
            "leg": f'{lg["direction"]}_{lg["type"]}_{lg["strike"]:.0f}',
            "market_premium": lg["premium"], "bs_theoretical": round(px, 2),
            "premium_vs_theory": round(lg["premium"] - px, 2),
            "position_delta": round(sign * dl, 3),
            "bs_iv_used": iv,
        })
    short_legs = [d for d, l in zip(leg_details, legs) if l["direction"] == "sell"]
    # 符号约定: net > 0 = 净支出(买入价差)，net < 0 = 净收租(卖出结构)
    return {
        "net_premium": round(net, 2),
        "net_premium_type": "净支出(debit)" if net > 0 else "收租(credit)",
        "structure_side": "买方" if net > 0 else "卖方",
        "bs_theoretical_net": round(theo_net, 2),
        "max_profit": round(max_pl, 2) if max_pl < 1e6 else "无限",
        "max_loss": round(min_pl, 2) if min_pl > -1e6 else "无限",
        "breakevens": [round(b, 2) for b in bes],
        "legs": leg_details,
        "short_leg_deltas": [d["position_delta"] for d in short_legs],
        # delta>0.30 铁律只约束收租型(credit)结构的短腿；买方价差的短腿是结构的一部分，不适用
        "short_leg_delta_breach_030": (net < 0
                                       and any(abs(d["position_delta"]) > 0.30 for d in short_legs)),
    }


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("price")
    p1.add_argument("--spot", type=float, required=True)
    p1.add_argument("--strike", type=float, required=True)
    p1.add_argument("--days", type=float, required=True)
    p1.add_argument("--iv", type=float, required=True)
    p1.add_argument("--type", choices=["call", "put"], required=True)

    p2 = sub.add_parser("iv")
    for a in ("spot", "strike", "days", "price"):
        p2.add_argument(f"--{a}", type=float, required=True)
    p2.add_argument("--type", choices=["call", "put"], required=True)

    p3 = sub.add_parser("strategy")
    p3.add_argument("--legs", required=True)
    p3.add_argument("--spot", type=float, required=True)
    p3.add_argument("--iv", type=float, required=True)

    p4 = sub.add_parser("status")
    p4.add_argument("--legs", required=True, help="legs 里 days 填剩余天数")
    p4.add_argument("--spot", type=float, required=True)
    p4.add_argument("--iv", type=float, required=True)
    p4.add_argument("--entry", type=float, default=None,
                    help="开仓净收租(+)/净支出(-)，不填则只报结构状态")

    args = ap.parse_args()
    if args.cmd == "price":
        T = args.days / 365.0
        c, p, dc, dp, g, th, v = bs_all(args.spot, args.strike, T, args.iv)
        px, dl = (c, dc) if args.type == "call" else (p, dp)
        print(json.dumps({"price": round(px, 2), "delta": round(dl, 3),
                          "gamma": round(g, 5), "theta_per_day": round(th, 3),
                          "vega_per_1pct_iv": round(v, 3)}, ensure_ascii=False, indent=2))
    elif args.cmd == "iv":
        iv = implied_vol(args.spot, args.strike, args.days / 365.0, args.price, args.type)
        print(json.dumps({"implied_vol": round(iv, 4) if iv else None}, ensure_ascii=False))
    elif args.cmd == "strategy":
        print(json.dumps(analyze_strategy(parse_legs(args.legs), args.spot, args.iv),
                         ensure_ascii=False, indent=2))
    elif args.cmd == "status":
        legs = parse_legs(args.legs)
        res = analyze_strategy(legs, args.spot, args.iv)
        # 现价下各腿理论市值 → 浮动盈亏（entry: 收租为正/支出为负；P/L = entry + 结构现值）
        now_value = sum(d["bs_theoretical"] * (1 if l["direction"] == "buy" else -1)
                        for d, l in zip(res["legs"], legs))
        out = {
            "current_structure_value": round(now_value, 2),
            "entry": args.entry,
            "unrealized_pl": round((args.entry if args.entry else 0) + now_value, 2)
                             if args.entry is not None else None,
        }
        out["short_leg_delta_breach_030"] = res["short_leg_delta_breach_030"]
        out["short_leg_deltas"] = res["short_leg_deltas"]
        out["breakevens"] = res["breakevens"]
        out["days_to_expiry_min"] = min(l["days"] for l in legs)
        out["legs"] = res["legs"]
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
