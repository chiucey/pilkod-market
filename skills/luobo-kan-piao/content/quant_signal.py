#!/usr/bin/env python3
"""
量化信号扫描器 v2 - 多维度共振选股系统
数据源: 腾讯财经API

模块:
  1. 均线粘合+MACD趋势共振 (原始)
  2. 价格通道趋势判断 (LLV/HHV + EMA + 趋势变色)
  3. 超买超卖指标 (RSI变体)
  4. 动量振荡器 (GUP1-GUP4, SMA多重平滑)
  5. 量价关系 (资金流/量价偏离)
  6. 形态识别 (金牛暴起/妖股)
  7. 多时间框架验证 (5/13/34/75/200)
  8. 信号过滤 (去重+多条件共振)
"""

import sys
import json
import requests
import time
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# 腾讯财经API数据获取
# ═══════════════════════════════════════════════════════════════

def get_stock_code(symbol: str) -> str:
    s = symbol.strip().lower()
    # 港股名称映射
    hk_names = {
        '商汤': 'hk00020', '商汤-w': 'hk00020',
        '阿里巴巴': 'hk09988', '阿里巴巴-w': 'hk09988', '阿里': 'hk09988',
        '腾讯': 'hk00700', '腾讯控股': 'hk00700',
        '地平线': 'hk09660', '地平线机器人': 'hk09660', '地平线机器人-w': 'hk09660',
        '小米': 'hk01810', '小米集团': 'hk01810', '小米集团-w': 'hk01810',
    }
    if s in hk_names:
        return hk_names[s]

    for prefix in ['sh', 'sz', 'bj', 'hk', 'http://', 'https://']:
        s = s.replace(prefix, '')
    s = s.replace('.', '').replace('/', '').strip('/')
    # 港股: 5位数字 0xxxx / 9xxxx, 且在已知港股列表中
    hk_codes = {'00700','00020','09988','09660','01810','03690','02018','02020'}
    if len(s) >= 5 and s[:5] in hk_codes:
        return f'hk{s[:5]}'
    if s.startswith('6') or s.startswith('9'):
        return f'sh{s[:6]}'
    elif s.startswith('0') or s.startswith('3') or s.startswith('2'):
        return f'sz{s[:6]}'
    elif s.startswith('8') or s.startswith('4'):
        return f'bj{s[:6]}'
    elif s.startswith('1') and len(s) >= 6:
        if s.startswith('15') or s.startswith('16') or s.startswith('17'):
            return f'sz{s[:6]}'
        return f'sh{s[:6]}'
    elif s.startswith('5'):
        return f'sh{s[:6]}'
    return f'sz{s[:6]}'


def fetch_kline(symbol: str, days: int = 250) -> list:
    """获取日K线 (前复权), 含成交量"""
    code = get_stock_code(symbol)
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,250,qfq"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://stockapp.finance.qq.com/',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] 获取数据失败: {e}", file=sys.stderr)
        return []

    stock_data = data.get('data', {}).get(code, {})
    klines = stock_data.get('qfqday') or stock_data.get('day') or []
    if not klines:
        # 港股尝试不带前复权
        if code.startswith('hk'):
            url2 = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,250,"
            try:
                resp2 = requests.get(url2, headers=headers, timeout=15)
                data2 = resp2.json()
                stock_data2 = data2.get('data', {}).get(code, {})
                klines = stock_data2.get('day') or []
            except Exception:
                pass
    if not klines:
        print(f"[ERROR] 未找到 {symbol} 的K线数据", file=sys.stderr)
        return []

    result = []
    for row in klines:
        if len(row) >= 5:
            try:
                result.append({
                    'date': row[0],
                    'open': float(row[1]),
                    'close': float(row[2]),
                    'high': float(row[3]),
                    'low': float(row[4]),
                    'volume': float(row[5]) if len(row) > 5 else 0,
                })
            except (ValueError, IndexError):
                continue
    return result


def fetch_realtime(symbol: str) -> dict:
    code = get_stock_code(symbol)
    url = f"https://qt.gtimg.cn/q={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        parts = resp.text.split('~')
        if len(parts) > 37:
            return {
                'name': parts[1], 'code': parts[2], 'price': float(parts[3]),
                'yesterday_close': float(parts[4]), 'open': float(parts[5]),
                'volume': float(parts[6]), 'change_pct': float(parts[32]),
            }
    except Exception:
        pass
    return {}


# ═══════════════════════════════════════════════════════════════
# 基础技术指标函数
# ═══════════════════════════════════════════════════════════════

def calc_ma(values: list, period: int) -> list:
    """简单移动平均"""
    ma = []
    for i in range(len(values)):
        if i < period - 1:
            ma.append(None)
        else:
            ma.append(sum(values[i - period + 1:i + 1]) / period)
    return ma


def calc_ema(values: list, period: int) -> list:
    """指数移动平均"""
    ema = []
    mult = 2.0 / (period + 1)
    for i, v in enumerate(values):
        if i == 0:
            ema.append(v)
        else:
            ema.append(v * mult + ema[-1] * (1 - mult))
    return ema


def calc_sma(values: list, period: int, weight: float = 1.0) -> list:
    """通达信SMA(X,N,M): Y = (M*X + (N-M)*Y') / N, M=weight"""
    sma = []
    for i, v in enumerate(values):
        if i == 0:
            sma.append(v)
        else:
            sma.append((weight * v + (period - weight) * sma[-1]) / period)
    return sma


