#!/usr/bin/env python3
"""MACD 自计算工具 — Sina K-line → DIF/DEA/Hist + 红绿柱判定 + 6 指数批量计算

【用途】
Sina K-line API (https://money.finance.sina.com.cn/.../CN_MarketData.getKLineData)
只返回 OHLCV 原始数据, 不返回 MACD DIF / DEA / Hist 字段。
本脚本从 Sina K-line 自计算 MACD, 用于 A 股 6 大指数技术信号分析。

【数据状态 — 重要警告 (2026-06-22 实测建立)】
- Sina K-line 是 T+1 更新机制, **datalen=15 在收盘任务 (15:05 cron) 抓取时实际只返回到 T-2**
- 6/22 (周一) 实测返回到 6/18 (周四) — 缺失 6/19 (周五) 和 6/22 (周一) 两根 K 线
- **报告中所有 Sina MACD 数据应标注"MACD 反映 T-1 (实际 Sina 滞后 2 天到 T-2)"**
- 如果需要 T-0 实时 close, 必须配合腾讯 qt.gtimg.cn (T-0 实时)

【用法】
    # 单指数计算
    python3 scripts/macd_self_calc.py sh000688
    
    # 6 指数批量
    python3 scripts/macd_self_calc.py --batch
    
    # JSON 输出
    python3 scripts/macd_self_calc.py sh000688 --json

【历史】
- 2026-06-22 首次创建 — 替换 akshare MACD 接口 (实测返回空 DataFrame)
- 关联: lark-stock-report skill §0 (V-reversal 9 模式判定) + references/a-stock-data-fetch-pitfalls.md §35/§37
"""

import argparse
import json
import sys
import urllib.request


# 6 大指数 (代码 → 名称) — 与 cron 任务固定抓取范围一致
INDICES_6 = {
    'sh000001': '上证指数',
    'sz399001': '深证成指',
    'sz399006': '创业板指',
    'sh000688': '科创50',
    'sz399005': '中小100',
    'sz399300': '沪深300',
}


def ema(data, period):
    """EMA 计算 (递推式, 起始为第一个数据点)

    Args:
        data: list[float], 价格序列
        period: int, EMA 周期 (12 / 26)

    Returns:
        list[float], EMA 序列
    """
    ema_list = [data[0]]
    k = 2 / (period + 1)
    for price in data[1:]:
        ema_list.append(price * k + ema_list[-1] * (1 - k))
    return ema_list


def calc_macd(closes, fast=12, slow=26, signal=9):
    """MACD 三件套: DIF / DEA / Hist

    Args:
        closes: list[float], 收盘价序列, 末尾是最新
        fast: int, EMA 快线周期 (默认 12)
        slow: int, EMA 慢线周期 (默认 26)
        signal: int, 信号线周期 (默认 9)

    Returns:
        list[(dif, dea, hist)], 与 closes 等长
    """
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    dif = [a - b for a, b in zip(ema_fast, ema_slow)]
    dea = ema(dif, signal)
    hist = [(d - e) * 2 for d, e in zip(dif, dea)]
    return list(zip(dif, dea, hist))


def fetch_kline(symbol, datalen=120, scale=240):
    """从 Sina 抓取 K 线数据

    Args:
        symbol: str, 股票/指数代码 (e.g. 'sh000001')
        datalen: int, K 线根数 (默认 120, 半年数据)
        scale: int, K 线周期 (默认 240 = 日线)

    Returns:
        list[dict], Sina K-line dict list
        ⚠️ Sina 返回 dict list, 不是 tuple list
        [{'day': '2026-05-15', 'open': 1800.0, 'high': 1820.0, ...}, ...]
    """
    url = (
        f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
        f"CN_MarketData.getKLineData?symbol={symbol}&scale={scale}&ma=no&datalen={datalen}"
    )
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read().decode('gbk', errors='replace')
    return json.loads(raw)


