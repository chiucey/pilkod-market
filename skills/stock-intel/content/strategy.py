#!/usr/bin/env python3
"""
尾盘动量选股战略引擎
基于文档：A股市场T+1微观结构下的尾盘动量与反内卷跟随策略
整合 Baostock + AKShare + QVERIS 三合一数据源
"""

import sys
import json
import subprocess
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

# ─── 配置 ────────────────────────────────────────────────────────────────────

QVERIS_API_KEY = "sk-EWuBOIYNNql10MfrX4T4sELRjRHH53uZ2jzlsvDh0Wo"

# 形态识别阈值（来自策略文档）
PATTERN_THRESHOLDS = {
    "smooth_rise": {
        "window_minutes": 30,         # 尾盘窗口 14:30-15:00
        "price_rise_min": 0.01,       # 最小涨幅 1%
        "price_rise_max": 0.03,       # 最大涨幅 3%
        "r_squared_min": 0.92,       # R² 最低要求
        "volume_growth_min": 1.2,    # 成交量增长倍数（相对全天均量）
        "priority": "MAX"
    },
    "straight_line_spike": {
        "window_minutes": 10,         # 末10分钟
        "price_rise_min": 0.05,       # 涨幅 > 5%
        "volume_shrink_ratio": 0.4,   # 成交量萎缩比例（后5min/前5min）
        "danger": "ABSOLUTE_AVOID",
        "priority": "BLOCK"
    },
    "volume_dump": {
        "price_drop_min": 0.02,        # 跌幅 > 2%
        "rebound_ratio": 0.3,         # 反弹幅度上限（反弹/下跌）
        "danger": "FORCE_LIQUIDATE",
        "priority": "VETO"
    },
    "fake_rise_dump": {
        "upper_shadow_ratio": 0.6,   # 上影线/实体 > 60% 视为可疑
        "volume_instability": 0.5,    # 量能波动系数
        "danger": "DEWEIGHT",
        "priority": "FILTER"
    }
}

# 宏观市场过滤阈值
MARKET_FILTER = {
    "index_critical": "000852",   # 中证1000
    "bear_threshold": -0.005,     # 指数日跌幅 > 0.5% → 暂停建仓
    "volume_shrink_ratio": 0.6    # 市场量能萎缩至60%以下 → 熔断
}

# ─── Layer 1: AKShare 实时扫描 ─────────────────────────────────────────────

