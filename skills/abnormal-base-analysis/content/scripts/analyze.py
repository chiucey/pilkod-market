#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股异动底仓分析工具

分析某日涨幅>=10%的A股，追溯其异动底仓（主力建仓）集中在日线的哪个时间段。

分析维度:
1. 底仓集群检测: 成交量异常放大的连续交易日集群
2. 缩量调整检测: 底仓后的缩量整理期
3. 三阳控三阴: 底仓区间阳量是否控制阴量（来源：股是股非）
4. 冰点量检测: 缩量末端成交量是否萎缩至极低（来源：股是股非）
5. 好位置评估: 底仓是否在均线归位、支撑位上方的有利位置（来源：股是股非）
6. 洗盘模式分类: 不破而立/先破而后立/大洗/小洗（来源：股是股非）

用法:
    python analyze.py [--date YYYY-MM-DD] [--output json|text|html]

示例:
    python analyze.py
    python analyze.py --output html
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ============================================================
# 配置
# ============================================================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
REFERER = "https://data.eastmoney.com/"
REQUEST_DELAY = 0.5

# 成交量异常阈值（相对60日均量）
VOLUME_SPIKE_THRESHOLD = 1.3
VOLUME_CONTRACTION_THRESHOLD = 0.7
MIN_CLUSTER_DAYS = 2
LOOKBACK_DAYS = 100  # 取100天K线保证60日均量计算

# --- 新增：股是股非量价分析参数 ---
# 冰点量
ICE_VOLUME_RATIO = 0.3          # 缩量期成交量低于均量30% = 冰点
SUDDEN_ICE_RATIO = 0.3         # 底仓结束后骤然萎缩至底仓均量30%以下 = 骤然极冰
# 三阳控三阴
YANG_YIN_RATIO = 1.5           # 阳量总和 / 阴量总和 > 1.5 = 合格
# 好位置
MA_ALIGNMENT_RATIO = 0.05      # 收盘价在MA60±5%内视为均线归位
SUPPORT_LOOKBACK = 20          # 支撑位回溯天数
# 洗盘模式
WASHOUT_BIG_DAYS = 10          # 缩量>10天 = 大洗
WASHOUT_SMALL_DAYS = 3         # 缩量>=3天 = 小洗


# ============================================================
# 数据获取
# ============================================================

def _build_secid(code: str) -> str:
    code = code.strip()
    if code.startswith(("60", "68")):
        return f"1.{code}"
    return f"0.{code}"


def _http_get(url: str) -> dict:
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Referer", REFERER)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except Exception as e:
            if attempt == 4:
                raise
            time.sleep(3 + attempt * 2)
    return {}


def fetch_all_stocks() -> list[dict]:
    """获取全量A股列表（含实时涨跌幅）"""
    all_stocks = []
    page = 1
    while True:
        url = (
            "https://push2delay.eastmoney.com/api/qt/clist/get?"
            f"pn={page}&pz=100&po=1&np=1&fltt=2&invt=2"
            "&fid=f3"
            "&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
            "&fields=f2,f3,f12,f14,f5,f8,f20"
        )
        data = _http_get(url)
        if not data or "data" not in data:
            break
        items = data["data"].get("diff") or []
        for item in items:
            try:
                pct = float(item.get("f3") or 0)
            except (ValueError, TypeError):
                pct = 0.0
            all_stocks.append({
                "code": str(item.get("f12", "")),
                "name": str(item.get("f14", "")),
                "pct_change": pct,
            })
        total = data["data"].get("total", 0)
        sys.stderr.write(f"\r  加载股票列表... {len(all_stocks)}/{total}")
        sys.stderr.flush()
        if page * 100 >= total or len(items) < 100:
            break
        page += 1
        time.sleep(0.2)
    sys.stderr.write("\n")
    return all_stocks


def filter_top_gainers(
    all_stocks: list[dict],
    threshold: float,
    max_stocks: int = 0,
) -> list[dict]:
    """从全量列表中筛选涨幅>=threshold的股票"""
    gainers = [s for s in all_stocks if s["pct_change"] >= threshold]
    gainers.sort(key=lambda x: x["pct_change"], reverse=True)
    if max_stocks > 0 and len(gainers) > max_stocks:
        gainers = gainers[:max_stocks]
    return gainers


def fetch_daily_kline(code: str, end_date: str = None) -> list[dict]:
    """获取个股日K线数据。优先东财（快），失败后走新浪（慢但稳定）。"""
    # 先尝试东财（快速失败）
    secid = _build_secid(code)
    url = (
        "https://push2his.eastmoney.com/api/qt/stock/kline/get?"
        f"secid={secid}&klt=101&fqt=1"
        "&fields1=f1,f2,f3,f4,f5,f6"
        "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
        f"&end=20500101&lmt={LOOKBACK_DAYS}"
    )
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", USER_AGENT)
        req.add_header("Referer", "https://quote.eastmoney.com/")
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
        if data and "data" in data:
            klines_raw = data["data"].get("klines") or []
            if klines_raw:
                result = []
                for line in klines_raw:
                    parts = line.split(",")
                    if len(parts) < 11:
                        continue
                    result.append({
                        "date": parts[0], "open": float(parts[1]),
                        "close": float(parts[2]), "high": float(parts[3]),
                        "low": float(parts[4]), "volume": float(parts[5]),
                        "amount": float(parts[6]), "amplitude": float(parts[7]),
                        "pct_change": float(parts[8]),
                        "change_amount": float(parts[9]),
                        "turnover_rate": float(parts[10]),
                    })
                return result
    except Exception:
        pass

    # 回退到新浪财经日K线
    if code.startswith(("60", "68")):
        symbol = f"sh{code}"
    else:
        symbol = f"sz{code}"
    url = (
        "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
        f"CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no"
        f"&datalen={LOOKBACK_DAYS + 5}"
    )
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Referer", "https://finance.sina.com.cn/")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("gbk", errors="replace")
                break
        except Exception:
            if attempt == 2:
                return []
            time.sleep(1)
    if not raw:
        return []
    try:
        raw_data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    result = []
    for d in raw_data:
        try:
            o = float(d["open"]); h = float(d["high"])
            l = float(d["low"]); c = float(d["close"])
            result.append({
                "date": d["day"], "open": o, "close": c,
                "high": h, "low": l, "volume": float(d["volume"]),
                "amount": 0,
                "amplitude": abs(h - l) / o * 100 if o > 0 else 0,
                "pct_change": 0, "change_amount": 0, "turnover_rate": 0,
            })
        except (KeyError, ValueError):
            continue
    return result