def calc_hhv(values: list, period: int) -> list:
    """N周期最高值"""
    hhv = []
    for i in range(len(values)):
        if i < period - 1:
            hhv.append(None)
        else:
            hhv.append(max(values[i - period + 1:i + 1]))
    return hhv


def calc_llv(values: list, period: int) -> list:
    """N周期最低值"""
    llv = []
    for i in range(len(values)):
        if i < period - 1:
            llv.append(None)
        else:
            llv.append(min(values[i - period + 1:i + 1]))
    return llv


def safe_div(a, b, default=0.0):
    return a / b if b != 0 else default


def calc_deviation_from_vals(ma5, ma21, ma65):
    vals = [ma5, ma21, ma65]
    avg = sum(vals) / 3
    return max(abs(v - avg) / avg for v in vals) if avg else 0


# ═══════════════════════════════════════════════════════════════
# 模块1: 均线粘合+MACD趋势共振 (原始信号)
# ═══════════════════════════════════════════════════════════════

def mod1_ma_macd(closes, highs, lows, volumes, n, ma5, ma21, ma65, is_hk=False):
    """均线粘合+MACD趋势共振系统"""
    macd_ema12 = calc_ema(closes, 12)
    macd_ema26 = calc_ema(closes, 26)
    dif = [macd_ema12[i] - macd_ema26[i] for i in range(n)]
    dea = calc_ema(dif, 9)
    macd_bar = [(dif[i] - dea[i]) * 2 for i in range(n)]

    # 成交量均线 (港股庄股判定需要)
    vol_ma20 = calc_ma(volumes, 20)

    def deviation(i):
        vals = [ma5[i], ma21[i], ma65[i]]
        avg = sum(vals) / 3
        return max(abs(v - avg) / avg for v in vals) if avg else 0

    def is_bull_trend(i):
        if i < 10 or ma21[i] is None or ma65[i] is None:
            return False
        return all(ma21[j] > ma65[j] for j in range(i - 9, i + 1)
                   if ma21[j] is not None and ma65[j] is not None)

    def is_sticky(i):
        return all(x is not None for x in [ma5[i], ma21[i], ma65[i]]) and deviation(i) <= 0.15

    def is_zhuang(i):
        """庄股判定
        A股: DIF连续10日<0 (原始逻辑)
        港股: DIF连续10日<0 + DIF在收窄 + 缩量 + 未暴跌
        """
        if i < 10:
            return False
        # 基础条件: DIF连续10日<0
        base = all(dif[j] < 0 for j in range(i - 9, i + 1))
        if not base:
            return False

        # A股保持原始逻辑
        if not is_hk:
            return True

        # ── 港股增强判定 ──
        # 条件1: DIF在收窄 (当前DIF > 5天前DIF, 说明下跌动能衰减)
        if i >= 5:
            dif_narrowing = dif[i] > dif[i - 5]
        else:
            dif_narrowing = False

        # 条件2: 缩量 (当日成交量 < 20日均量的0.8倍 = 洗盘而非出逃)
        vol_shrinking = (vol_ma20[i] is not None and vol_ma20[i] > 0
                         and volumes[i] < vol_ma20[i] * 0.8)

        # 条件3: 未暴跌 (近20日跌幅 < 15%, 排除恐慌下跌)
        if i >= 20 and closes[i - 20] > 0:
            drop_pct = (closes[i] - closes[i - 20]) / closes[i - 20]
            no_crash = drop_pct > -0.15
        else:
            no_crash = True

        # 港股必须三个过滤条件同时满足
        return dif_narrowing and vol_shrinking and no_crash

    def sig_bull_sticky(i):
        return is_bull_trend(i) and is_sticky(i)

    def sig_target(i):
        return is_bull_trend(i) and is_sticky(i) and is_zhuang(i)

    def sig_breakout(i):
        if i < 65 or not is_sticky(i):
            return False
        if ma65[i] is None or ma65[i - 3] is None or ma65[i] <= ma65[i - 3]:
            return False
        tpx = min(ma65[i] * 1.15, ma21[i] * 1.13)
        return closes[i] > tpx

    last_target = -1
    for i in range(n):
        if sig_target(i):
            last_target = i

    def sig_attack(i):
        if last_target < 0 or i < last_target or i < 1:
            return False
        return dif[i] > dea[i] and dif[i - 1] <= dea[i - 1]

    last_attack = -1
    for i in range(n):
        if sig_attack(i):
            last_attack = i

    return {
        'dif': dif, 'dea': dea, 'macd_bar': macd_bar,
        'is_bull_trend': is_bull_trend, 'is_sticky': is_sticky,
        'is_zhuang': is_zhuang, 'deviation': deviation,
        'sig_bull_sticky': sig_bull_sticky, 'sig_target': sig_target,
        'sig_attack': sig_attack, 'sig_breakout': sig_breakout,
        'last_target': last_target, 'last_attack': last_attack,
    }


# ═══════════════════════════════════════════════════════════════
# 模块2: 价格通道趋势判断
# LLV(LOW,34) + HHV(HIGH,30) + EMA + 趋势变色
# ═══════════════════════════════════════════════════════════════

