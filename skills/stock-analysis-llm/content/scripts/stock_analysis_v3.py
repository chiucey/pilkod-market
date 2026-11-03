#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents V3 - LLM驱动辩论系统
"""

import urllib.request
import ssl
import json
import sys
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

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
            'volume': int(data[6]), 'turnover': float(data[38]),
            'pe': float(data[39]) if data[39] else 0,
            'roe': float(data[46]) if data[46] else 0,
            'high_52w': float(data[47]) if data[47] else 0,
            'low_52w': float(data[48]) if data[48] else 0,
            'change': float(data[3]) - float(data[4]),
            'change_pct': (float(data[3]) - float(data[4])) / float(data[4]) * 100 if float(data[4]) > 0 else 0,
        }
    except Exception as e:
        return {'error': str(e)}

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
                    kline_data.append({'date': k[0], 'close': float(k[2]), 'volume': int(float(k[5]))})
        return kline_data
    except:
        return []

def get_market_news():
    url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('utf-8')
        data = json.loads(content.replace('var ajaxResult=', ''))
        return [item.get('title', '') for item in data.get('LivesList', [])[:5]]
    except:
        return []

def run_analysis(stock_code):
    print("=" * 70)
    print(f"🤖 TradingAgents V3 - LLM驱动辩论系统")
    print("=" * 70)
    
    realtime = get_realtime_data(stock_code)
    klines = get_kline_history(stock_code, 60)
    news = get_market_news()
    
    if 'error' in realtime:
        print(f"错误: {realtime['error']}")
        return
    
    # 计算技术指标
    ma5 = ma10 = ma20 = avg_vol = last5_vol = price_20d = 0
    if len(klines) >= 20:
        ma5 = sum(k['close'] for k in klines[-5:]) / 5
        ma10 = sum(k['close'] for k in klines[-10:]) / 10
        ma20 = sum(k['close'] for k in klines[-20:]) / 20
        avg_vol = sum(k['volume'] for k in klines[-20:]) / 20
        last5_vol = sum(k['volume'] for k in klines[-5:]) / 5
        price_20d = (klines[-1]['close'] - klines[-20]['close']) / klines[-20]['close'] * 100
    
    r = realtime
    emoji = "🟢" if r['change'] >= 0 else "🔴"
    
    print(f"\n📊 {r['name']} ({stock_code})")
    print(f"   价格: ¥{r['current']:.2f} {emoji} {r['change_pct']:+.2f}%")
    print(f"   MA5: ¥{ma5:.2f} | MA10: ¥{ma10:.2f} | MA20: ¥{ma20:.2f}")
    print(f"   PE: {r['pe']:.1f} | ROE: {r['roe']:.1f}%")
    print(f"   20日涨跌: {price_20d:+.1f}%")
    
    print("\n" + "=" * 70)
    print("⚔️ 启动LLM辩论系统...")
    print("=" * 70)
    
    return {
        'realtime': realtime,
        'technical': {'ma5': ma5, 'ma10': ma10, 'ma20': ma20, 'price_20d': price_20d, 'avg_vol': avg_vol, 'last5_vol': last5_vol},
        'news': news
    }

if __name__ == '__main__':
    code = sys.argv[1] if len(sys.argv) > 1 else '600410'
    run_analysis(code)
