#!/usr/bin/env python3
"""
Editorial Calendar Generator - 30天编辑日历生成器
Usage: python generate_editorial_calendar.py --brand "品牌名" --pillars "教育,娱乐,转化" --platforms "微信,小红书,抖音"
"""

import argparse
import json
from datetime import date, timedelta
import csv
import sys
import io

# Windows 编码兼容
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PILLAR_FORMATS = {
    "教育": ["长文", "图文教程", "视频教程", "信息图表"],
    "娱乐": ["短视频", "故事帖", "表情包图文", "直播片段"],
    "启发": ["行业洞察文", "数据报告", "观点文", "播客"],
    "转化": ["产品介绍", "案例故事", "优惠活动", "用户证言"],
    "互动": ["投票/问答", "挑战话题", "UGC征集", "Q&A"],
}

PLATFORM_FREQUENCY = {
    "微信": 2,
    "小红书": 5,
    "抖音": 4,
    "视频号": 3,
    "LinkedIn": 3,
    "博客": 2,
    "播客": 1,
}

def generate_calendar(brand, pillars, platforms, start_date=None, days=30):
    if not start_date:
        start_date = date.today()
    
    pillars_list = [p.strip() for p in pillars.split(",")]
    platforms_list = [p.strip() for p in platforms.split(",")]
    
    calendar = []
    current_date = start_date
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # 周末减少发布
        is_weekend = current_date.weekday() >= 5
        
        for platform in platforms_list:
            freq = PLATFORM_FREQUENCY.get(platform, 3)
            # 简单分配：按频率决定是否发布
            if is_weekend and freq < 4:
                continue
            if day % max(1, 7 // freq) != 0:
                continue
            
            # 轮换支柱
            pillar = pillars_list[day % len(pillars_list)]
            formats = PILLAR_FORMATS.get(pillar, ["图文"])
            content_format = formats[day % len(formats)]
            
            calendar.append({
                "日期": current_date.strftime("%Y-%m-%d"),
                "星期": ["周一","周二","周三","周四","周五","周六","周日"][current_date.weekday()],
                "平台": platform,
                "内容支柱": pillar,
                "格式": content_format,
                "主题/标题": f"[{brand}] {pillar}类内容 - 待定",
                "状态": "待策划",
                "负责人": "",
                "备注": "",
            })
    
    return calendar


def save_csv(calendar, filename="editorial_calendar.csv"):
    if not calendar:
        print("没有生成任何日历条目")
        return
    
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=calendar[0].keys())
        writer.writeheader()
        writer.writerows(calendar)
    print(f"✅ 日历已保存至: {filename}")
    print(f"   共 {len(calendar)} 条内容计划")


def save_json(calendar, filename="editorial_calendar.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(calendar, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 已保存至: {filename}")


def main():
    parser = argparse.ArgumentParser(description="30天编辑日历生成器")
    parser.add_argument("--brand", required=True, help="品牌名称")
    parser.add_argument("--pillars", default="教育,娱乐,启发,转化,互动", help="内容支柱（逗号分隔）")
    parser.add_argument("--platforms", default="微信,小红书,抖音", help="发布平台（逗号分隔）")
    parser.add_argument("--days", type=int, default=30, help="天数（默认30天）")
    parser.add_argument("--output", default="csv", choices=["csv", "json", "both"], help="输出格式")
    parser.add_argument("--filename", default="editorial_calendar", help="输出文件名（不含扩展名）")
    
    args = parser.parse_args()
    
    print(f"🚀 正在生成 {args.brand} 的 {args.days} 天编辑日历...")
    print(f"   支柱: {args.pillars}")
    print(f"   平台: {args.platforms}")
    print()
    
    calendar = generate_calendar(
        brand=args.brand,
        pillars=args.pillars,
        platforms=args.platforms,
        days=args.days
    )
    
    if args.output in ("csv", "both"):
        save_csv(calendar, f"{args.filename}.csv")
    if args.output in ("json", "both"):
        save_json(calendar, f"{args.filename}.json")
    
    # 打印前5条预览
    print("\n📋 前5条预览：")
    for item in calendar[:5]:
        print(f"  {item['日期']} {item['星期']} | {item['平台']} | {item['内容支柱']} | {item['格式']}")


if __name__ == "__main__":
    main()