def mod2_price_channel(closes, highs, lows, n):
    """
    价格通道趋势系统:
    - LLV(LOW,34) / HHV(HIGH,30) 构建波动通道
    - EMA平滑处理价格, 过滤短期噪音
    - 趋势线变色: 红涨蓝跌 (基于动力线计算)
    """
    llv34 = calc_llv(lows, 34)
    hhv30 = calc_hhv(highs, 30)
    ema_close = calc_ema(closes, 13)  # EMA13平滑价格

    # 动力线 = (EMA13 - LLV34) / (HHV30 - LLV34) * 100
    power_line = []
    for i in range(n):
        if llv34[i] is None or hhv30[i] is None:
            power_line.append(None)
        else:
            rng = hhv30[i] - llv34[i]
            power_line.append(safe_div(ema_close[i] - llv34[i], rng, 50.0) * 100)

    # 趋势方向: 动力线>50 为上涨趋势(红), 否则下跌(蓝)
    trend_up = [pl > 50 if pl is not None else None for pl in power_line]

    # 价格在通道中的位置 (0-100)
    channel_pos = []
    for i in range(n):
        if llv34[i] is None or hhv30[i] is None:
            channel_pos.append(None)
        else:
            rng = hhv30[i] - llv34[i]
            channel_pos.append(safe_div(closes[i] - llv34[i], rng, 50.0) * 100)

    return {
        'llv34': llv34, 'hhv30': hhv30, 'ema13': ema_close,
        'power_line': power_line, 'trend_up': trend_up,
        'channel_pos': channel_pos,
    }


# ═══════════════════════════════════════════════════════════════
# 模块3: 超买超卖指标
# (CLOSE-LLV(LOW,N)) / (HHV(HIGH,N)-LLV(LOW,N)) * 100
# ═══════════════════════════════════════════════════════════════

def mod3_overbought_oversold(closes, highs, lows, n):
    """
    多周期超买超卖 (RSI变体)
    - 9日: 短期超买超卖
    - 14日: 标准周期
    - 34日: 中期极端状态
    近100为超买, 近0为超卖
    """
    results = {}
    for period in [9, 14, 34]:
        llv = calc_llv(lows, period)
        hhv = calc_hhv(highs, period)
        rsi_vals = []
        for i in range(n):
            if llv[i] is None or hhv[i] is None:
                rsi_vals.append(None)
            else:
                rng = hhv[i] - llv[i]
                rsi_vals.append(safe_div(closes[i] - llv[i], rng, 50.0) * 100)
        results[f'rsi_{period}'] = rsi_vals

    return results


# ═══════════════════════════════════════════════════════════════
# 模块4: 动量振荡器 (GUP1-GUP4 SMA多重平滑)
# ═══════════════════════════════════════════════════════════════

def mod4_momentum_oscillator(closes, highs, lows, n):
    """
    SMA平滑处理的RSI改良版本
    GUP1: 基础RSI值 (使用涨跌幅计算)
    GUP2: SMA(GUP1, 3, 1) 第一次平滑
    GUP3: SMA(GUP2, 3, 1) 第二次平滑
    GUP4: SMA(GUP3, 3, 1) 第三次平滑
    3次平滑增强信号可靠性
    """
    # GUP1: 基于日涨跌幅的RSI变体
    gains = [0.0]
    for i in range(1, n):
        gains.append(max(0.0, closes[i] - closes[i - 1]))
    avg_gain = calc_sma(gains, 14, 1.0)

    losses = [0.0]
    for i in range(1, n):
        losses.append(max(0.0, closes[i - 1] - closes[i]))
    avg_loss = calc_sma(losses, 14, 1.0)

    gup1 = []
    for i in range(n):
        if avg_gain[i] + avg_loss[i] == 0:
            gup1.append(50.0)
        else:
            gup1.append(avg_gain[i] / (avg_gain[i] + avg_loss[i]) * 100)

    gup2 = calc_sma(gup1, 3, 1.0)
    gup3 = calc_sma(gup2, 3, 1.0)
    gup4 = calc_sma(gup3, 3, 1.0)

    # 动量方向: GUP4 > GUP3 表示动量向上
    momentum_up = [gup4[i] > gup3[i] for i in range(n)]

    return {
        'gup1': gup1, 'gup2': gup2, 'gup3': gup3, 'gup4': gup4,
        'momentum_up': momentum_up,
    }


# ═══════════════════════════════════════════════════════════════
# 模块5: 量价关系 (资金流/量价偏离)
# 资金Q = EMA(AMOUNT,13); 过滤Q = (资金Q/量Q)/100
# ═══════════════════════════════════════════════════════════════