# ============================================================
# 基础量化分析
# ============================================================

def calc_volume_ma(klines: list[dict], window: int = 60) -> list[float]:
    volumes = [k["volume"] for k in klines]
    ma = []
    for i in range(len(volumes)):
        start = max(0, i - window + 1)
        avg = sum(volumes[start:i + 1]) / (i - start + 1)
        ma.append(avg)
    return ma


def calc_price_ma(klines: list[dict], window: int = 60) -> list[float]:
    """计算收盘价移动均线"""
    closes = [k["close"] for k in klines]
    ma = []
    for i in range(len(closes)):
        start = max(0, i - window + 1)
        avg = sum(closes[start:i + 1]) / (i - start + 1)
        ma.append(avg)
    return ma


def calc_price_ma_90(klines: list[dict]) -> list[float]:
    """计算90日均线"""
    return calc_price_ma(klines, 90)


def find_volume_clusters(
    klines: list[dict],
    vol_ma60: list[float],
    breakout_idx: int,
) -> list[dict]:
    """在爆发日之前寻找成交量异常放大的集群"""
    clusters = []
    i = breakout_idx - 1
    while i >= 0:
        if klines[i]["volume"] >= vol_ma60[i] * VOLUME_SPIKE_THRESHOLD:
            cluster_start = i
            cluster_end = i
            cluster_volumes = [klines[i]["volume"]]
            cluster_vol_ratios = [
                klines[i]["volume"] / vol_ma60[i] if vol_ma60[i] > 0 else 1
            ]
            j = i - 1
            while j >= 0:
                vol_ratio = klines[j]["volume"] / vol_ma60[j] if vol_ma60[j] > 0 else 1
                if vol_ratio >= VOLUME_SPIKE_THRESHOLD:
                    cluster_start = j
                    cluster_volumes.insert(0, klines[j]["volume"])
                    cluster_vol_ratios.insert(0, vol_ratio)
                    j -= 1
                elif vol_ratio >= VOLUME_SPIKE_THRESHOLD - 0.2:
                    cluster_start = j
                    cluster_volumes.insert(0, klines[j]["volume"])
                    cluster_vol_ratios.insert(0, vol_ratio)
                    j -= 1
                else:
                    break

            cluster_days = cluster_end - cluster_start + 1
            if cluster_days >= MIN_CLUSTER_DAYS:
                avg_ratio = sum(cluster_vol_ratios) / len(cluster_vol_ratios)
                max_ratio = max(cluster_vol_ratios)
                start_close = klines[cluster_start]["close"]
                end_close = klines[cluster_end]["close"]
                price_change = (
                    (end_close - start_close) / start_close * 100
                    if start_close > 0 else 0
                )

                # 计算底仓区间最低价（用于后续洗盘分类）
                cluster_low = min(
                    klines[k]["low"] for k in range(cluster_start, cluster_end + 1)
                )

                clusters.append({
                    "start_idx": cluster_start,
                    "end_idx": cluster_end,
                    "start_date": klines[cluster_start]["date"],
                    "end_date": klines[cluster_end]["date"],
                    "days": cluster_days,
                    "avg_vol_ratio": round(avg_ratio, 2),
                    "max_vol_ratio": round(max_ratio, 2),
                    "price_change_pct": round(price_change, 2),
                    "highest_turnover": max(
                        klines[k]["turnover_rate"]
                        for k in range(cluster_start, cluster_end + 1)
                    ),
                    "cluster_low": cluster_low,
                })
            i = cluster_start - 1
        else:
            i -= 1
    return clusters


def analyze_contraction(
    klines: list[dict],
    vol_ma60: list[float],
    cluster: dict,
    breakout_idx: int,
) -> dict:
    contraction_start = cluster["end_idx"] + 1
    contraction_end = breakout_idx - 1
    if contraction_start > contraction_end:
        return {"has_contraction": False, "contraction_days": 0, "avg_vol_ratio": 0}

    ratios = []
    for i in range(contraction_start, contraction_end + 1):
        if vol_ma60[i] > 0:
            ratios.append(klines[i]["volume"] / vol_ma60[i])

    if not ratios:
        return {"has_contraction": False, "contraction_days": 0, "avg_vol_ratio": 0}

    avg_ratio = sum(ratios) / len(ratios)
    days = contraction_end - contraction_start + 1

    # 计算缩量区间最低价
    contraction_low = min(
        klines[k]["low"] for k in range(contraction_start, contraction_end + 1)
    )

    return {
        "has_contraction": True,
        "contraction_days": days,
        "start_date": klines[contraction_start]["date"],
        "end_date": klines[contraction_end]["date"],
        "avg_vol_ratio": round(avg_ratio, 2),
        "is_typical": avg_ratio <= VOLUME_CONTRACTION_THRESHOLD,
        "contraction_low": contraction_low,
    }


# ============================================================
# 新增维度一：冰点量检测（来源：股是股非）
# ============================================================

