#!/usr/bin/env python3
"""
daily_review.py - 收盘复盘
记录当日操作，更新持仓成本，生成复盘笔记
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path('/workspace/memory')
TODAY = datetime.now().strftime('%Y-%m-%d')

TRADE_LOG = MEMORY_DIR / 'trade_log.json'
DAILY_TEMPLATE = MEMORY_DIR / f'{TODAY}-review.md'

POSITIONS_TEMPLATE = """
# {date} 收盘复盘

## 当日操作记录
{operations}

## 持仓状况
{positions}

## 情绪罗盘
- 收盘情绪：{emotion}分
- 主线板块：{theme}
- 仓位：{position}%

## 明日计划
{plans}

## 涟漪笔记
{notes}
"""

def load_trade_log():
    if TRADE_LOG.exists():
        with open(TRADE_LOG) as f:
            return json.load(f)
    return []

def save_trade_log(log):
    with open(TRADE_LOG, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def append_review(review_text):
    DAILY_TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    with open(DAILY_TEMPLATE, 'w') as f:
        f.write(review_text)

def main():
    print(f"=== {TODAY} 收盘复盘 ===")
    
    # 加载当日记录
    log = load_trade_log()
    today_ops = [op for op in log if op.get('date', '') == TODAY]
    
    if today_ops:
        print(f"今日操作：{len(today_ops)}笔")
        for op in today_ops:
            print(f"  - {op['action']}: {op.get('detail', '')}")
    else:
        print("今日无操作")
    
    # 生成复盘模板（供涟漪填写）
    review = POSITIONS_TEMPLATE.format(
        date=TODAY,
        operations='\n'.join([f"- {op['action']}: {op.get('detail','')}" for op in today_ops]) or "今日无操作",
        positions="见模拟账户",
        emotion="[待填写]",
        theme="[待填写]",
        position="[待填写]",
        plans="[涟漪填写：明日操作计划]",
        notes="[涟漪填写：今日心得/教训]"
    )
    
    append_review(review)
    print(f"\n复盘模板已保存：{DAILY_TEMPLATE}")
    print("请涟漪补充：情绪评分、主线、操作计划、心得")

if __name__ == '__main__':
    main()