def mod5_volume_price(closes, volumes, n):
    """
    量价关系分析:
    - 成交额近似 = 收盘价 * 成交量
    - 资金线 = EMA(成交额, 13)
    - 量线 = EMA(成交量, 13)
    - 均价偏离度 = 资金线 / 量线 / 100
    - 异常量价检测: 量价背离/量价齐升
    """
    # 近似成交额 (腾讯API不直接提供AMOUNT)
    amounts = [closes[i] * volumes[i] for i in range(n)]

    fund_q = calc_ema(amounts, 13)    # 资金Q
    vol_q = calc_ema(volumes, 13)     # 量Q

    # 均价偏离度
    price_deviation = []
    for i in range(n):
        if vol_q[i] > 0:
            price_deviation.append(fund_q[i] / vol_q[i] / 100)
        else:
            price_deviation.append(None)

    # 量比: 今日量/5日均量
    vol_ma5 = calc_ma(volumes, 5)
    vol_ratio = []
    for i in range(n):
        if vol_ma5[i] and vol_ma5[i] > 0:
            vol_ratio.append(volumes[i] / vol_ma5[i])
        else:
            vol_ratio.append(None)

    # 资金方向: 资金线在上升
    fund_up = [fund_q[i] > fund_q[i - 1] if i > 0 else False for i in range(n)]

    # 量价齐升: 价涨 + 放量
    vol_price_up = []
    for i in range(n):
        if i < 1:
            vol_price_up.append(False)
            continue
        price_up = closes[i] > closes[i - 1]
        vol_up = volumes[i] > (vol_ma5[i] * 1.2 if vol_ma5[i] else volumes[i - 1])
        vol_price_up.append(price_up and vol_up)

    # 量价背离: 价涨量缩 or 价跌量增
    divergence = []
    for i in range(n):
        if i < 1:
            divergence.append(0)
            continue
        if closes[i] > closes[i - 1] and volumes[i] < volumes[i - 1]:
            divergence.append(-1)  # 顶背离
        elif closes[i] < closes[i - 1] and volumes[i] > volumes[i - 1]:
            divergence.append(1)   # 底背离 (价跌量增, 可能吸筹)
        else:
            divergence.append(0)

    return {
        'fund_line': fund_q, 'vol_line': vol_q,
        'price_deviation': price_deviation, 'vol_ratio': vol_ratio,
        'fund_up': fund_up, 'vol_price_up': vol_price_up,
        'divergence': divergence,
    }


# ═══════════════════════════════════════════════════════════════
# 模块6: 形态识别 (金牛暴起 / 妖股)
# ═══════════════════════════════════════════════════════════════

def mod6_pattern(closes, opens, highs, lows, volumes, n):
    """
    形态识别:
    - 金牛暴起: 连续阳线 + 放量突破
    - 妖股检测: 异常波动率 + 极端量价
    """
    ma20 = calc_ma(closes, 20)
    vol_ma20 = calc_ma(volumes, 20)

    # 阳线判断
    bullish = [closes[i] > opens[i] for i in range(n)]

    # ── 金牛暴起 ──
    # 条件: 连续3天以上阳线 + 最近一天涨幅>3% + 放量(>1.5倍20日均量) + 突破20日高点
    golden_bull = []
    for i in range(n):
        if i < 4 or ma20[i] is None:
            golden_bull.append(False)
            continue

        # 连续3天阳线
        consecutive_bull = all(bullish[j] for j in range(i - 2, i + 1))

        # 最近一天涨幅>3%
        pct_change = safe_div(closes[i] - closes[i - 1], closes[i - 1]) * 100
        big_move = pct_change > 3.0

        # 放量
        vol_explosion = volumes[i] > (vol_ma20[i] * 1.5 if vol_ma20[i] else volumes[i])

        # 突破近20日高点
        recent_high = max(highs[i - 19:i + 1])
        break_high = closes[i] >= recent_high

        golden_bull.append(consecutive_bull and big_move and vol_explosion and break_high)

    # ── 妖股检测 ──
    # 条件: 近10日波动率>8% + 多次涨跌幅>5% + 换手极端
    demon_stock = []
    for i in range(n):
        if i < 10:
            demon_stock.append(False)
            continue

        # 10日波动率
        ten_day_range = []
        for j in range(i - 9, i + 1):
            if highs[j] > 0:
                ten_day_range.append((highs[j] - lows[j]) / highs[j] * 100)
        avg_range = sum(ten_day_range) / len(ten_day_range) if ten_day_range else 0

        # 大幅波动天数
        big_days = 0
        for j in range(i - 9, i + 1):
            if j > 0 and abs(safe_div(closes[j] - closes[j - 1], closes[j - 1]) * 100) > 5:
                big_days += 1

        # 异常放量天数
        vol_spikes = 0
        for j in range(i - 9, i + 1):
            if vol_ma20[j] and volumes[j] > vol_ma20[j] * 2:
                vol_spikes += 1

        demon_stock.append(avg_range > 8.0 and (big_days >= 3 or vol_spikes >= 3))

    return {
        'golden_bull': golden_bull, 'demon_stock': demon_stock,
    }


# ═══════════════════════════════════════════════════════════════
# 模块7: 多时间框架验证
# 短期(5/13) 中期(34/75) 长期(200)
# ═══════════════════════════════════════════════════════════════

