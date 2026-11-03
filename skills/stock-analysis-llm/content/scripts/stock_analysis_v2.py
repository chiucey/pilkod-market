#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents 合并版 V2+V3
- V2: 完整四大分析师 + 辩论机制 + 三方风控（直接输出结论）
- V3: 数据收集模式（返回结构化dict，供LLM深度辩论）

用法:
  python3 stock_analysis_v2.py <代码> [名称]           # V2标准分析
  python3 stock_analysis_v2.py <代码> --llm           # V3数据模式
"""

import urllib.request
import ssl
import json
import sys
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

# ==================== 数据获取 ====================

def get_realtime_data(stock_code):
    market = 'sh' if stock_code.startswith('6') or stock_code.startswith('9') else 'sz'
    url = f"https://qt.gtimg.cn/q={market}{stock_code}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('gbk', errors='ignore')
        data = content.split('=')[1].strip('";').split('~')
        return {
            'code': stock_code, 'name': data[2],
            'current': float(data[3]), 'prev_close': float(data[4]),
            'open': float(data[5]), 'volume': int(data[6]),
            'high': float(data[33]), 'low': float(data[34]),
            'turnover': float(data[38]), 'pe': float(data[39]) if data[39] else 0,
            'total_shares': float(data[43]) if data[43] else 0,
            'float_shares': float(data[44]) if data[44] else 0,
            'bvps': float(data[45]) if data[45] else 0,
            'high_52w': float(data[47]) if data[47] else 0,
            'low_52w': float(data[48]) if data[48] else 0,
            'roe': float(data[46]) if data[46] else 0,
            'change': float(data[3]) - float(data[4]),
            'change_pct': (float(data[3]) - float(data[4])) / float(data[4]) * 100 if float(data[4]) > 0 else 0,
        }
    except Exception as e:
        return {'error': str(e), 'code': stock_code}

def get_kline_history(stock_code, days=60):
    market = 'sh' if stock_code.startswith('6') or stock_code.startswith('9') else 'sz'
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{stock_code},day,,,{days},qfq"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=15)
        content = response.read().decode('utf-8', errors='ignore')
        data = json.loads(content)
        kline_data = []
        if 'data' in data:
            key = f"{market}{stock_code}"
            if key in data['data']:
                for k in data['data'][key].get('qfqday', []):
                    kline_data.append({
                        'date': k[0], 'open': float(k[1]), 'close': float(k[2]),
                        'high': float(k[3]), 'low': float(k[4]),
                        'volume': int(float(k[5])) if len(k) > 5 else 0,
                    })
        return kline_data
    except Exception as e:
        return []

def get_market_news():
    """获取财经新闻（V3新增，东方财富）"""
    url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('utf-8')
        data = json.loads(content.replace('var ajaxResult=', ''))
        news = []
        for item in data.get('LivesList', [])[:8]:
            news.append({
                'title': item.get('title', ''),
                'digest': item.get('digest', '')[:80],
                'time': item.get('showtime', '')[:16]
            })
        return news
    except:
        return []

# ==================== V2 四大分析师 ====================

def market_analyst(klines, realtime):
    latest = klines[-1] if klines else {}
    ma5 = sum(k['close'] for k in klines[-5:]) / 5 if len(klines) >= 5 else 0
    ma10 = sum(k['close'] for k in klines[-10:]) / 10 if len(klines) >= 10 else 0
    ma20 = sum(k['close'] for k in klines[-20:]) / 20 if len(klines) >= 20 else 0
    first = klines[-20] if len(klines) >= 20 else (klines[0] if klines else {})
    price_change_20d = (latest.get('close', 0) - first.get('close', 0)) / first.get('close', 1) * 100 if first else 0
    if ma5 > ma10 > ma20:
        ma_trend = "多头排列 ✅"
    elif ma5 < ma10 < ma20:
        ma_trend = "空头排列 🔴"
    else:
        ma_trend = "震荡整理 📊"
    recent10 = klines[-10:] if len(klines) >= 10 else klines
    return {
        "role": "📊 市场分析师",
        "ma_trend": ma_trend, "ma5": ma5, "ma10": ma10, "ma20": ma20,
        "resistance": max(k['high'] for k in recent10) if recent10 else 0,
        "support": min(k['low'] for k in recent10) if recent10 else 0,
        "price_change_20d": price_change_20d
    }

def sentiment_analyst(klines, realtime):
    if not klines:
        return {"role": "🎭 情绪分析师", "sentiment": "数据不足"}
    avg_vol = sum(k['volume'] for k in klines[-20:]) / 20
    last5_vol = sum(k['volume'] for k in klines[-5:]) / 5
    vol_ratio = last5_vol / avg_vol if avg_vol > 0 else 1
    latest = klines[-1]
    first = klines[-20] if len(klines) >= 20 else klines[0]
    if vol_ratio > 1.5 and latest['close'] > first['close']:
        sentiment = "乐观 - 放量上涨 ✅"
    elif vol_ratio > 1.5 and latest['close'] < first['close']:
        sentiment = "谨慎 - 放量下跌 ⚠️"
    elif vol_ratio < 0.7 and latest['close'] > first['close']:
        sentiment = "疑虑 - 缩量上涨 ⚠️"
    elif vol_ratio < 0.7 and latest['close'] < first['close']:
        sentiment = "悲观 - 缩量下跌 🔴"
    else:
        sentiment = "中性 - 正常量价配合 📊"
    return {"role": "🎭 情绪分析师", "sentiment": sentiment, "vol_ratio": vol_ratio}

def news_analyst(stock_code, realtime):
    current = realtime.get('current', 0)
    high_52w = realtime.get('high_52w', 0)
    low_52w = realtime.get('low_52w', 0)
    if high_52w > 0 and low_52w > 0:
        price_pos = (current - low_52w) / (high_52w - low_52w) * 100
        if price_pos > 80:
            position, advice = "接近52周高点 ⚠️", "注意回调风险"
        elif price_pos < 20:
            position, advice = "接近52周低点 🟢", "关注超跌反弹"
        else:
            position, advice = "52周中性区间 📊", "等待方向明确"
    else:
        position, advice = "数据获取失败", "暂无"
    market_news = get_market_news()
    return {"role": "📰 新闻分析师", "position": position, "advice": advice, "market_news": market_news[:5]}

def fundamentals_analyst(stock_code, realtime):
    pe = realtime.get('pe', 0)
    roe = realtime.get('roe', 0)
    pb = realtime.get('current', 0) / realtime.get('bvps', 1) if realtime.get('bvps', 0) > 0 else 0
    pe_status = "偏低 🟢" if pe < 20 else ("偏高 ⚠️" if pe > 60 else "适中 📊") if pe > 0 else "亏损 🔴"
    roe_status = "优秀 ✅" if roe > 15 else ("一般 📊" if roe > 5 else "较低 ⚠️")
    return {"role": "📈 基本面分析师", "pe": pe, "pe_status": pe_status, "roe": roe, "roe_status": roe_status, "pb": pb}

# ==================== V2 辩论机制 ====================

def bull_researcher(analysts):
    market = analysts.get("market_analyst", {})
    sentiment = analysts.get("sentiment_analyst", {})
    fundamentals = analysts.get("fundamentals_analyst", {})
    reasons = []
    if "多头" in market.get("ma_trend", ""): reasons.append("✅ 均线多头排列")
    if market.get("price_change_20d", 0) > 5: reasons.append(f"✅ 20日涨幅{market.get('price_change_20d', 0):.1f}%")
    if "乐观" in sentiment.get("sentiment", ""): reasons.append("✅ 市场情绪乐观")
    if "优秀" in fundamentals.get("roe_status", ""): reasons.append("✅ ROE表现优秀")
    if not reasons: reasons.append("⚠️ 缺乏明显看多信号")
    return {"role": "🐂 看多研究员", "观点": "建议买入/持有", "理由": reasons}

def bear_researcher(analysts):
    market = analysts.get("market_analyst", {})
    sentiment = analysts.get("sentiment_analyst", {})
    fundamentals = analysts.get("fundamentals_analyst", {})
    reasons = []
    if "空头" in market.get("ma_trend", ""): reasons.append("🔴 均线空头排列")
    if market.get("price_change_20d", 0) < -5: reasons.append(f"🔴 20日跌幅{abs(market.get('price_change_20d', 0)):.1f}%")
    if "亏损" in fundamentals.get("pe_status", ""): reasons.append("🔴 公司亏损")
    if not reasons: reasons.append("⚠️ 缺乏明显看空信号")
    return {"role": "🐻 看空研究员", "观点": "建议观望/卖出", "理由": reasons}

def research_manager(bull, bear):
    bull_score = len([r for r in bull.get("理由", []) if r.startswith("✅")])
    bear_score = len([r for r in bear.get("理由", []) if r.startswith("🔴")])
    if bull_score > bear_score + 1:
        recommendation, confidence = "偏多", "较高"
    elif bear_score > bull_score + 1:
        recommendation, confidence = "偏空", "较高"
    else:
        recommendation, confidence = "中性", "一般"
    return {"role": "📋 研究经理", "裁决": recommendation, "信心度": confidence}

# ==================== V2 三方风控 ====================

def aggressive_analyst(analysts):
    return {"role": "⚡ 激进分析师", "观点": "可以加大仓位", "理由": ["趋势向上，可以做多", "放量上涨，强势信号"]}

def conservative_analyst(analysts):
    return {"role": "🛡️ 保守分析师", "观点": "建议轻仓/观望", "理由": ["控制仓位，谨慎操作", "设置止损保护"]}

def neutral_analyst(analysts):
    return {"role": "⚖️ 中性分析师", "观点": "保持现有仓位", "理由": ["等待趋势明朗", "可以适当做T+0"]}

def risk_manager(aggressive, conservative, neutral):
    votes = {"加仓": 0, "持有": 0, "减仓": 0, "观望": 0}
    for a in [aggressive, conservative, neutral]:
        观点 = a.get("观点", "")
        if "加仓" in 观点 or "加大" in 观点: votes["加仓"] += 1
        elif "减仓" in 观点 or "卖出" in 观点: votes["减仓"] += 1
        elif "持有" in 观点: votes["持有"] += 1
        else: votes["观望"] += 1
    return {"role": "🎯 风控经理", "最终决策": max(votes, key=votes.get), "投票": votes}

# ==================== V2 标准分析报告 ====================

def generate_v2_report(stock_code, stock_name=None):
    print("=" * 70)
    print(f"🤖 TradingAgents V2 - {stock_code} 综合分析")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n📥 Phase 1: 数据采集")
    print("-" * 50)
    realtime = get_realtime_data(stock_code)
    klines = get_kline_history(stock_code, 60)
    if 'error' in realtime:
        print(f"❌ 错误: {realtime['error']}")
        return
    name = stock_name or realtime.get('name', stock_code)
    emoji = "🟢" if realtime['change'] >= 0 else "🔴"
    print(f"📈 {name} ({stock_code})")
    print(f"   价格: ¥{realtime['current']:.2f} {emoji} {realtime['change_pct']:+.2f}%")
    print(f"   数据源: 腾讯财经 + 东方财富")

    print("\n🔍 Phase 2: 四大分析师")
    print("-" * 50)
    market = market_analyst(klines, realtime)
    print(f"\n{market['role']}")
    print(f"   均线: {market['ma_trend']}")
    print(f"   MA5: ¥{market['ma5']:.2f} | MA10: ¥{market['ma10']:.2f} | MA20: ¥{market['ma20']:.2f}")
    print(f"   压力: ¥{market['resistance']:.2f} | 支撑: ¥{market['support']:.2f}")
    sentiment = sentiment_analyst(klines, realtime)
    print(f"\n{sentiment['role']}")
    print(f"   情绪: {sentiment['sentiment']}")
    news = news_analyst(stock_code, realtime)
    print(f"\n{news['role']}")
    print(f"   价位: {news['position']}")
    print(f"   建议: {news['advice']}")
    print("   📰 财经要闻:")
    for i, n in enumerate(news.get('market_news', [])[:3], 1):
        print(f"      {i}. {n.get('title', '')[:60]}")
    fundamentals = fundamentals_analyst(stock_code, realtime)
    print(f"\n{fundamentals['role']}")
    print(f"   市盈率PE: {fundamentals['pe']:.2f} ({fundamentals['pe_status']})")
    print(f"   ROE: {fundamentals['roe']:.2f}% ({fundamentals['roe_status']})")

    print("\n⚔️ Phase 3: 投资辩论")
    print("-" * 50)
    analysts = {"market_analyst": market, "sentiment_analyst": sentiment, "fundamentals_analyst": fundamentals}
    bull = bull_researcher(analysts)
    bear = bear_researcher(analysts)
    manager = research_manager(bull, bear)
    print(f"\n{bull['role']} - {bull['观点']}")
    for r in bull['理由']: print(f"   {r}")
    print(f"\n{bear['role']} - {bear['观点']}")
    for r in bear['理由']: print(f"   {r}")
    print(f"\n{manager['role']}: {manager['裁决']} (信心: {manager['信心度']})")

    print("\n🛡️ Phase 4: 三方风控")
    print("-" * 50)
    agg = aggressive_analyst(analysts)
    cons = conservative_analyst(analysts)
    neut = neutral_analyst(analysts)
    risk = risk_manager(agg, cons, neut)
    print(f"\n{agg['role']}: {agg['观点']}")
    print(f"{cons['role']}: {cons['观点']}")
    print(f"{neut['role']}: {neut['观点']}")
    print(f"\n{risk['role']}: 🏆 {risk['最终决策']}")
    print(f"   投票: {risk['投票']}")

    print("\n" + "=" * 50)
    print("📋 综合结论")
    print("=" * 50)
    print(f"""