def detect_ice_volume(
    klines: list[dict],
    vol_ma60: list[float],
    cluster: dict,
    contraction: dict,
) -> dict:
    """
    检测缩量调整末端的冰点量信号。

    信号1 - 冰点量: 缩量调整期内有某日成交量 < MA60 * ICE_VOLUME_RATIO（即萎缩至均量30%以下）
    信号2 - 骤然极冰: 底仓结束后，第一根阴量的量能骤降至底仓均量30%以下

    返回:
        has_ice: 是否检测到冰点量
        has_sudden_ice: 是否检测到骤然极冰
        ice_date: 冰点量日期(如有)
        ice_ratio: 冰点量/均量比值
        description: 中文描述
    """
    result = {
        "has_ice": False,
        "has_sudden_ice": False,
        "ice_date": None,
        "ice_ratio": 0.0,
        "description": "",
    }

    # 1. 冰点量检测：遍历缩量调整期
    if contraction.get("has_contraction"):
        # 通过日期定位缩量区间索引
        start_date = contraction["start_date"]
        end_date = contraction["end_date"]
        min_ratio = float("inf")
        min_date = None
        for i, k in enumerate(klines):
            if start_date <= k["date"] <= end_date:
                if vol_ma60[i] > 0:
                    ratio = k["volume"] / vol_ma60[i]
                    if ratio < min_ratio:
                        min_ratio = ratio
                        min_date = k["date"]

        if min_ratio <= ICE_VOLUME_RATIO:
            result["has_ice"] = True
            result["ice_date"] = min_date
            result["ice_ratio"] = round(min_ratio, 2)
            result["description"] = f"冰点量({min_date}, 均量比{min_ratio:.2f}x)"

    # 2. 骤然极冰检测：底仓结束后第一根缩量K线的量能
    cluster_end_idx = cluster["end_idx"]
    if cluster_end_idx + 1 < len(klines):
        # 计算底仓区间日均量
        cluster_volumes = [
            klines[k]["volume"]
            for k in range(cluster["start_idx"], cluster_end_idx + 1)
        ]
        cluster_avg_vol = sum(cluster_volumes) / len(cluster_volumes) if cluster_volumes else 1

        # 底仓后第一根
        first_after = klines[cluster_end_idx + 1]
        if cluster_avg_vol > 0 and first_after["volume"] / cluster_avg_vol <= SUDDEN_ICE_RATIO:
            # 确认是阴线（收盘 < 开盘）
            if first_after["close"] < first_after["open"]:
                result["has_sudden_ice"] = True
                if not result["description"]:
                    result["description"] = "骤然极冰(底仓后首阴骤缩)"

    # 合并描述
    if result["has_ice"] and result["has_sudden_ice"]:
        result["description"] = f"冰点量+骤然极冰({result['ice_date']})"
    elif result["has_ice"]:
        pass  # already set
    elif result["has_sudden_ice"]:
        result["description"] = "骤然极冰(底仓后首阴骤缩)"

    return result


# ============================================================
# 新增维度二：好位置评估（来源：股是股非）
# ============================================================

def assess_position_quality(
    klines: list[dict],
    cluster: dict,
    price_ma60: list[float],
    price_ma90: list[float],
) -> dict:
    """
    评估底仓所在位置是否有利。

    信号1 - 均线归位: 底仓起始日收盘价在MA60±5%范围内
    信号2 - 支撑位: 底仓起始价在近20日最低价上方
    信号3 - 90日均线趋势: 上行/走平/下行

    返回:
        ma_aligned: 均线是否归位
        above_support: 是否在支撑位上方
        ma90_trend: 90日均线趋势
        description: 中文描述
        score_bonus: 加分项列表
    """
    cluster_start_idx = cluster["start_idx"]

    result = {
        "ma_aligned": False,
        "above_support": False,
        "ma90_trend": "未知",
        "description": "",
        "score_details": [],
    }

    # 1. 均线归位检测
    if cluster_start_idx < len(price_ma60):
        ma60_val = price_ma60[cluster_start_idx]
        close_val = klines[cluster_start_idx]["close"]
        if ma60_val > 0:
            deviation = abs(close_val - ma60_val) / ma60_val
            if deviation <= MA_ALIGNMENT_RATIO:
                result["ma_aligned"] = True
                result["score_details"].append("均线归位(+5)")
            # 也检查收盘价是否在MA60上方（更强势）
            elif close_val > ma60_val and deviation <= MA_ALIGNMENT_RATIO * 4:
                result["ma_aligned"] = True  # 在均线上方不远处也算归位
                result["score_details"].append("均线上方归位(+3)")

    # 2. 支撑位检测
    lookback_start = max(0, cluster_start_idx - SUPPORT_LOOKBACK)
    recent_lows = [klines[k]["low"] for k in range(lookback_start, cluster_start_idx)]
    if recent_lows:
        support_low = min(recent_lows)
        if klines[cluster_start_idx]["close"] > support_low:
            result["above_support"] = True
            result["score_details"].append("支撑位上方(+5)")

    # 3. 90日均线趋势
    if cluster_start_idx >= 30 and cluster_start_idx < len(price_ma90):
        ma90_current = price_ma90[cluster_start_idx]
        ma90_30ago = price_ma90[max(0, cluster_start_idx - 30)]
        if ma90_30ago > 0:
            trend_pct = (ma90_current - ma90_30ago) / ma90_30ago * 100
            if trend_pct > 1:
                result["ma90_trend"] = "上行"
            elif trend_pct > -1:
                result["ma90_trend"] = "走平"
            else:
                result["ma90_trend"] = "下行"

    # 生成描述
    parts = []
    if result["ma_aligned"]:
        parts.append("均线归位")
    if result["above_support"]:
        parts.append("支撑位上方")
    if result["ma90_trend"] != "未知":
        parts.append(f"MA90{result['ma90_trend']}")
    result["description"] = "、".join(parts) if parts else "位置一般"

    return result


# ============================================================
# 新增维度三：三阳控三阴量态分析（来源：股是股非）
# ============================================================

def analyze_yang_yin_volume(
    klines: list[dict],
    cluster: dict,
) -> dict:
    """
    统计底仓集群内阳量 vs 阴量的关系。

    阳量: 收盘>开盘的交易日成交量之和
    阴量: 收盘<开盘的交易日成交量之和
    三阳控三阴: 阳量 > 1.5 * 阴量

    返回:
        yang_vol_sum: 阳量总和
        yin_vol_sum: 阴量总和
        ratio: 阳量/阴量比值
        is_qualified: 是否三阳控三阴
        description: 中文描述
    """
    start_idx = cluster["start_idx"]
    end_idx = cluster["end_idx"]

    yang_vol = 0.0
    yin_vol = 0.0
    yang_days = 0
    yin_days = 0

    for i in range(start_idx, end_idx + 1):
        k = klines[i]
        if k["close"] > k["open"]:
            yang_vol += k["volume"]
            yang_days += 1
        elif k["close"] < k["open"]:
            yin_vol += k["volume"]
            yin_days += 1

    if yin_vol == 0:
        ratio = 999 if yang_vol > 0 else 1
    else:
        ratio = yang_vol / yin_vol

    is_qualified = ratio >= YANG_YIN_RATIO

    if is_qualified:
        desc = f"三阳控三阴(阳量{ratio:.1f}x阴量, 阳{yang_days}天阴{yin_days}天)"
    else:
        desc = f"量态偏弱(阳量{ratio:.1f}x阴量)"

    return {
        "yang_vol_sum": round(yang_vol, 0),
        "yin_vol_sum": round(yin_vol, 0),
        "yang_days": yang_days,
        "yin_days": yin_days,
        "ratio": round(ratio, 2),
        "is_qualified": is_qualified,
        "description": desc,
    }