def mod7_multi_timeframe(closes, n):
    """
    多周期均线共振:
    - 短期: MA5/MA13 → 捕捉买卖点
    - 中期: MA34/MA75 → 判断趋势
    - 长期: MA200 → 牛熊分界
    - 多周期一致性评分
    """
    ma = {}
    for p in [5, 13, 34, 75, 200]:
        ma[p] = calc_ma(closes, p)

    # 各周期趋势判断
    short_bull = (ma[5][-1] is not None and ma[13][-1] is not None
                  and ma[5][-1] > ma[13][-1])
    mid_bull = (ma[34][-1] is not None and ma[75][-1] is not None
                and ma[34][-1] > ma[75][-1])
    long_bull = ma[200][-1] is not None and closes[-1] > ma[200][-1]

    # 价格相对位置
    positions = {}
    for p in [5, 13, 34, 75, 200]:
        if ma[p][-1] and ma[p][-1] > 0:
            positions[p] = safe_div(closes[-1] - ma[p][-1], ma[p][-1]) * 100
        else:
            positions[p] = None

    # 多周期一致性 (0-100)
    score = 50
    if short_bull:
        score += 15
    else:
        score -= 15
    if mid_bull:
        score += 20
    else:
        score -= 20
    if long_bull:
        score += 15
    else:
        score -= 15
    score = max(0, min(100, score))

    return {
        'ma': ma, 'short_bull': short_bull, 'mid_bull': mid_bull,
        'long_bull': long_bull, 'positions': positions,
        'consistency_score': score,
    }


# ═══════════════════════════════════════════════════════════════
# 模块8: 信号过滤 (去重+多条件共振)
# ═══════════════════════════════════════════════════════════════

def mod8_signal_filter(signals_list, n, window=30):
    """
    信号过滤:
    - 去重: 同类信号在window日内只保留首次
    - 共振确认: 多个模块同时发出信号才确认
    """
    # COUNT(condition, window)=1 逻辑: window日内信号唯一
    def filter_unique(signal_fn, window):
        filtered = []
        for i in range(n):
            if not signal_fn(i):
                filtered.append(False)
                continue
            # 检查window日内是否有其他信号
            count = sum(1 for j in range(max(0, i - window + 1), i + 1) if signal_fn(j))
            filtered.append(count == 1)
        return filtered

    return {'filter_unique': filter_unique}


# ═══════════════════════════════════════════════════════════════
# 综合信号引擎
# ═══════════════════════════════════════════════════════════════