┌────────────────────────────────────────────┐
│ 股票: {name} ({stock_code})              │
│ 当前: ¥{realtime['current']:.2f} {realtime['change_pct']:+.2f}%                  │
│ 技术: {market['ma_trend']}          │
│ 情绪: {sentiment['sentiment'].split(' - ')[0]}        │
│ 基本面: PE{realtime['pe']:.1f} ROE{realtime['roe']:.1f}%          │
│ 研究裁决: {manager['裁决']}                        │
│ 风控决策: {risk['最终决策']}                          │
└────────────────────────────────────────────┘
""")

# ==================== V3 LLM数据结构 ====================

def generate_llm_data(stock_code):
    """V3模式：返回结构化数据，供LLM深度辩论"""
    realtime = get_realtime_data(stock_code)
    klines = get_kline_history(stock_code, 60)
    news = get_market_news()
    if 'error' in realtime:
        return {'error': realtime['error']}
    ma5 = ma10 = ma20 = avg_vol = last5_vol = price_20d = 0
    if len(klines) >= 20:
        ma5 = sum(k['close'] for k in klines[-5:]) / 5
        ma10 = sum(k['close'] for k in klines[-10:]) / 10
        ma20 = sum(k['close'] for k in klines[-20:]) / 20
        avg_vol = sum(k['volume'] for k in klines[-20:]) / 20
        last5_vol = sum(k['volume'] for k in klines[-5:]) / 5
        price_20d = (klines[-1]['close'] - klines[-20]['close']) / klines[-20]['close'] * 100
    return {
        'realtime': realtime,
        'technical': {'ma5': ma5, 'ma10': ma10, 'ma20': ma20, 'price_20d': price_20d, 'avg_vol': avg_vol, 'last5_vol': last5_vol},
        'news': [n['title'] for n in news[:8]]
    }

# ==================== 主入口 ====================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 stock_analysis_v2.py <代码> [名称]     # V2标准分析")
        print("  python3 stock_analysis_v2.py <代码> --llm      # V3数据模式")
        sys.exit(1)
    code = sys.argv[1]
    if '--llm' in sys.argv:
        data = generate_llm_data(code)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        name = sys.argv[2] if len(sys.argv) > 2 else None
        generate_v2_report(code, name)
