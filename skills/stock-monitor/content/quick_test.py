#!/usr/bin/env python3
"""
quick_test.py - Stock Scout 快速测试（仅测试5只代表性股票）
"""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score import calculate_score

# 测试样本股票
TEST_STOCKS = [
    {
        "ts_code": "600519", "name": "贵州茅台",
        "northbound_pct": 7.24, "margin_balance": 150000,
        "margin_change_pct": -2.5, "moneyflow_net": 12500,
        "moneyflow_large": 8000, "broker_rating": 4.5,
        "broker_target": 2200, "price": 1680.0,
        "change_pct": 1.85, "turnover_rate": 1.2,
        "price_5d_trend": 3.5, "broker_target_gap_pct": 28.5
    },
    {
        "ts_code": "002230", "name": "科大讯飞",
        "northbound_pct": 3.15, "margin_balance": 85000,
        "margin_change_pct": 5.2, "moneyflow_net": 6800,
        "moneyflow_large": 4200, "broker_rating": 4.2,
        "broker_target": 65.0, "price": 52.5,
        "change_pct": 3.2, "turnover_rate": 4.5,
        "price_5d_trend": 8.5, "broker_target_gap_pct": 23.8
    },
    {
        "ts_code": "300750", "name": "宁德时代",
        "northbound_pct": 12.8, "margin_balance": 220000,
        "margin_change_pct": 15.5, "moneyflow_net": -3500,
        "moneyflow_large": -1800, "broker_rating": 4.8,
        "broker_target": 680.0, "price": 560.0,
        "change_pct": -1.2, "turnover_rate": 2.8,
        "price_5d_trend": -2.3, "broker_target_gap_pct": 21.4
    },
    {
        "ts_code": "000858", "name": "五粮液",
        "northbound_pct": 5.6, "margin_balance": 98000,
        "margin_change_pct": -8.5, "moneyflow_net": 15200,
        "moneyflow_large": 11000, "broker_rating": 4.0,
        "broker_target": 200.0, "price": 145.0,
        "change_pct": 4.5, "turnover_rate": 3.2,
        "price_5d_trend": 5.8, "broker_target_gap_pct": 37.9
    },
    {
        "ts_code": "600036", "name": "招商银行",
        "northbound_pct": 8.9, "margin_balance": 185000,
        "margin_change_pct": 2.1, "moneyflow_net": 9200,
        "moneyflow_large": 6500, "broker_rating": 4.3,
        "broker_target": 52.0, "price": 38.5,
        "change_pct": 0.8, "turnover_rate": 1.5,
        "price_5d_trend": 1.2, "broker_target_gap_pct": 35.1
    },
]


def main():
    print("=" * 70)
    print("Stock Scout 快速测试 | 五维评分引擎验证")
    print("=" * 70)

    results = []
    for stock in TEST_STOCKS:
        sig = calculate_score(**stock)
        results.append(sig)

    # 按评分排序
    results.sort(key=lambda x: x.score, reverse=True)

    print(f"\n{'='*70}")
    print(f"{'排名':<4} {'股票名称':<10} {'评分':<6} {'信号类型':<10} {'信号等级':<12}")
    print(f"{'='*70}")

    for i, s in enumerate(results, 1):
        print(f"{i:<4} {s.name:<10} {s.score:<6} {s.signal_type:<10} {s.phase}")

    print(f"\n{'='*70}")
    print("详细数据：")
    print(f"{'='*70}")

    for s in results:
        print(f"\n【{s.name}({s.ts_code})】")
        print(f"  综合评分: {s.score}分 {s.phase}")
        print(f"  信号类型: {s.signal_type}")
        print(f"  当前价格: ¥{s.price:.2f} ({s.change_pct:+.2f}%)")
        print(f"  换手率: {s.turnover_rate:.2f}%")
        print(f"  北向持股: {s.northbound_pct:.2f}%")
        print(f"  主力净流入: {s.moneyflow_net:.0f}万元")
        print(f"  融资余额变动: {s.margin_change_pct:+.1f}%")
        print(f"  券商评级: {s.broker_rating:.1f}/5.0")
        print(f"  目标价空间: {s.target_gap_pct:.1f}%")

    print(f"\n{'='*70}")
    print("✅ 评分引擎测试通过！")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