# ============================================================
# 新增维度四：洗盘模式分类（来源：股是股非）
# ============================================================

def classify_washout_pattern(
    klines: list[dict],
    cluster: dict,
    contraction: dict,
    breakout_idx: int,
) -> dict:
    """
    对缩量调整期进行洗盘模式分类。

    模式1 - 不破而立: 缩量调整期最低价 >= 底仓区最低价（没破底仓）
    模式2 - 先破而后立: 缩量调整期最低价 < 底仓区最低价，但爆发日收盘回升
    洗盘规模:
      大洗: 缩量天数 > 10天
      小洗: 缩量天数 3~10天
      微型洗: 缩量天数 < 3天

    返回:
        pattern: 洗盘模式名称
        scale: 洗盘规模
        description: 中文描述
    """
    if not contraction.get("has_contraction"):
        return {
            "pattern": "无洗盘",
            "scale": "直接爆发",
            "description": "底仓后直接爆发，无缩量洗盘",
        }

    cluster_low = cluster.get("cluster_low", 0)
    contraction_low = contraction.get("contraction_low", 0)
    contraction_days = contraction["contraction_days"]

    # 判断模式
    if contraction_low >= cluster_low:
        pattern = "不破而立"
        pattern_desc = "缩量未破底仓最低价"
    else:
        pattern = "先破而后立"
        pattern_desc = "缩量跌破底仓最低价后止跌"

    # 判断规模
    if contraction_days > WASHOUT_BIG_DAYS:
        scale = "大洗"
        scale_desc = f"缩量{contraction_days}天(>10天)"
    elif contraction_days >= WASHOUT_SMALL_DAYS:
        scale = "小洗"
        scale_desc = f"缩量{contraction_days}天(3~10天)"
    else:
        scale = "微型洗"
        scale_desc = f"缩量{contraction_days}天(<3天)"

    return {
        "pattern": pattern,
        "scale": scale,
        "pattern_detail": pattern_desc,
        "contraction_days": contraction_days,
        "cluster_low": round(cluster_low, 2),
        "contraction_low": round(contraction_low, 2),
        "description": f"{pattern} · {scale}（{scale_desc}, {pattern_desc}）",
    }


# ============================================================
# 综合评分（整合全部维度）
# ============================================================

def score_cluster(
    cluster: dict,
    contraction: dict,
    distance: int,
    ice_volume: dict,
    position: dict,
    yang_yin: dict,
    washout: dict,
) -> float:
    """
    综合评分，整合基础维度+股是股非新增维度。

    评分体系:
    - 放量强度 (15分)
    - 集群天数 (10分)
    - 距爆发日距离 (15分)
    - 缩量质量 (10分)
    - 价格温和度 (5分)
    - 三阳控三阴 (10分) — 新增
    - 冰点量检测 (15分) — 新增
    - 好位置评估 (10分) — 新增
    - 洗盘模式 (10分) — 新增
    满分: 100分
    """
    score = 0.0
    details = []

    # 1. 放量强度 (15)
    r = cluster["avg_vol_ratio"]
    if r >= 3.0:
        score += 15; details.append("放量强度+15(>=3x)")
    elif r >= 2.0:
        score += 12; details.append("放量强度+12(>=2x)")
    elif r >= 1.5:
        score += 9; details.append("放量强度+9(>=1.5x)")
    else:
        score += 5; details.append("放量强度+5(<1.5x)")

    # 2. 集群天数 (10)
    d = cluster["days"]
    if 3 <= d <= 8:
        score += 10; details.append(f"集群天数+10({d}天)")
    elif 2 <= d <= 10:
        score += 7; details.append(f"集群天数+7({d}天)")
    else:
        score += 3; details.append(f"集群天数+3({d}天)")

    # 3. 距爆发日距离 (15)
    if 1 <= distance <= 5:
        score += 15; details.append("距离+15(1-5天)")
    elif 6 <= distance <= 15:
        score += 12; details.append("距离+12(6-15天)")
    elif 16 <= distance <= 30:
        score += 8; details.append("距离+8(16-30天)")
    else:
        score += 3; details.append("距离+3(>30天)")

    # 4. 缩量质量 (10)
    if contraction["has_contraction"]:
        cr = contraction["avg_vol_ratio"]
        if cr <= 0.5:
            score += 10; details.append("缩量质量+10(<=0.5x)")
        elif cr <= 0.7:
            score += 7; details.append("缩量质量+7(<=0.7x)")
        elif cr <= 0.9:
            score += 4; details.append("缩量质量+4(<=0.9x)")
        else:
            score += 2; details.append("缩量质量+2(>0.9x)")

    # 5. 价格变化 (5)
    ap = abs(cluster["price_change_pct"])
    if ap <= 5:
        score += 5; details.append("价格温和+5")
    elif ap <= 10:
        score += 3; details.append("价格温和+3")
    else:
        score += 1; details.append("价格温和+1")

    # === 新增维度 ===

    # 6. 三阳控三阴 (10)
    if yang_yin["is_qualified"]:
        extra = 10 if yang_yin["ratio"] >= 2.0 else 7
        score += extra; details.append(f"三阳控三阴+{extra}(阳量{yang_yin['ratio']:.1f}x)")
    elif yang_yin["ratio"] >= 1.0:
        score += 3; details.append(f"量态均衡+3")
    # ratio < 1.0 → 不加分

    # 7. 冰点量检测 (15)
    ice_bonus = 0
    if ice_volume["has_ice"]:
        ice_bonus += 8
    if ice_volume["has_sudden_ice"]:
        ice_bonus += 7
    if ice_bonus > 0:
        score += ice_bonus; details.append(f"冰点量+{ice_bonus}")

    # 8. 好位置评估 (10)
    pos_bonus = 0
    if position["ma_aligned"]:
        pos_bonus += 5
    if position["above_support"]:
        pos_bonus += 5
    if pos_bonus > 0:
        score += pos_bonus; details.append(f"好位置+{pos_bonus}")

    # 9. 洗盘模式 (10)
    washout_bonus = 0
    if washout["pattern"] == "不破而立":
        washout_bonus += 6
    elif washout["pattern"] == "先破而后立":
        washout_bonus += 3
    if washout["scale"] == "大洗":
        washout_bonus += 4
    elif washout["scale"] == "小洗":
        washout_bonus += 2
    if washout_bonus > 0:
        score += washout_bonus; details.append(f"洗盘模式+{washout_bonus}({washout['pattern']})")

    return round(score, 1)


