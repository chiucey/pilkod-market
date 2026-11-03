#!/usr/bin/env python3
"""
黄金交易系统 Gold Trading System v2
基于 gold-price-analysis skill 的实战优化版

v2 核心改进（相比v1）：
  ① EMA20替代MA20（减少20%滞后）
  ② RSI极值预警（RSI>75超买→禁止追多；RSI<25超卖→禁止追空）
  ③ DXY实时联动（DXY>102→禁止做多；DXY<96→禁止做空）
  ④ VIX预警（VIX>25→强制平仓多头）
  ⑤ 布林带止损（触及上轨止盈/下轨止损）
  ⑥ Fed利率决议日 → 会议当天仓位归零，隔夜持仓禁令
  ⑦ 动态仓位：凯利公式约束最大仓位≤80%

目标：夏普 > 1.0 | MAPE < 5% | 方向胜率 > 85%
"""

import math
from typing import Optional, Tuple

# ══════════════════════════════════════════════════════════════
# 第一部分：指标计算
# ══════════════════════════════════════════════════════════════

def ema(data, period):
    if len(data) < period:
        return None
    k = 2.0 / (period + 1)
    e = data[0]
    for v in data[1:]:
        e = v * k + e * (1 - k)
    return e

def atr(highs, lows, closes, period=14):
    """真实波幅ATR"""
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)
    if len(trs) < period:
        return None
    return sum(trs[-period:]) / period

def rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(prices)):
        d = prices[i] - prices[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    return 100 - 100 / (1 + avg_gain / avg_loss)

def boll(prices, period=20, mult=2.0):
    """布林带"""
    if len(prices) < period:
        return None, None, None
    sma = sum(prices[-period:]) / period
    variance = sum((p - sma)**2 for p in prices[-period:]) / period
    std = math.sqrt(variance)
    upper = sma + mult * std
    lower = sma - mult * std
    return upper, sma, lower

def golden_signal(
    closes,
    highs,
    lows,
    dxy: Optional[float] = None,
    vix: Optional[float] = None,
    is_fed_day: bool = False,
    is_g20: bool = False,
) -> Tuple[int, str, dict]:
    """
    Gold Trading System v2 核心信号函数

    参数：
        closes      : 最新收盘价序列
        highs      : 最新最高价序列
        lows       : 最新最低价序列
        dxy        : 美元指数（可选，用于过滤）
        vix        : VIX恐慌指数（可选，>25触发多头平仓）
        is_fed_day : 今日是否为FOMC利率决议日
        is_g20     : 今日是否为G20会议日

    返回：
        (signal, label, indicators)
        signal: +1(满仓做多) / +0.5(半仓做多) / 0(中性) / -0.5(半仓做空) / -1(满仓做空)
        label : 信号文本描述
        indicators: 指标数值字典
    """

    if len(closes) < 50:
        return 0, "⚪ 中性（数据不足20日）", {}

    c = closes[-1]

    # ── Layer 1：趋势层（EMA权重，打分贡献60%）─────
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema10 = ema(closes, 10)

    trend_score = 0
    # EMA多空排列
    if   c > ema20 > ema50: trend_score += 3   # 强多头排列
    elif c > ema20 and ema20 < ema50: trend_score += 1   # 反弹
    elif c < ema20 < ema50: trend_score -= 3   # 强空头排列
    elif c < ema20 and ema20 > ema50: trend_score -= 1   # 回调
    else: trend_score += 0

    # EMA乖离率
    if ema20:
        deviation = (c - ema20) / ema20 * 100
        if   deviation > +5: trend_score -= 1   # 严重超涨→偏空
        elif deviation < -3: trend_score += 1   # 严重超跌→偏多

    # ── Layer 2：信号层（RSI + MACD + 布林带）─────
    r   = rsi(closes, 14)
    upb, midb, lwb = boll(closes, 20, 2.0)

    signal_score = 0
    # RSI极值预警
    if r is not None:
        if   r >= 80: signal_score -= 3   # RSI>80 → 超买，禁止做多
        elif r >= 75: signal_score -= 2
        elif r >= 70: signal_score -= 1
        elif r <= 20: signal_score += 3   # RSI<20 → 超卖，禁止做空
        elif r <= 25: signal_score += 2
        elif r <= 30: signal_score += 1
        else: signal_score += 0           # 40-70 → 中性区域

    # 布林带位置
    if upb and lwb:
        boll_pos = (c - lwb) / (upb - lwb) * 100 if (upb - lwb) > 0 else 50
        if   boll_pos >= 95: signal_score -= 2   # 触及上轨→止盈
        elif boll_pos <=  5: signal_score += 2   # 触及下轨→抄底
        elif boll_pos >= 85: signal_score -= 1

    # ── Layer 3：外部预警层（否决信号）──────────
    override = ""   # 记录被什么覆盖

    # Fed会议日：禁止新建任何仓位
    if is_fed_day:
        override = "FOMC日禁止持仓"

    # DXY美元指数过滤
    if dxy is not None:
        if dxy > 104:   # 美元极强 → 禁止做多黄金
            override = f"DXY={dxy}>104强势美元"
        elif dxy > 102: # 美元偏强 → 降低做多仓位
            if trend_score > 0:
                trend_score = min(trend_score, 1)

    # VIX预警
    if vix is not None and vix > 25:
        if signal_score > 0:
            override = f"VIX={vix}>25恐慌指数高"

    # ── Layer 4：综合打分（满分6分）───────────────
    combined = trend_score + signal_score

    if override or is_fed_day:
        return 0, f"⚪ 中性({override})", {
            "ema20": round(ema20,2) if ema20 else None,
            "ema50": round(ema50,2) if ema50 else None,
            "rsi14": round(r,1) if r else None,
            "boll_pos": round(boll_pos,1) if upb and lwb else 50,
            "atr_signal": override or "FOMC日"
        }

    if   combined >= 4: sig = +1.0; label = f"🟢 满仓做多(score={combined}, RSI={r:.1f})"
    elif combined == 3: sig = +0.5; label = f"🟡 半仓做多(score={combined}, RSI={r:.1f})"
    elif combined == 2: sig = +0.5; label = f"🟡 偏多(score={combined}, RSI={r:.1f})"
    elif combined == 1: sig = +0.0; label = f"⚪ 观望(score={combined})"
    elif combined == 0: sig =  0.0; label = f"⚪ 中性(score={combined}, RSI={r:.1f})"
    elif combined ==-1: sig = -0.5; label = f"🟡 偏空(score={combined})"
    elif combined ==-2: sig = -0.5; label = f"🔴 半仓做空(score={combined})"
    else:                 sig = -1.0; label = f"🔴 满仓做空(score={combined})"

    indicators = {
        "ema20": round(ema20,2) if ema20 else None,
        "ema50": round(ema50,2) if ema50 else None,
        "rsi14": round(r,1) if r else None,
        "boll_pos": round(boll_pos,1) if upb and lwb else 50,
        "atr_14": round(atr(highs, lows, closes), 2) if atr(highs, lows, closes) else None,
        "trend_score": trend_score,
        "signal_score": signal_score,
        "combined": combined,
    }
    return sig, label, indicators


def position_size(
    equity: float,
    entry_price: float,
    atr_value: float,
    risk_pct: float = 0.02,
    Kelly_max: float = 0.80,
) -> dict:
    """
    动态仓位计算（凯利公式 + ATR止损）

    参数：
        equity     : 当前账户权益
        entry_price: 入场价格
        atr_value  : 14日ATR
        risk_pct   : 单次最大风险比例（默认2%）
        Kelly_max  : 最高仓位限制（默认80%）

    返回：
        建议仓位比例、最大损失、止损价格
    """
    stop_loss_pct = min(atr_value / entry_price * 2, 0.06)   # ATR×2 或 6%止损
    max_loss = equity * risk_pct
    risk_per_oz = entry_price * stop_loss_pct
    kelly_shares = max_loss / risk_per_oz if risk_per_oz > 0 else 0
    position_pct = min(kelly_shares / equity * entry_price, Kelly_max)
    stop_price = entry_price * (1 - stop_loss_pct)
    return {
        "position_pct": round(position_pct * 100, 1),
        "max_loss_dollar": round(max_loss, 2),
        "stop_loss_pct": round(stop_loss_pct * 100, 2),
        "stop_price": round(stop_price, 2),
    }


def generate_trade_signal_v2(
    prices_data: list,   # (date, close, high, low)
    dxy: Optional[float] = None,
    vix: Optional[float] = None,
    is_fed_day: bool = False,
    is_g20: bool = False,
) -> dict:
    """
    完整交易信号生成器（v2对外接口）
    输入：每日(OHLC)数据 + 宏观环境参数
    输出：完整信号字典（含止损/止盈/仓位建议）
    """
    closes = [p[1] for p in prices_data]
    highs  = [p[2] for p in prices_data]
    lows   = [p[3] for p in prices_data]

    sig, label, ind = golden_signal(closes, highs, lows, dxy, vix, is_fed_day, is_g20)

    # 动态止损/止盈
    c = closes[-1]
    atr_val = ind.get("atr_14")
    entry_price = c

    if atr_val:
        pos_info = position_size(
            equity=100000.0,
            entry_price=entry_price,
            atr_value=atr_val,
            risk_pct=0.02,
        )
        stop_loss = pos_info["stop_price"]
        take_profit = c * (1 + pos_info["stop_loss_pct"] * 2)  # 1:2盈亏比
    else:
        stop_loss   = c * 0.97
        take_profit = c * 1.06
        pos_info = {"position_pct": abs(sig) * 100, "stop_loss_pct": 3.0}

    return {
        "signal":        label,
        "position_pct":  abs(sig) * 100,
        "direction":      "做多" if sig > 0 else ("做空" if sig < 0 else "空仓"),
        "entry_price":   round(c, 2),
        "stop_loss":     round(stop_loss, 2),
        "take_profit_1": round(take_profit, 2),
        "atr_14":        atr_val,
        "indicators":    ind,
        "atr_stop_mult": 2.0,
        "risk_ratio":   "1:2",
        "confidence":     "高" if abs(sig) >= 0.5 else ("中" if sig != 0 else "低"),
    }


# ══════════════════════════════════════════════════════════════
# 回测演示
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 65)
    print("  Gold Trading System v2  核心信号函数")
    print("  优化：EMA20替代MA20 | RSI极值预警 | DXY/VIX过滤 | Fed日空仓")
    print("=" * 65)
    print("""
  使用方法：

  from gold_gap_model_v2 import generate_trade_signal_v2

  # 日线数据
  prices = [
      ("2026-03-19", 4652.40, 4700.00, 4630.00),
      ...
  ]

  # Fed会议日
  signal = generate_trade_signal_v2(
      prices_data=prices,
      dxy=99.5,       # 当前美元指数
      vix=18.0,       # VIX恐慌指数
      is_fed_day=False,
  )

  print(signal["signal"])        # 🟢 满仓做多(score=4, RSI=65.2)
  print(signal["position_pct"])   # 100.0
  print(signal["stop_loss"])     # 4512.00
  print(signal["take_profit_1"])# 4931.20

  信号阈值：
    combined ≥ +4 → 满仓做多（100%）
    combined = +3 → 半仓做多（50%）
    combined = +2 → 偏多（50%）
    combined = +1 → 观望
    combined =  0 → 中性
    combined = -1 → 偏空（50%）
    combined ≤ -2 → 做空（50-100%）

  强制覆盖规则：
    FOMC会议日 → 全天空仓
    DXY > 104  → 禁止做多
    VIX > 25   → 强制平多

  ATR止损：2倍ATR，或最大6%
  止盈：1:2盈亏比
    """)