def calc_signals(klines: list, is_hk: bool = False) -> dict:
    """计算全部8个模块的信号"""
    if len(klines) < 80:
        return {'error': '数据不足, 至少需要80个交易日'}

    closes = [k['close'] for k in klines]
    opens = [k['open'] for k in klines]
    highs = [k['high'] for k in klines]
    lows = [k['low'] for k in klines]
    volumes = [k['volume'] for k in klines]
    dates = [k['date'] for k in klines]
    n = len(closes)

    ma5 = calc_ma(closes, 5)
    ma21 = calc_ma(closes, 21)
    ma65 = calc_ma(closes, 65)

    # ── 运行所有模块 ──
    m1 = mod1_ma_macd(closes, highs, lows, volumes, n, ma5, ma21, ma65, is_hk=is_hk)
    m2 = mod2_price_channel(closes, highs, lows, n)
    m3 = mod3_overbought_oversold(closes, highs, lows, n)
    m4 = mod4_momentum_oscillator(closes, highs, lows, n)
    m5 = mod5_volume_price(closes, volumes, n)
    m6 = mod6_pattern(closes, opens, highs, lows, volumes, n)
    m7 = mod7_multi_timeframe(closes, n)
    m8 = mod8_signal_filter([], n)

    latest = n - 1

    # ── 跟踪计数 ──
    track = (latest - m1['last_target']) * 8 if m1['last_target'] >= 0 else 0

    # ── 涨幅 ──
    gain = 0
    daily_gain = 0
    if m1['last_attack'] >= 0:
        gain = safe_div(closes[latest] - closes[m1['last_attack']], closes[m1['last_attack']]) * 100
        days = latest - m1['last_attack']
        daily_gain = gain / days if days > 0 else 0

    # ── 综合评分 (共振度) ──
    resonance_score = 0
    # 模块1: 均线粘合+MACD (最多30分)
    if m1['sig_bull_sticky'](latest):
        resonance_score += 10
    if m1['is_zhuang'](latest):
        resonance_score += 10
    if m1['sig_target'](latest):
        resonance_score += 5
    if m1['sig_attack'](latest):
        resonance_score += 5

    # 模块2: 价格通道 (最多15分)
    if m2['trend_up'][latest]:
        resonance_score += 10
    if m2['power_line'][latest] and 30 < m2['power_line'][latest] < 80:
        resonance_score += 5  # 在健康区间

    # 模块3: 超买超卖 (最多10分, 减分项)
    rsi14 = m3['rsi_14'][latest]
    if rsi14 is not None:
        if rsi14 < 30:
            resonance_score += 10  # 超卖反弹
        elif rsi14 < 50:
            resonance_score += 5
        elif rsi14 > 80:
            resonance_score -= 10  # 超买风险

    # 模块4: 动量 (最多10分)
    if m4['momentum_up'][latest]:
        resonance_score += 5
    if m4['gup4'][latest] > 50:
        resonance_score += 5

    # 模块5: 量价 (最多15分)
    if m5['fund_up'][latest]:
        resonance_score += 5
    if m5['vol_price_up'][latest]:
        resonance_score += 5
    if m5['divergence'][latest] == 1:  # 底背离 = 吸筹
        resonance_score += 5

    # 模块6: 形态 (最多10分)
    if m6['golden_bull'][latest]:
        resonance_score += 10
    if m6['demon_stock'][latest]:
        resonance_score -= 5  # 妖股减分

    # 模块7: 多周期 (最多10分)
    resonance_score += m7['consistency_score'] // 10

    resonance_score = max(0, min(100, resonance_score))

    # ── 综合操作建议 ──
    buy_conds = [m1['sig_attack'](latest), m1['sig_breakout'](latest), m6['golden_bull'][latest]]
    risk_conds = [
        m3['rsi_14'][latest] and m3['rsi_14'][latest] > 80,
        m6['demon_stock'][latest],
        m5['divergence'][latest] == -1,
    ]

    # ── 汇总 ──
    sig = {
        'date': dates[latest],
        'close': closes[latest],
        # 模块1
        'ma5': round(ma5[latest], 2) if ma5[latest] else None,
        'ma21': round(ma21[latest], 2) if ma21[latest] else None,
        'ma65': round(ma65[latest], 2) if ma65[latest] else None,
        'deviation': round(m1['deviation'](latest) * 100, 2),
        'dif': round(m1['dif'][latest], 4),
        'dea': round(m1['dea'][latest], 4),
        'macd_bar': round(m1['macd_bar'][latest], 4),
        'bull_sticky': m1['sig_bull_sticky'](latest),
        'zhuang': m1['is_zhuang'](latest),
        'target': m1['sig_target'](latest),
        'attack': m1['sig_attack'](latest),
        'breakout': m1['sig_breakout'](latest),
        'track': track,
        'gain': round(gain, 2),
        'daily_gain': round(daily_gain, 2),
        # 模块2
        'trend_up': m2['trend_up'][latest],
        'power_line': round(m2['power_line'][latest], 1) if m2['power_line'][latest] else None,
        'channel_pos': round(m2['channel_pos'][latest], 1) if m2['channel_pos'][latest] else None,
        # 模块3
        'rsi_9': round(m3['rsi_9'][latest], 1) if m3['rsi_9'][latest] else None,
        'rsi_14': round(m3['rsi_14'][latest], 1) if m3['rsi_14'][latest] else None,
        'rsi_34': round(m3['rsi_34'][latest], 1) if m3['rsi_34'][latest] else None,
        # 模块4
        'gup4': round(m4['gup4'][latest], 1),
        'momentum_up': m4['momentum_up'][latest],
        # 模块5
        'vol_ratio': round(m5['vol_ratio'][latest], 2) if m5['vol_ratio'][latest] else None,
        'fund_up': m5['fund_up'][latest],
        'vol_price_up': m5['vol_price_up'][latest],
        'divergence': m5['divergence'][latest],
        # 模块6
        'golden_bull': m6['golden_bull'][latest],
        'demon_stock': m6['demon_stock'][latest],
        # 模块7
        'short_bull': m7['short_bull'],
        'mid_bull': m7['mid_bull'],
        'long_bull': m7['long_bull'],
        'consistency_score': m7['consistency_score'],
        # 模块8
        'resonance_score': resonance_score,
        # 原始
        'any_buy_signal': any(buy_conds),
        'any_risk_signal': any(risk_conds),
    }

    # ── 近30日信号历史 ──
    history = []
    for i in range(max(0, latest - 29), latest + 1):
        day_sig = {}
        if m1['sig_target'](i):   day_sig['目标'] = 12.8
        if m1['sig_attack'](i):   day_sig['出击'] = 16.8
        if m1['sig_breakout'](i): day_sig['突破'] = 20.8
        if m1['sig_bull_sticky'](i): day_sig['粘合'] = 5
        if m1['is_zhuang'](i):    day_sig['庄股'] = 3
        if m6['golden_bull'][i]:  day_sig['金牛暴起'] = True
        if m6['demon_stock'][i]:  day_sig['妖股'] = True
        if day_sig:
            history.append({'date': dates[i], 'close': closes[i], 'signals': day_sig})
    sig['history'] = history

    sig['target_dates'] = [dates[i] for i in range(n) if m1['sig_target'](i)]
    sig['attack_dates'] = [dates[i] for i in range(n) if m1['sig_attack'](i)]

    return sig


# ═══════════════════════════════════════════════════════════════
# 输出格式化
# ═══════════════════════════════════════════════════════════════

def rsi_label(val):
    if val is None:
        return ''
    if val > 80: return ' ⚠️超买'
    if val > 65: return ' 偏强'
    if val < 20: return ' 🔥极度超卖'
    if val < 35: return ' 超卖'
    return ''