# ============================================================
# 单只股票综合分析
# ============================================================

def analyze_stock(stock: dict) -> dict:
    """对单只股票进行完整的底仓分析"""
    code = stock["code"]
    name = stock["name"]
    pct_change = stock["pct_change"]

    klines = fetch_daily_kline(code)
    if len(klines) < 30:
        return {"code": code, "name": name, "pct_change": pct_change,
                "error": f"K线数据不足（仅{len(klines)}条）"}

    vol_ma60 = calc_volume_ma(klines, 60)
    price_ma60 = calc_price_ma(klines, 60)
    price_ma90 = calc_price_ma_90(klines)
    breakout_idx = len(klines) - 1

    clusters = find_volume_clusters(klines, vol_ma60, breakout_idx)
    if not clusters:
        return {
            "code": code, "name": name, "pct_change": pct_change,
            "breakout_date": klines[breakout_idx]["date"],
            "vol_ma60_latest": int(vol_ma60[-1]) if vol_ma60 else 0,
            "error": "未检测到明显底仓集群",
        }

    analyzed = []
    for c in clusters:
        distance = breakout_idx - c["end_idx"]
        contraction = analyze_contraction(klines, vol_ma60, c, breakout_idx)

        # 新增维度分析
        ice_volume = detect_ice_volume(klines, vol_ma60, c, contraction)
        position = assess_position_quality(klines, c, price_ma60, price_ma90)
        yang_yin = analyze_yang_yin_volume(klines, c)
        washout = classify_washout_pattern(klines, c, contraction, breakout_idx)

        s = score_cluster(c, contraction, distance, ice_volume, position, yang_yin, washout)
        analyzed.append({
            **c,
            "distance_to_breakout": distance,
            "contraction": contraction,
            "ice_volume": ice_volume,
            "position": position,
            "yang_yin": yang_yin,
            "washout": washout,
            "confidence_score": s,
        })

    analyzed.sort(key=lambda x: x["confidence_score"], reverse=True)
    best = analyzed[0]

    return {
        "code": code, "name": name, "pct_change": pct_change,
        "breakout_date": klines[breakout_idx]["date"],
        "breakout_volume": int(klines[breakout_idx]["volume"]),
        "breakout_turnover": klines[breakout_idx]["turnover_rate"],
        "breakout_close": klines[breakout_idx]["close"],
        "vol_ma60_latest": int(vol_ma60[-1]) if vol_ma60 else 0,
        "total_clusters_found": len(analyzed),
        "primary_base": {
            "start_date": best["start_date"],
            "end_date": best["end_date"],
            "days": best["days"],
            "avg_vol_ratio": best["avg_vol_ratio"],
            "max_vol_ratio": best["max_vol_ratio"],
            "price_change_pct": best["price_change_pct"],
            "highest_turnover": best["highest_turnover"],
            "confidence_score": best["confidence_score"],
            "contraction": best["contraction"],
            "ice_volume": best["ice_volume"],
            "position": best["position"],
            "yang_yin": best["yang_yin"],
            "washout": best["washout"],
        },
        "all_clusters": [
            {"start_date": c["start_date"], "end_date": c["end_date"],
             "days": c["days"], "avg_vol_ratio": c["avg_vol_ratio"],
             "confidence_score": c["confidence_score"],
             "contraction_days": c["contraction"]["contraction_days"]}
            for c in analyzed
        ],
    }


# ============================================================
# 时间段分类
# ============================================================

TIME_RANGES = {
    "A": ("2026-05-06", "2026-05-13", "5月6日 -> 5月13日"),
    "B": ("2026-05-14", "2026-05-20", "5月14日 -> 5月20日"),
    "C": ("2026-05-21", "2026-05-28", "5月21日 -> 5月28日"),
    "D": ("2026-05-29", "2026-06-04", "5月29日 -> 6月4日"),
}


def classify_time_range(base_start: str, base_end: str) -> str:
    """将底仓区间归入对应时间段。按底仓起始日期判定。"""
    for label, (rs, re, _desc) in TIME_RANGES.items():
        if rs <= base_start <= re or rs <= base_end <= re:
            return label
    # 检查是否跨越多个区间，取起始日期所在的区间
    for label, (rs, re, _desc) in TIME_RANGES.items():
        if base_start <= re and base_end >= rs:
            return label
    return "其他"


def build_range_summary(results: list[dict]) -> dict:
    """统计各时间段的底仓分布"""
    valid = [r for r in results if "primary_base" in r]
    summary = {}
    for label, (rs, re, desc) in TIME_RANGES.items():
        summary[label] = {"desc": desc, "stocks": [], "count": 0,
                          "avg_confidence": 0.0, "avg_vol_ratio": 0.0}
    summary["其他"] = {"desc": "不在上述范围内", "stocks": [], "count": 0,
                       "avg_confidence": 0.0, "avg_vol_ratio": 0.0}

    for s in valid:
        pb = s["primary_base"]
        rng = classify_time_range(pb["start_date"], pb["end_date"])
        if rng not in summary:
            rng = "其他"
        entry = {"name": s["name"], "code": s["code"], "pct": s["pct_change"],
                 "base_start": pb["start_date"], "base_end": pb["end_date"],
                 "days": pb["days"], "confidence": pb["confidence_score"],
                 "avg_vol_ratio": pb["avg_vol_ratio"]}
        summary[rng]["stocks"].append(entry)
        summary[rng]["count"] += 1

    for rng in summary:
        stocks = summary[rng]["stocks"]
        if stocks:
            summary[rng]["avg_confidence"] = round(
                sum(s["confidence"] for s in stocks) / len(stocks), 1)
            summary[rng]["avg_vol_ratio"] = round(
                sum(s["avg_vol_ratio"] for s in stocks) / len(stocks), 2)

    return summary


