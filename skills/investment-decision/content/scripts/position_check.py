#!/usr/bin/env python3
"""
position_check.py - 持仓检查
检查持仓是否触发止损/回撤条件
"""
import subprocess
import json
from datetime import datetime

API = "https://mkapi2.dfcfs.com/finskillshub/api/claw/mockTrading/positions"

def get_positions():
    """获取模拟账户持仓"""
    try:
        result = subprocess.run(
            ['curl', '-s', API, '-H', f'x-api-key: mkt_rFi5UvWEov4fc_VZB8FojnDxzYCPE5Y8DJEoGgnRTeI'],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        return data.get('data', [])
    except:
        return []

def check_stops(positions):
    """检查是否触发止损/回撤"""
    warnings = []
    for pos in positions:
        name = pos.get('name', pos.get('stockName', '?'))
        cost = pos.get('cost', 0)
        current = pos.get('currentPrice', cost)
        ratio = pos.get('ratio', 0)  # 涨跌幅
        
        # 止损检查
        if ratio <= -5:
            warnings.append(f"⚠️ {name} 触发止损条件（-{abs(ratio):.1f}%）")
        
        # 回撤检查
        # 需要最高价数据，这里简化处理
        
        # 仓位超限检查
        qty = pos.get('qty', 0)
        value = qty * current
        if value > 25000:  # 单只超过25%（总仓10万基准）
            warnings.append(f"⚠️ {name} 仓位超限（持仓¥{value:.0f}）")
    
    return warnings

def main():
    positions = get_positions()
    
    if not positions:
        print("=== 持仓检查 ===")
        print("当前无持仓")
        return
    
    print("=== 持仓检查 ===")
    total_value = 0
    for pos in positions:
        name = pos.get('name', pos.get('stockName', '?'))
        qty = pos.get('qty', 0)
        cost = pos.get('cost', 0)
        current = pos.get('currentPrice', cost)
        ratio = pos.get('ratio', 0)
        
        value = qty * current
        total_value += value
        
        tag = '🔴' if ratio < -3 else ('🟡' if ratio < 0 else '🟢')
        print(f"{tag} {name}: {qty}股 现价{current} 成本{cost} 涨跌{ratio:+.1f}% 市值¥{value:.0f}")
    
    print(f"\n总持仓: ¥{total_value:.0f} 仓位:{total_value/100000*100:.1f}%")
    
    warnings = check_stops(positions)
    if warnings:
        print("\n=== 预警 ===")
        for w in warnings:
            print(w)

if __name__ == '__main__':
    main()