def format_result(symbol: str, sig: dict) -> str:
    if 'error' in sig:
        return f"❌ {symbol}: {sig['error']}"

    L = []
    L.append(f"{'━'*56}")
    L.append(f"📊 量化信号扫描 v2: {symbol}")
    L.append(f"{'━'*56}")
    L.append(f"📅 {sig['date']}  收盘: {sig['close']}")
    L.append(f"")

    # ── 模块1: 均线+MACD ──
    L.append(f"┌─ ① 均线+MACD趋势共振")
    L.append(f"│  MA5:{sig['ma5']}  MA21:{sig['ma21']}  MA65:{sig['ma65']}")
    L.append(f"│  乖离率:{sig['deviation']}%  DIF:{sig['dif']}  DEA:{sig['dea']}  MACD:{sig['macd_bar']}")
    m1_flags = []
    if sig['bull_sticky']: m1_flags.append('🔴粘合')
    if sig['zhuang']:      m1_flags.append('🟡庄股')
    if sig['target']:      m1_flags.append('⚪目标')
    if sig['attack']:      m1_flags.append('🟢出击')
    if sig['breakout']:    m1_flags.append('🔵突破')
    L.append(f"│  信号: {' '.join(m1_flags) if m1_flags else '无'}")
    if sig['track'] > 0:
        L.append(f"│  跟踪: 目标后{sig['track']//8}天  涨幅:{sig['gain']:+.2f}%  日均:{sig['daily_gain']:+.2f}%")
    L.append(f"└{'─'*50}")

    # ── 模块2: 价格通道 ──
    L.append(f"")
    L.append(f"┌─ ② 价格通道趋势")
    trend_icon = '🔴' if sig['trend_up'] else '🔵'
    L.append(f"│  趋势: {trend_icon} {'上涨' if sig['trend_up'] else '下跌'}")
    L.append(f"│  动力线: {sig['power_line']}  通道位置: {sig['channel_pos']}%")
    L.append(f"└{'─'*50}")

    # ── 模块3: 超买超卖 ──
    L.append(f"")
    L.append(f"┌─ ③ 超买超卖")
    L.append(f"│  RSI9:  {sig['rsi_9']}{rsi_label(sig['rsi_9'])}")
    L.append(f"│  RSI14: {sig['rsi_14']}{rsi_label(sig['rsi_14'])}")
    L.append(f"│  RSI34: {sig['rsi_34']}{rsi_label(sig['rsi_34'])}")
    L.append(f"└{'─'*50}")

    # ── 模块4: 动量振荡 ──
    L.append(f"")
    L.append(f"┌─ ④ 动量振荡器")
    mom_icon = '📈' if sig['momentum_up'] else '📉'
    L.append(f"│  GUP4: {sig['gup4']}  动量: {mom_icon} {'向上' if sig['momentum_up'] else '向下'}")
    L.append(f"└{'─'*50}")

    # ── 模块5: 量价关系 ──
    L.append(f"")
    L.append(f"┌─ ⑤ 量价关系")
    vr = sig['vol_ratio']
    vr_txt = f"{vr}x" if vr else 'N/A'
    div_map = {0: '正常', -1: '⚠️顶背离', 1: '✨底背离(吸筹?)'}
    L.append(f"│  量比: {vr_txt}  资金: {'流入↑' if sig['fund_up'] else '流出↓'}")
    L.append(f"│  量价: {'齐升' if sig['vol_price_up'] else '非齐升'}  背离: {div_map.get(sig['divergence'], 'N/A')}")
    L.append(f"└{'─'*50}")

    # ── 模块6: 形态识别 ──
    L.append(f"")
    L.append(f"┌─ ⑥ 形态识别")
    p_flags = []
    if sig['golden_bull']: p_flags.append('🐂金牛暴起')
    if sig['demon_stock']: p_flags.append('👻妖股')
    L.append(f"│  {'  '.join(p_flags) if p_flags else '无特殊形态'}")
    L.append(f"└{'─'*50}")

    # ── 模块7: 多周期共振 ──
    L.append(f"")
    L.append(f"┌─ ⑦ 多时间框架")
    L.append(f"│  短期(MA5/13): {'🔴多头' if sig['short_bull'] else '🔵空头'}")
    L.append(f"│  中期(MA34/75): {'🔴多头' if sig['mid_bull'] else '🔵空头'}")
    L.append(f"│  长期(MA200): {'🔴牛市上方' if sig['long_bull'] else '🔵熊市下方'}")
    L.append(f"│  一致性评分: {sig['consistency_score']}/100")
    L.append(f"└{'─'*50}")

    # ── 模块8: 综合共振评分 ──
    L.append(f"")
    score = sig['resonance_score']
    if score >= 80:    score_bar = '🟢🟢🟢🟢🟢 强烈共振'
    elif score >= 60:  score_bar = '🟢🟢🟢🟢⚪ 较强共振'
    elif score >= 40:  score_bar = '🟡🟡🟡⚪⚪ 中等共振'
    elif score >= 20:  score_bar = '🟠🟠⚪⚪⚪ 弱共振'
    else:              score_bar = '🔴⚪⚪⚪⚪ 无共振'
    L.append(f"┌─ 🎯 综合共振评分: {score}/100")
    L.append(f"│  {score_bar}")
    L.append(f"└{'─'*50}")

    # ── 操作建议 ──
    L.append(f"")
    L.append(f"┌─ 💡 操作建议")
    buy = sig['any_buy_signal']
    risk = sig['any_risk_signal']

    if buy and not risk and score >= 60:
        L.append(f"│  🚀 强共振买入信号! 多模块确认, 建议果断买入")
        L.append(f"│  📌 止损设在多头粘合平台最低点下方")
    elif buy and score >= 40:
        L.append(f"│  ✅ 买入信号触发, 但共振度一般({score}分)")
        L.append(f"│  📌 可轻仓试探, 严格止损")
    elif sig['target'] and not buy:
        L.append(f"│  👁 目标信号已出, 等待出击/突破确认")
        L.append(f"│  📌 加入自选池重点观察")
    elif risk:
        L.append(f"│  ⚠️ 检测到风险信号:")
        if sig['rsi_14'] and sig['rsi_14'] > 80:
            L.append(f"│    - RSI14={sig['rsi_14']} 超买, 不宜追高")
        if sig['demon_stock']:
            L.append(f"│    - 妖股形态, 波动剧烈, 风险极高")
        if sig['divergence'] == -1:
            L.append(f"│    - 顶背离信号, 可能见顶")
    elif score >= 50:
        L.append(f"│  📊 中等共振({score}分), 可持续关注")
        L.append(f"│  📌 等待更多确认信号")
    else:
        L.append(f"│  💤 无交易信号, 继续观望")
    L.append(f"└{'─'*50}")

    # ── 信号历史 ──
    if sig.get('history'):
        L.append(f"")
        L.append(f"┌─ 📋 近30日信号历史")
        for h in sig['history'][-15:]:
            sigs = ', '.join(str(v) if v is True else f"{k}={v}" for k, v in h['signals'].items())
            L.append(f"│  {h['date']}  {h['close']}  → {sigs}")
        L.append(f"└{'─'*50}")

    L.append(f"{'━'*56}")
    return '\n'.join(L)