def format_range_text(results: list[dict]) -> str:
    """输出时间段分布文字报告"""
    summary = build_range_summary(results)
    total = sum(v["count"] for v in summary.values())
    lines = ["\n" + "=" * 80, "  底仓时间段分布统计", "=" * 80]
    sorted_items = sorted(summary.items(), key=lambda x: x[1]["count"], reverse=True)
    abcd = [(l, i) for l, i in summary.items() if l in "ABCD"]
    max_label = max(abcd, key=lambda x: x[1]["count"])[0] if abcd else (sorted_items[0][0] if sorted_items else "?")
    for label, info in sorted_items:
        if label == "其他" and info["count"] == 0:
            continue
        marker = "★" if label == max_label else " "
        lines.append(f"\n  {marker} [{label}] {info['desc']}")
        lines.append(f"      底仓集中于此的股票: {info['count']} 只 (占 {info['count']/total*100:.1f}%)" if total > 0 else "")
        lines.append(f"      平均置信度: {info['avg_confidence']}  平均均量比: {info['avg_vol_ratio']}x")
        for s_ in info["stocks"][:8]:
            lines.append(f"        {s_['name']}({s_['code']}) 涨幅{s_['pct']:.1f}%  底仓{s_['base_start']}->{s_['base_end']}  置信度{s_['confidence']}")
        if len(info["stocks"]) > 8:
            lines.append(f"        ...共 {len(info['stocks'])} 只")
    lines.append(f"\n{'=' * 80}")
    lines.append(f"  ★ 结论: 异动底仓最集中的时间段是 {sorted_items[0][0]} 段: {summary[sorted_items[0][0]]['desc']}")
    return "\n".join(lines)


# ============================================================
# 输出格式化
# ============================================================

def format_text(results: list[dict]) -> str:
    lines = ["=" * 80, "  A股异动底仓分析报告", "=" * 80]
    valid = [r for r in results if "primary_base" in r]
    errors = [r for r in results if "error" in r]
    lines.append(f"\n  总计涨幅>=10%股票: {len(results)} 只")
    lines.append(f"  检测到底仓: {len(valid)} 只")
    lines.append(f"  未检测到底仓或异常: {len(errors)} 只")

    for i, s in enumerate(valid, 1):
        pb = s["primary_base"]
        ct = pb["contraction"]
        iv = pb.get("ice_volume", {})
        pos = pb.get("position", {})
        yy = pb.get("yang_yin", {})
        wo = pb.get("washout", {})

        lines.append(f"\n{'─' * 80}")
        lines.append(f"  [{i}] {s['name']}（{s['code']}） 涨幅: {s['pct_change']:.2f}%")
        lines.append(f"      爆发日: {s['breakout_date']}  收盘: {s['breakout_close']}  换手: {s['breakout_turnover']:.2f}%")
        lines.append(f"      爆发日成交量: {s['breakout_volume']:,}手  60日均量: {s['vol_ma60_latest']:,}手")
        lines.append(f"")
        lines.append(f"  【底仓分析】 置信度: {pb['confidence_score']}/100")
        lines.append(f"    底仓建立: {pb['start_date']} -> {pb['end_date']}（{pb['days']}个交易日）")
        lines.append(f"    区间涨跌: {pb['price_change_pct']:+.2f}%  均量比: {pb['avg_vol_ratio']}x  最大放量: {pb['max_vol_ratio']}x")
        lines.append(f"    最高换手率: {pb['highest_turnover']:.2f}%")

        # 三阳控三阴
        if yy:
            lines.append(f"  【三阳控三阴】 {yy.get('description', '')}")

        if ct["has_contraction"]:
            lines.append(f"  【缩量调整】")
            lines.append(f"    {ct['start_date']} -> {ct['end_date']}（{ct['contraction_days']}天）")
            lines.append(f"    均量比: {ct['avg_vol_ratio']}x  {'[典型缩量整理]' if ct['is_typical'] else '[缩量不够充分]'}")
        else:
            lines.append(f"  【缩量调整】 无（底仓直接爆发）")

        # 洗盘模式
        if wo:
            lines.append(f"  【洗盘模式】 {wo.get('description', '')}")

        # 冰点量
        if iv and (iv.get("has_ice") or iv.get("has_sudden_ice")):
            lines.append(f"  【冰点量】 {iv.get('description', '')}")

        # 好位置
        if pos and pos.get("description"):
            lines.append(f"  【好位置】 {pos['description']}")

        if s["total_clusters_found"] > 1:
            lines.append(f"\n  【其他可疑集群】")
            for c in s["all_clusters"][1:]:
                lines.append(f"    {c['start_date']}->{c['end_date']} ({c['days']}天, 均量{c['avg_vol_ratio']}x, 评分{c['confidence_score']})")

    if errors:
        lines.append(f"\n{'─' * 80}")
        lines.append(f"  数据异常/未检测到底仓:")
        for e in errors:
            lines.append(f"    {e['name']}（{e['code']}）: {e['error']}")
    lines.append(f"\n{'=' * 80}")
    return "\n".join(lines)


def format_json(results: list[dict]) -> str:
    valid = [r for r in results if "primary_base" in r]
    errors = [r for r in results if "error" in r]
    summary = build_range_summary(results)
    return json.dumps({
        "total": len(results),
        "with_base": len(valid),
        "errors": len(errors),
        "stocks": valid,
        "error_stocks": errors,
        "time_range_distribution": {
            label: {"desc": info["desc"], "count": info["count"],
                    "avg_confidence": info["avg_confidence"],
                    "avg_vol_ratio": info["avg_vol_ratio"]}
            for label, info in summary.items()
        },
    }, ensure_ascii=False, indent=2)