def macd_status(dif, dea, hist):
    """MACD 形态判定

    Args:
        dif: float, 最新 DIF
        dea: float, 最新 DEA (信号线)
        hist: float, 最新 MACD 柱

    Returns:
        dict: {bar: str, dif_vs_dea: str, interpretation: str}
    """
    # 红绿柱判定 (A 股惯例: Hist > 0 = 红柱多头, Hist < 0 = 绿柱空头)
    if hist > 0:
        bar = "红柱 (多头)"
    elif hist < 0:
        bar = "绿柱 (空头)"
    else:
        bar = "零轴"

    # DIF vs DEA 关系
    if dif > dea:
        dif_vs_dea = "DIF 在 DEA 之上 (多头延续)"
    elif dif < dea:
        dif_vs_dea = "DIF 在 DEA 之下 (空头延续)"
    else:
        dif_vs_dea = "DIF = DEA (零轴)"

    # 整体解读
    if hist > 0 and dif > dea:
        interpretation = "强多头"
    elif hist > 0 and dif < 0:
        interpretation = "绿柱转红, 多头修复中 (金叉确认)"
    elif hist > 0 and dif < dea:
        interpretation = "红柱但 DIF 在 DEA 下 (弱势多头)"
    elif hist < 0 and dif > dea:
        interpretation = "红柱转绿, 多头减弱 (死叉确认)"
    elif hist < 0 and dif < 0:
        interpretation = "强空头"
    elif hist < 0 and dif > 0:
        interpretation = "绿柱但 DIF 在 DEA 上 (弱势空头)"
    else:
        interpretation = "中性"

    return {
        "bar": bar,
        "dif_vs_dea": dif_vs_dea,
        "interpretation": interpretation,
    }


def calc_one(symbol, datalen=120):
    """单指数 MACD 计算完整流程

    Returns:
        dict: {
            'symbol': str,
            'latest_dif': float,
            'latest_dea': float,
            'latest_hist': float,
            'dif_last3': list[float],
            'macd_hist_last3': list[float],
            'macd_status': dict,
            'data_date': str,  # 最新 K 线日期 (注意是 T-2, 不是 T-0!)
            'note': str,  # 数据状态警告
        }
    """
    data = fetch_kline(symbol, datalen=datalen)
    closes = [float(k['close']) for k in data]
    macd = calc_macd(closes)
    dif, dea, hist = macd[-1]
    status = macd_status(dif, dea, hist)

    return {
        'symbol': symbol,
        'name': INDICES_6.get(symbol, symbol),
        'latest_dif': round(dif, 2),
        'latest_dea': round(dea, 2),
        'latest_hist': round(hist, 2),
        'dif_last3': [round(d, 2) for d in [m[0] for m in macd[-3:]]],
        'macd_hist_last3': [round(h, 2) for h in [m[2] for m in macd[-3:]]],
        'macd_status': status,
        'data_date': data[-1]['day'],  # Sina 返回的最早可观察日期
        'note': (
            '⚠️ Sina K-line 滞后 2 天 (T-2, 收盘 cron 抓取时不包含 T-1 和 T-0); '
            'MACD 反映历史状态, 不是今日实时'
        ),
    }


def calc_batch():
    """6 指数批量计算"""
    results = {}
    for symbol in INDICES_6:
        try:
            results[symbol] = calc_one(symbol)
        except Exception as e:
            results[symbol] = {'symbol': symbol, 'error': str(e)}
    return results


def main():
    parser = argparse.ArgumentParser(description='MACD 自计算工具 (Sina K-line)')
    parser.add_argument('symbol', nargs='?', help='股票/指数代码 (e.g. sh000001)')
    parser.add_argument('--batch', action='store_true', help='6 指数批量计算')
    parser.add_argument('--datalen', type=int, default=120, help='K 线根数 (默认 120)')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    args = parser.parse_args()

    if args.batch:
        result = calc_batch()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            for symbol, data in result.items():
                if 'error' in data:
                    print(f"{data['name']} ({symbol}): ❌ {data['error']}")
                    continue
                print(f"\n{data['name']} ({symbol}) — 数据日期 {data['data_date']}")
                print(f"  DIF  : {data['latest_dif']:+.2f}")
                print(f"  DEA  : {data['latest_dea']:+.2f}")
                print(f"  Hist : {data['latest_hist']:+.2f}")
                print(f"  形态 : {data['macd_status']['interpretation']}")
                print(f"  柱状 : {data['macd_status']['bar']}")
                print(f"  关系 : {data['macd_status']['dif_vs_dea']}")
                print(f"  {data['note']}")
    elif args.symbol:
        result = calc_one(args.symbol, datalen=args.datalen)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"{result['name']} ({result['symbol']}) — 数据日期 {result['data_date']}")
            print(f"  DIF  : {result['latest_dif']:+.2f}")
            print(f"  DEA  : {result['latest_dea']:+.2f}")
            print(f"  Hist : {result['latest_hist']:+.2f}")
            print(f"  形态 : {result['macd_status']['interpretation']}")
            print(f"  柱状 : {result['macd_status']['bar']}")
            print(f"  关系 : {result['macd_status']['dif_vs_dea']}")
            print(f"\n最近 3 期 DIF:    {result['dif_last3']}")
            print(f"最近 3 期 MACD:  {result['macd_hist_last3']}")
            print(f"\n{result['note']}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()