def format_compact(symbol: str, sig: dict) -> str:
    """简洁模式输出"""
    if 'error' in sig:
        return f"❌ {symbol}: {sig['error']}"

    active = []
    if sig['target']:      active.append('⚪目标')
    if sig['attack']:      active.append('🟢出击')
    if sig['breakout']:    active.append('🔵突破')
    if sig['bull_sticky']: active.append('🔴粘合')
    if sig['zhuang']:      active.append('🟡庄股')
    if sig['golden_bull']: active.append('🐂金牛')

    trend = '🔴↑' if sig['trend_up'] else '🔵↓'
    mom = '↑' if sig['momentum_up'] else '↓'

    line = f"{symbol} {sig['close']} {trend}"
    if active:
        line += f" {' '.join(active)}"
    else:
        line += ' ⚪无信号'

    line += f" 共振:{sig['resonance_score']} RSI14:{sig['rsi_14']} 量:{sig['vol_ratio']}x"

    if sig['track'] > 0:
        line += f" 跟踪:{sig['track']}"
    if sig['gain'] != 0:
        line += f" 涨幅:{sig['gain']:+.2f}%"

    return line


def scan_stocks(symbols: list, verbose: bool = False) -> str:
    results = []
    alerts = []
    for i, sym in enumerate(symbols):
        sym = sym.strip()
        if not sym:
            continue
        klines = fetch_kline(sym)
        if not klines:
            results.append(f"❌ {sym}: 数据获取失败")
            continue
        is_hk = get_stock_code(sym).startswith('hk')
        sig = calc_signals(klines, is_hk=is_hk)

        if verbose:
            results.append(format_result(sym, sig))
        else:
            results.append(format_compact(sym, sig))

        if 'error' not in sig:
            if sig['attack'] or sig['breakout'] or sig['golden_bull']:
                alerts.append(sym)
            if sig['resonance_score'] >= 70:
                alerts.append(f"{sym}(强共振{sig['resonance_score']}分)")

        if i < len(symbols) - 1:
            time.sleep(0.3)

    output = '\n'.join(results)
    if alerts:
        output += f"\n\n🚨 关注标的: {', '.join(alerts)}"
    return output


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("量化信号扫描器 v2 - 多维度共振选股")
        print("")
        print("用法:")
        print("  python3 quant_signal.py 600519 000858        # 批量简洁扫描")
        print("  python3 quant_signal.py --verbose 600519     # 单只详细分析")
        print("  python3 quant_signal.py --json 600519        # JSON输出")
        print("  python3 quant_signal.py --score 600519       # 仅显示共振评分")
        sys.exit(1)

    verbose = '--verbose' in sys.argv
    json_out = '--json' in sys.argv
    score_only = '--score' in sys.argv
    symbols = [a for a in sys.argv[1:] if not a.startswith('--')]

    if not symbols:
        print("❌ 未提供股票代码")
        sys.exit(1)

    if json_out:
        results = []
        for sym in symbols:
            klines = fetch_kline(sym)
            is_hk = get_stock_code(sym).startswith('hk')
            sig = calc_signals(klines, is_hk=is_hk) if klines else {'error': '数据获取失败'}
            results.append({'symbol': sym, 'signals': sig})
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if score_only:
        for sym in symbols:
            klines = fetch_kline(sym)
            is_hk = get_stock_code(sym).startswith('hk')
            sig = calc_signals(klines, is_hk=is_hk) if klines else {'error': '数据获取失败'}
            if 'error' in sig:
                print(f"{sym}: {sig['error']}")
            else:
                print(f"{sym}  共振:{sig['resonance_score']}/100  "
                      f"趋势:{'↑' if sig['trend_up'] else '↓'}  "
                      f"RSI14:{sig['rsi_14']}  "
                      f"动量:{'↑' if sig['momentum_up'] else '↓'}  "
                      f"多周期:{sig['consistency_score']}")
            time.sleep(0.3)
        return

    if len(symbols) == 1 and verbose:
        klines = fetch_kline(symbols[0])
        is_hk = get_stock_code(symbols[0]).startswith('hk')
        sig = calc_signals(klines, is_hk=is_hk) if klines else {'error': '数据获取失败'}
        print(format_result(symbols[0], sig))
    else:
        print(scan_stocks(symbols, verbose=verbose))


if __name__ == '__main__':
    main()