def get_market_breadth() -> dict:
    """获取市场广度（上涨/下跌家数）+ 指数状态"""
    try:
        import akshare as ak
        summary = ak.stock_sse_summary()
        index_df = ak.stock_zh_index_spot_em()
        
        # 中证1000
        csi1000 = index_df[index_df['名称'] == '中证1000']
        csi1000_val = float(csi1000.iloc[0]['涨跌幅']) / 100 if not csi1000.empty else 0
        
        # 全市场量能
        total_vol = float(summary.iloc[0, 3]) if len(summary) > 0 else 0  # 成交额
        
        return {
            "status": "success",
            "up_count": int(summary.iloc[0, 1]) if len(summary) > 0 else 0,
            "down_count": int(summary.iloc[0, 2]) if len(summary) > 0 else 0,
            "csi1000_change": csi1000_val,
            "market_breadth_ratio": 0,  # 需计算
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_market_regime() -> str:
    """判断市场宏观状态：多头/空头/震荡"""
    try:
        import akshare as ak
        index_df = ak.stock_zh_index_spot_em()
        
        # 中证1000当日表现
        csi1000 = index_df[index_df['名称'] == '中证1000']
        change = float(csi1000.iloc[0]['涨跌幅']) / 100 if not csi1000.empty else 0
        
        # 上证指数
        sh = index_df[index_df['名称'] == '上证指数']
        sh_change = float(sh.iloc[0]['涨跌幅']) / 100 if not sh.empty else 0
        
        if change > 0.005 and sh_change > 0.005:
            return "BULL"
        elif change < -0.005 or sh_change < -0.005:
            return "BEAR"
        else:
            return "NEUTRAL"
    except Exception:
        return "UNKNOWN"


def scan_tail_volume_stocks(min_rise: float = 0.01, max_rise: float = 0.035) -> List[dict]:
    """
    扫描尾盘放量/异动个股（30分钟窗口初筛）
    策略：找涨幅在1%-3.5%的个股，作为尾盘稳步推升候选
    """
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        
        # 过滤条件：涨幅在策略窗口内，非ST，流通市值>10亿
        candidates = []
        for _, row in df.iterrows():
            try:
                change_pct = float(row.get('涨跌幅', 0))
                price = float(row.get('最新价', 0))
                name = str(row.get('名称', ''))
                code = str(row.get('代码', ''))
                amount = float(row.get('成交额', 0))
                
                # ST股过滤
                if 'ST' in name or '*ST' in name:
                    continue
                # 流通市值过滤（成交额>1亿作为市值代理）
                if amount < 1e8:
                    continue
                # 涨幅窗口过滤（策略核心区间）
                if change_pct < min_rise * 100 or change_pct > max_rise * 100:
                    continue
                    
                candidates.append({
                    "code": code,
                    "name": name,
                    "price": price,
                    "change_pct": change_pct,
                    "amount": amount,
                    "rank_score": change_pct  # 涨幅作为初步排序
                })
            except (ValueError, TypeError):
                continue
        
        # 按涨幅排序（尾盘稳步推升：1%-3%最理想）
        candidates.sort(key=lambda x: x['rank_score'], reverse=True)
        return candidates[:30]  # 返回TOP30
        
    except Exception as e:
        return [{"status": "error", "error": str(e)}]


def get_stock_minute_data(code: str, date: str = None) -> dict:
    """
    获取个股分钟级数据（AKShare）
    用于计算：R²平滑度、量能变化、尾盘各形态识别
    """
    try:
        import akshare as ak
        # 格式化代码
        market = "sh" if code.startswith('6') else "sz"
        
        # 获取日内5分钟K线（模拟分钟级）
        # 注意：AKShare部分股票支持1min，这里用5min演示
        try:
            df = ak.stock_zh_a_hist(
                symbol=code, 
                period="5", 
                start_date=(datetime.now() - timedelta(days=3)).strftime('%Y%m%d'),
                end_date=date or datetime.now().strftime('%Y%m%d'),
                adjust=""
            )
            if df is None or df.empty:
                return {"status": "no_data", "code": code}
            
            # 取最新交易日最后10条（≈尾盘50分钟）
            df = df.tail(10).reset_index(drop=True)
            
            closes = df['收盘'].astype(float).tolist()
            volumes = df['成交量'].astype(float).tolist()
            times = df['日期'].tolist() if '日期' in df.columns else list(range(len(closes)))
            
            return {
                "status": "success",
                "code": code,
                "closes": closes,
                "volumes": volumes,
                "times": times,
                "latest_close": closes[-1] if closes else 0,
                "close_change": (closes[-1] - closes[0]) / closes[0] if closes and closes[0] != 0 else 0
            }
        except Exception:
            return {"status": "unsupported", "code": code}
            
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ─── Layer 2: Baostock 历史K线 ─────────────────────────────────────────────

def get_tail_window_kline(code: str, days: int = 5) -> dict:
    """获取最近N天尾盘30分钟窗口的K线数据（Baostock）"""
    try:
        import baostock as bs
        bs.login()
        
        # 格式转换
        bs_code = code
        if not ('.' in code):
            bs_code = ('sh.' + code) if code.startswith('6') else ('sz.' + code)
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        rs = bs.query_history_k_data_plus(
            bs_code,
            'date,code,open,high,low,close,volume,turn,pctChg',
            start_date=start_date, end_date=end_date, frequency='d'
        )
        # rs.get_row_data() 是生成器，只可消费一次
        all_rows = []
        while rs.next():
            all_rows.append(rs.get_row_data())
        rows = [r for r in all_rows if r and len(r) >= 9 and r[5]]
        bs.logout()
        
        if not rows:
            return {"status": "no_data", "code": bs_code}
        
        # 分析最近3天的日线特征
        analysis = []
        for row in rows[-3:]:
            try:
                close = float(row[5])
                open_p = float(row[2])
                high = float(row[3])
                low = float(row[4])
                volume = float(row[6])
                pctChg = float(row[8]) if row[8] else 0
                
                # 简单尾盘特征代理（实际需要分钟数据，这里用日线模拟）
                daily_range = (high - low) / close if close != 0 else 0
                
                analysis.append({
                    "date": row[0],
                    "close": close,
                    "pct_chg": pctChg,
                    "daily_range": daily_range,
                    "volume": volume
                })
            except (ValueError, IndexError):
                continue
        
        return {
            "status": "success",
            "code": bs_code,
            "recent_days": analysis
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def calculate_smooth_rise_score(closes: List[float]) -> dict:
    """
    计算平滑上行动量因子（R² 线性回归拟合度）
    这是策略最核心的量化指标
    """
    if len(closes) < 5:
        return {"status": "insufficient_data"}
    
    n = len(closes)
    x = list(range(n))
    y = closes
    
    # 线性回归：y = a*x + b
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return {"status": "flat_line"}
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    # R² 计算
    ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
    ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # 累计收益率
    if closes[0] != 0:
        cumulative_return = (closes[-1] - closes[0]) / closes[0]
    else:
        cumulative_return = 0
    
    return {
        "status": "success",
        "r_squared": round(r_squared, 4),
        "slope": round(slope, 4),
        "cumulative_return": round(cumulative_return, 4),
        "n_datapoints": n,
        # 形态判定
        "is_smooth_rise": r_squared >= PATTERN_THRESHOLDS["smooth_rise"]["r_squared_min"] 
                          and PATTERN_THRESHOLDS["smooth_rise"]["price_rise_min"] <= cumulative_return <= PATTERN_THRESHOLDS["smooth_rise"]["price_rise_max"],
        "is_spike": cumulative_return > PATTERN_THRESHOLDS["straight_line_spike"]["price_rise_min"]
    }


# ─── Layer 3: QVERIS 舆情 & 新闻 ─────────────────────────────────────────────

def check_news_sentiment(code: str, name: str = "") -> dict:
    """通过QVERIS发现新闻舆情API并检查个股舆情"""
    try:
        # 发现新闻工具
        result = subprocess.run(
            ["node", 
             os.path.expanduser("~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs"),
             "discover", 
             "China stock news sentiment API"],
            capture_output=True, text=True,
            env={**os.environ, "QVERIS_API_KEY": QVERIS_API_KEY},
            timeout=30
        )
        
        # 提取search_id
        search_id = None
        for line in result.stdout.strip().split('\n'):
            if 'Discovery ID:' in line:
                search_id = line.split('Discovery ID:')[1].strip()
                break
        
        if not search_id:
            return {"status": "no_tool_found"}
        
        # 从发现结果中找可用的新闻API
        tool_id = None
        for line in result.stdout.strip().split('\n'):
            if 'ID: finnhub' in line or 'ID: newsapi' in line.lower() or 'ID: bloomberg' in line.lower():
                # 提取tool_id
                parts = line.split('ID:')
                if len(parts) > 1:
                    tool_id = parts[1].strip().split()[0]
                    break
        
        if not tool_id:
            return {"status": "no_relevant_news_tool"}
        
        # 调用新闻API
        call_result = subprocess.run(
            ["node",
             os.path.expanduser("~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs"),
             "call", tool_id,
             "--discovery-id", search_id,
             "--params", f'{{"symbol": "{code}"}}'],
            capture_output=True, text=True,
            env={**os.environ, "QVERIS_API_KEY": QVERIS_API_KEY},
            timeout=30
        )
        
        return {"status": "success", "raw": call_result.stdout[:1000]}
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ─── 核心：形态识别引擎 ───────────────────────────────────────────────────────

def recognize_pattern(code: str, name: str = "", minute_data: dict = None) -> dict:
    """
    四象限形态识别引擎
    返回：形态类型 + 优先级 + 操作指令 + 置信度
    """
    if not minute_data or minute_data.get("status") != "success":
        # 用Baostock日线做初步判定
        kline_data = get_tail_window_kline(code, days=3)
        if kline_data.get("status") != "success":
            return {"pattern": "UNKNOWN", "confidence": 0, "signal": "NO_DATA"}
        
        # 从日线数据做简单推断
        recent = kline_data.get("recent_days", [])
        if not recent:
            return {"pattern": "UNKNOWN", "confidence": 0, "signal": "NO_DATA"}
        
        latest = recent[-1]
        pct_chg = latest.get("pct_chg", 0) / 100
        
        if pct_chg < -0.02:
            return {
                "pattern": "VOLUME_DUMP",
                "confidence": 0.75,
                "signal": "VETO",
                "action": "禁止买入/强制止损",
                "pct_chg": pct_chg
            }
        elif pct_chg > 0.05:
            return {
                "pattern": "STRAIGHT_LINE_SPIKE",
                "confidence": 0.7,
                "signal": "BLOCK",
                "action": "绝对规避",
                "pct_chg": pct_chg
            }
        elif 0.01 <= pct_chg <= 0.03:
            return {
                "pattern": "SMOOTH_RISE_CANDIDATE",
                "confidence": 0.6,
                "signal": "WATCH",
                "action": "进入候选池，需分钟数据确认",
                "pct_chg": pct_chg
            }
        else:
            return {
                "pattern": "NEUTRAL",
                "confidence": 0.5,
                "signal": "HOLD",
                "action": "继续观察",
                "pct_chg": pct_chg
            }
    
    # 分钟数据分析（核心逻辑）
    closes = minute_data.get("closes", [])
    volumes = minute_data.get("volumes", [])
    
    if len(closes) < 5:
        return {"pattern": "UNKNOWN", "confidence": 0, "signal": "NO_DATA"}
    
    # ① 计算R²平滑因子
    r2_result = calculate_smooth_rise_score(closes)
    r2 = r2_result.get("r_squared", 0)
    cum_ret = r2_result.get("cumulative_return", 0)
    
    # ② 量能分析
    if len(volumes) >= 6:
        first_half_vol = sum(volumes[:len(volumes)//2])
        second_half_vol = sum(volumes[len(volumes)//2:])
        vol_trend = second_half_vol / first_half_vol if first_half_vol != 0 else 1
    else:
        vol_trend = 1
    
    # ③ 形态判决树
    # 条件A：R² >= 0.92 且 1% <= 累计涨幅 <= 3% → 稳步推升
    if r2 >= 0.92 and 0.01 <= cum_ret <= 0.03:
        return {
            "pattern": "SMOOTH_RISE",
            "confidence": round(min(r2 * 0.9 + vol_trend * 0.1, 0.99), 3),
            "signal": "BUY",
            "action": "最高优先级买入",
            "r2": r2,
            "cumulative_return": cum_ret,
            "vol_trend": vol_trend
        }
    
    # 条件B：末段涨幅 > 5% → 直线拉升陷阱
    if len(closes) >= 2:
        last_segment_return = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] != 0 else 0
        if last_segment_return > 0.05 and vol_trend < 0.6:
            return {
                "pattern": "STRAIGHT_LINE_SPIKE",
                "confidence": 0.85,
                "signal": "BLOCK",
                "action": "绝对规避/诱多陷阱",
                "last_segment_return": last_segment_return,
                "vol_shrink": vol_trend
            }
    
    # 条件C：持续下跌且无量反弹 → 放量下跌
    if cum_ret < -0.02 and vol_trend > 1.3:
        return {
            "pattern": "VOLUME_DUMP",
            "confidence": 0.8,
            "signal": "VETO",
            "action": "一票否决/强制止损",
            "cum_ret": cum_ret,
            "vol_expansion": vol_trend
        }
    
    # 条件D：先涨后砸（高波动但R²低）→ 洗盘信号
    if r2 < 0.7 and abs(cum_ret) > 0.01:
        return {
            "pattern": "FAKE_RISE_DUMP",
            "confidence": 0.65,
            "signal": "DEWEIGHT",
            "action": "降权/过滤出候选池",
            "r2": r2,
            "cum_ret": cum_ret
        }
    
    return {
        "pattern": "AMBIGUOUS",
        "confidence": 0.4,
        "signal": "HOLD",
        "action": "信号不明确，继续观察"
    }


# ─── 宏观过滤器 ───────────────────────────────────────────────────────────────

def macro_filter() -> dict:
    """宏观市场状态过滤器"""
    regime = get_market_regime()
    breadth = get_market_breadth()
    
    if regime == "BEAR":
        return {
            "allowed": False,
            "reason": "大盘下行趋势，暂停尾盘建仓",
            "regime": regime,
            "max_position": 0
        }
    
    if regime == "NEUTRAL" and breadth.get("csi1000_change", 0) < MARKET_FILTER["bear_threshold"]:
        return {
            "allowed": False,
            "reason": "中证1000跌幅超过0.5%，市场偏弱",
            "regime": regime,
            "max_position": 0.2  # 半仓熔断
        }
    
    return {
        "allowed": True,
        "reason": "市场状态正常，支持建仓",
        "regime": regime,
        "max_position": 1.0,
        "breadth": breadth
    }


# ─── 选股扫描主程序 ──────────────────────────────────────────────────────────

def screen_stocks(max_candidates: int = 20) -> dict:
    """
    选股扫描主流程
    1. 宏观过滤器 → 判断是否适合建仓
    2. AKShare全市场扫描 → 候选池
    3. 逐一个股形态识别 → 最终信号
    4. QVERIS舆情确认 → 最终评级
    """
    print(f"\n{'='*60}")
    print(f"  尾盘动量选股战略扫描  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    # Step 1: 宏观过滤
    print("【Step 1】宏观市场过滤...")
    macro = macro_filter()
    print(f"  市场状态: {macro['regime']} | 允许建仓: {macro['allowed']} | 仓位上限: {macro['max_position']}")
    
    if not macro["allowed"]:
        print("\n  🔴 大盘状态不支持建仓，扫描终止。")
        return {
            "status": "market_closed",
            "macro": macro,
            "signals": []
        }
    
    # Step 2: AKShare全市场扫描
    print("\n【Step 2】AKShare全市场扫描（尾盘异动候选）...")
    candidates = scan_tail_volume_stocks(
        min_rise=0.01,  # 涨幅>1%
        max_rise=0.035  # 涨幅<3.5%（含超过3%的待过滤）
    )
    print(f"  初筛候选: {len(candidates)} 只")
    
    if not candidates or (isinstance(candidates, list) and candidates and candidates[0].get("status") == "error"):
        return {
            "status": "scan_failed",
            "macro": macro,
            "error": str(candidates)
        }
    
    # Step 3: 逐一个股形态识别
    print("\n【Step 3】形态识别（四象限引擎）...")
    signals = []
    
    for stock in candidates[:max_candidates]:
        code = stock["code"]
        name = stock.get("name", "")
        
        # 获取分钟数据
        minute_data = get_stock_minute_data(code)
        
        # 形态识别
        pattern = recognize_pattern(code, name, minute_data)
        
        signal = {
            **stock,
            **pattern,
            "timestamp": datetime.now().isoformat()
        }
        signals.append(signal)
        
        # 打印信号
        emoji = {
            "BUY": "🟢",
            "BLOCK": "🔴",
            "VETO": "🔴",
            "WATCH": "🟡",
            "HOLD": "⚪",
            "DEWEIGHT": "🟡",
            "NO_DATA": "⚪"
        }.get(pattern.get("signal", "HOLD"), "⚪")
        
        action = pattern.get("action", "")
        conf = pattern.get("confidence", 0)
        print(f"  {emoji} {code} {name:<8} | {pattern.get('pattern','?'):<25} | 置信{conf:.0%} | {action}")
    
    # Step 4: 信号排序
    signal_order = {"BUY": 0, "WATCH": 1, "HOLD": 2, "DEWEIGHT": 3, "BLOCK": 4, "VETO": 5}
    signals.sort(key=lambda x: signal_order.get(x.get("signal", "HOLD"), 9))
    
    # 最终输出
    print(f"\n{'='*60}")
    print("  扫描结论")
    print(f"{'='*60}")
    buys = [s for s in signals if s.get("signal") == "BUY"]
    print(f"\n  🟢 买入候选 ({len(buys)} 只):")
    for s in buys:
        print(f"     {s['code']} {s['name']} 置信{s.get('confidence',0):.0%} 涨幅{s.get('change_pct',0):.2f}%")
    
    return {
        "status": "success",
        "scan_time": datetime.now().isoformat(),
        "macro": macro,
        "total_candidates": len(candidates),
        "signals": signals,
        "buy_candidates": buys,
        "total_scanned": len(signals)
    }


# ─── 单股深度分析 ────────────────────────────────────────────────────────────

def analyze_stock(code: str) -> dict:
    """单股深度分析（结合三层数据源）"""
    print(f"\n{'='*60}")
    print(f"  深度分析  {code}")
    print(f"{'='*60}\n")
    
    # 格式化代码
    code_raw = code.zfill(6)
    
    # Layer 1: AKShare 实时
    import akshare as ak
    try:
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == code_raw]
        if not row.empty:
            r = row.iloc[0]
            realtime = {
                "status": "success",
                "name": r.get('名称', ''),
                "price": r.get('最新价', 0),
                "change_pct": r.get('涨跌幅', 0),
                "volume": r.get('成交量', 0),
                "amount": r.get('成交额', 0),
                "high": r.get('最高', 0),
                "low": r.get('最低', 0),
                "pe": r.get('市盈率-动态', ''),
                "pb": r.get('市净率', ''),
            }
        else:
            realtime = {"status": "no_match"}
    except Exception as e:
        realtime = {"status": "error", "error": str(e)}
    
    # Layer 2: Baostock 历史
    history = get_tail_window_kline(code_raw, days=5)
    
    # Layer 3: 形态识别
    minute_data = get_stock_minute_data(code_raw)
    pattern = recognize_pattern(code_raw, realtime.get("name", ""), minute_data)
    
    return {
        "code": code_raw,
        "realtime": realtime,
        "history": history,
        "pattern": pattern,
        "timestamp": datetime.now().isoformat()
    }


# ─── 主入口 ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 strategy.py scan          # 全市场扫描")
        print("  python3 strategy.py analyze 000001  # 单股深度分析")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'scan':
        result = screen_stocks()
        print("\n【最终结果JSON】")
        print(json.dumps({k: v for k, v in result.items() if k != 'signals'}, ensure_ascii=False, indent=2))
        
    elif cmd == 'analyze':
        if len(sys.argv) < 3:
            print("请提供股票代码: python3 strategy.py analyze 000001")
            sys.exit(1)
        result = analyze_stock(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {cmd}")