def format_html(results: list[dict], date_str: str) -> str:
    valid = [r for r in results if "primary_base" in r]
    errors = [r for r in results if "error" in r]

    rows = []
    for i, s in enumerate(valid, 1):
        pb = s["primary_base"]
        ct = pb["contraction"]
        iv = pb.get("ice_volume", {})
        pos = pb.get("position", {})
        yy = pb.get("yang_yin", {})
        wo = pb.get("washout", {})

        sc = pb["confidence_score"]
        sc_color = "#dc2626" if sc >= 70 else ("#f59e0b" if sc >= 50 else "#94a3b8")

        contra = (
            f"{ct['start_date']} -> {ct['end_date']}<br>({ct['contraction_days']}天, {ct['avg_vol_ratio']}x)"
            if ct["has_contraction"] else "无缩量"
        )

        # 股是股非维度标签
        tags = []
        if yy.get("is_qualified"):
            tags.append(f'<span class="tag tag-yy">三阳控三阴</span>')
        if iv.get("has_ice"):
            tags.append(f'<span class="tag tag-ice">冰点量</span>')
        if iv.get("has_sudden_ice"):
            tags.append(f'<span class="tag tag-ice">骤然极冰</span>')
        if wo.get("pattern"):
            tags.append(f'<span class="tag tag-washout">{wo["pattern"]}</span>')
        if pos.get("ma_aligned"):
            tags.append(f'<span class="tag tag-pos">均线归位</span>')
        tag_html = " ".join(tags) if tags else '<span style="color:#94a3b8;font-size:10px">-</span>'

        # 洗盘+冰点+位置 详情tooltip
        extra_info_parts = []
        if wo.get("description"):
            extra_info_parts.append(wo["description"])
        if iv.get("description"):
            extra_info_parts.append(iv["description"])
        if pos.get("description"):
            extra_info_parts.append(pos["description"])
        extra_info = "<br>".join(extra_info_parts)

        rows.append(f"""<tr>
            <td>{i}</td>
            <td><strong>{s['name']}</strong><br><span class="code">{s['code']}</span></td>
            <td class="pct">{s['pct_change']:.2f}%</td>
            <td>{s['breakout_date']}</td>
            <td>{pb['start_date']} -> {pb['end_date']}<br><span class="detail">({pb['days']}天)</span></td>
            <td>{pb['avg_vol_ratio']}x / {pb['max_vol_ratio']}x</td>
            <td>{contra}</td>
            <td>{tag_html}</td>
            <td title="{extra_info}">{yy.get('description', '')[:12]}{'...' if len(yy.get('description', '')) > 12 else ''}</td>
            <td><span class="score" style="color:{sc_color}">{sc}</span></td>
        </tr>""")

    error_section = ""
    if errors:
        items = "".join(f'<li>{e["name"]}（{e["code"]}）: {e["error"]}</li>' for e in errors)
        error_section = f'<div class="errors"><h2>数据异常 / 未检测到底仓</h2><ul>{items}</ul></div>'

    # 时间段分布
    range_summary = build_range_summary(results)
    total_base = sum(v["count"] for v in range_summary.values())
    abcd_pairs = [(l, i) for l, i in range_summary.items() if l in "ABCD"]
    max_count = max(v["count"] for _, v in abcd_pairs) if abcd_pairs else 0
    range_rows = []
    sorted_ranges = sorted(range_summary.items(), key=lambda x: x[1]["count"], reverse=True)
    bar_colors = {"A": "#ef4444", "B": "#f59e0b", "C": "#3b82f6", "D": "#10b981", "其他": "#94a3b8"}
    for label, info in sorted_ranges:
        if label == "其他" and info["count"] == 0:
            continue
        pct = info["count"] / total_base * 100 if total_base > 0 else 0
        star = "★ " if info["count"] == max_count and label != "其他" else ""
        range_rows.append(f"""<div class="range-row">
            <div class="range-label">{star}[{label}] {info["desc"]}</div>
            <div class="range-bar-bg"><div class="range-bar" style="width:{pct}%;background:{bar_colors.get(label, '#94a3b8')}"></div></div>
            <div class="range-stats">{info["count"]}只 ({pct:.1f}%) 均置信度{info["avg_confidence"]} 均量比{info["avg_vol_ratio"]}x</div>
        </div>""")
        for s_ in info["stocks"][:5]:
            range_rows.append(f'<div class="range-stock">{s_["name"]}({s_["code"]}) 涨幅{s_["pct"]:.1f}% 底仓{s_["base_start"]}->{s_["base_end"]} 置信度{s_["confidence"]}</div>')
        if len(info["stocks"]) > 5:
            range_rows.append(f'<div class="range-stock" style="color:#94a3b8">... 共 {len(info["stocks"])} 只</div>')

    max_label = max(abcd_pairs, key=lambda x: x[1]["count"])[0] if abcd_pairs else "?"
    conclusion_label = max_label
    conclusion_desc = range_summary[conclusion_label]["desc"] if conclusion_label in range_summary else ""
    range_section = f"""<div class="range-distribution">
<h2>📊 底仓时间段分布统计</h2>
<p style="margin-bottom:16px;font-size:13px;color:#64748b">按底仓起始日期归入对应时间段</p>
{''.join(range_rows)}
<div class="conclusion">★ 结论: 异动底仓最集中的时间段是 [{conclusion_label}] {conclusion_desc}，共 {max_count} 只股票底仓集中于此</div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A股异动底仓分析报告 - {date_str}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Microsoft YaHei",sans-serif;background:#f5f7fa;color:#1a1a2e;padding:20px}}
.container{{max-width:1600px;margin:0 auto}}
h1{{font-size:22px;margin-bottom:6px}}
.header{{background:white;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.stats{{display:flex;gap:20px;margin-top:12px;flex-wrap:wrap}}
.stat-box{{background:#f0f4ff;border-radius:8px;padding:14px 22px;text-align:center}}
.stat-value{{font-size:28px;font-weight:700;color:#2563eb}}
.stat-label{{font-size:12px;color:#64748b;margin-top:2px}}
table{{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);font-size:12px}}
th{{background:#1e293b;color:white;padding:8px 10px;text-align:left;font-size:11px;font-weight:600;white-space:nowrap}}
td{{padding:8px 10px;border-bottom:1px solid #e2e8f0;font-size:11px;line-height:1.4}}
tr:hover{{background:#f8fafc}}
.code{{color:#94a3b8;font-size:10px;font-family:monospace}}
.pct{{color:#dc2626;font-weight:700;font-size:13px}}
.detail{{color:#94a3b8;font-size:9px}}
.score{{font-weight:700;font-size:14px}}
.tag{{display:inline-block;padding:1px 6px;border-radius:4px;font-size:9px;font-weight:600;margin:1px}}
.tag-yy{{background:#dcfce7;color:#15803d}}
.tag-ice{{background:#dbeafe;color:#1d4ed8}}
.tag-washout{{background:#fef3c7;color:#92400e}}
.tag-pos{{background:#ede9fe;color:#6d28d9}}
.errors{{background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:20px;margin-top:20px}}
.errors h2{{font-size:15px;color:#dc2626;margin-bottom:8px}}
.errors ul{{list-style:none}}
.errors li{{padding:3px 0;color:#7f1d1d;font-size:12px}}
.note{{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:10px 16px;margin-top:16px;font-size:12px;color:#92400e;line-height:1.6}}
.range-distribution{{background:white;border-radius:12px;padding:24px;margin-top:20px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.range-distribution h2{{font-size:16px;margin-bottom:4px}}
.range-row{{margin-bottom:14px}}
.range-label{{font-size:14px;font-weight:600;margin-bottom:4px}}
.range-bar-bg{{background:#e2e8f0;border-radius:4px;height:8px;margin:4px 0}}
.range-bar{{height:8px;border-radius:4px;min-width:2px}}
.range-stats{{font-size:12px;color:#64748b}}
.range-stock{{font-size:11px;color:#475569;padding:1px 0 1px 16px}}
.conclusion{{background:#f0fdf4;border:2px solid #22c55e;border-radius:10px;padding:14px 18px;margin-top:20px;font-size:15px;font-weight:700;color:#15803d}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;font-size:11px;color:#64748b}}
.legend span{{display:flex;align-items:center;gap:4px}}
.legend-dot{{width:10px;height:10px;border-radius:2px;display:inline-block}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>A股异动底仓分析报告</h1>
<p style="color:#64748b;font-size:13px">分析日期: {date_str}</p>
<div class="stats">
<div class="stat-box"><div class="stat-value">{len(results)}</div><div class="stat-label">涨幅>=10%股票</div></div>
<div class="stat-box"><div class="stat-value">{len(valid)}</div><div class="stat-label">检测到底仓</div></div>
<div class="stat-box"><div class="stat-value">{len(errors)}</div><div class="stat-label">未检测到</div></div>
</div>
<div class="legend">
<span>分析维度:</span>
<span><span class="legend-dot" style="background:#dcfce7;border:1px solid #15803d"></span> 三阳控三阴</span>
<span><span class="legend-dot" style="background:#dbeafe;border:1px solid #1d4ed8"></span> 冰点量/骤然极冰</span>
<span><span class="legend-dot" style="background:#fef3c7;border:1px solid #92400e"></span> 洗盘模式</span>
<span><span class="legend-dot" style="background:#ede9fe;border:1px solid #6d28d9"></span> 均线归位</span>
<span style="color:#94a3b8;margin-left:8px">来源: 股是股非</span>
</div>
</div>
<table><thead><tr>
<th>#</th><th>股票名称</th><th>涨幅</th><th>爆发日</th><th>底仓区间</th><th>均量比</th><th>缩量调整</th><th>信号标签</th><th>量态</th><th>置信度</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table>
{error_section}
{range_section}
<div class="note"><strong>分析说明：</strong>底仓区间通过回溯成交量异常放大的连续交易日集群识别。<br>
<strong>置信度评分维度（满分100）：</strong>放量强度(15) + 集群天数(10) + 距离爆发日(15) + 缩量质量(10) + 价格温和度(5) + 三阳控三阴(10) + 冰点量(15) + 好位置(10) + 洗盘模式(10)<br>
<strong>新增维度来源：</strong>«股是股非»系列 — 三阳控三阴、冰点量/骤然极冰、均线归位、洗盘模式分类<br>
<strong>仅供参考，不构成投资建议。</strong></div>
</div>
</body>
</html>"""


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="A股异动底仓分析 - 追溯涨幅>=10%股票的底仓建立时间段"
    )
    parser.add_argument("--output", "-o", default="text",
                        choices=["text", "json", "html"], help="输出格式")
    parser.add_argument("--threshold", "-t", type=float, default=9.9,
                        help="涨幅阈值 (默认: 9.9%%)")
    parser.add_argument("--max-stocks", "-m", type=int, default=0,
                        help="最大分析股票数 (0=不限)")
    args = parser.parse_args()

    date_str = datetime.now().strftime("%Y-%m-%d")

    # 1. 获取全量股票及筛选涨幅>=阈值的
    sys.stderr.write("=" * 70 + "\n")
    sys.stderr.write("  A股异动底仓分析工具\n")
    sys.stderr.write(f"  分析日期: {date_str}\n")
    sys.stderr.write("  新增维度: 三阳控三阴 | 冰点量 | 好位置 | 洗盘模式 (来源: 股是股非)\n")
    sys.stderr.write("=" * 70 + "\n\n")
    sys.stderr.write("[1/3] 获取A股全量列表并筛选涨幅>=10%...\n")

    all_stocks = fetch_all_stocks()
    stocks = filter_top_gainers(all_stocks, args.threshold, args.max_stocks)

    sys.stderr.write(f"\n  全量: {len(all_stocks)} 只, 涨幅>={args.threshold}%: {len(stocks)} 只\n\n")

    if not stocks:
        print("当日无涨幅>=10%的A股。")
        return

    # 2. 逐只分析
    sys.stderr.write(f"[2/3] 开始逐只分析底仓（共 {len(stocks)} 只）...\n")
    results = []
    for i, stock in enumerate(stocks):
        sys.stderr.write(f"  [{i+1}/{len(stocks)}] {stock['name']}（{stock['code']}）...")
        sys.stderr.flush()
        result = analyze_stock(stock)
        status = "OK" if "primary_base" in result else result.get("error", "?")
        sys.stderr.write(f" {status}\n")
        results.append(result)
        time.sleep(REQUEST_DELAY)

    # 3. 输出
    sys.stderr.write(f"\n[3/3] 生成报告...\n")
    if args.output == "json":
        # JSON 模式：stdout 纯 JSON
        print(format_json(results))
    elif args.output == "html":
        # HTML 模式：stdout 纯 HTML，不混入任何日志
        html = format_html(results, date_str)
        filename = f"breakout_base_analysis_{date_str.replace('-', '')}.html"
        path = os.path.join(os.getcwd(), filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        sys.stderr.write(f"  HTML报告已保存: {path}\n")
        # stdout 只输出纯 HTML，不含任何进度文本
        sys.stdout.write(html)
        sys.stdout.flush()
    else:
        print(format_text(results))
        print(format_range_text(results))


if __name__ == "__main__":
    main()
