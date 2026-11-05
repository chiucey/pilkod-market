#!/usr/bin/env python3
"""
LAYTIME计算脚本 - 预处理：拆分复合事件

输入: extracted/sof_parsed.json 或 extracted/judgments.json
输出: extracted/timeline_split.json

功能:
1. 解析复合事件中的下雨时间段
2. 将复合时间段拆分为多个子时间段
3. 标注每个子时间段是否为雨天

示例:
输入: "WAITING FOR CARGO SAMPLING. RAIN: 0000-0200, 0606-1045"
      time_range: "0000-2400"
      
输出: 4条记录
      0000-0200: RAIN (is_rain=True)
      0200-0606: NON-RAIN (is_rain=False)
      0606-1045: RAIN (is_rain=True)
      1045-2400: NON-RAIN (is_rain=False)
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta


def parse_time(time_str):
    """解析时间字符串为分钟数"""
    """0000 → 0, 2400 → 1440"""
    time_str = time_str.strip()
    hours = int(time_str[:2])
    minutes = int(time_str[2:])
    return hours * 60 + minutes


def minutes_to_time(minutes):
    """分钟数转时间字符串"""
    """0 → 0000, 1440 → 2400"""
    if minutes >= 1440:
        return "2400"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}{mins:02d}"


def parse_rain_periods(event_text):
    """
    从事件描述中解析下雨时间段
    
    返回: [(start_minutes, end_minutes), ...]
    """
    rain_periods = []
    
    # 模式1: RAIN: 0000-0200, 0606-1045
    pattern1 = r'RAIN[^:]*:\s*(\d{4}-\d{4}(?:,\s*\d{4}-\d{4})*)'
    match1 = re.search(pattern1, event_text, re.IGNORECASE)
    
    if match1:
        periods_str = match1.group(1)
        for period in periods_str.split(','):
            period = period.strip()
            if '-' in period:
                start, end = period.split('-')
                start_min = parse_time(start)
                end_min = parse_time(end)
                rain_periods.append((start_min, end_min))
    
    # 模式2: RAIN FROM 1700-2015
    pattern2 = r'RAIN\s+FROM\s+(\d{4})-(\d{4})'
    match2 = re.search(pattern2, event_text, re.IGNORECASE)
    
    if match2:
        start_min = parse_time(match2.group(1))
        end_min = parse_time(match2.group(2))
        rain_periods.append((start_min, end_min))
    
    # 模式3: RAIN PERIODS: 0015-0220, 0312-0430
    pattern3 = r'RAIN\s+PERIODS?:\s*(\d{4}-\d{4}(?:,\s*\d{4}-\d{4})*)'
    match3 = re.search(pattern3, event_text, re.IGNORECASE)
    
    if match3:
        periods_str = match3.group(1)
        for period in periods_str.split(','):
            period = period.strip()
            if '-' in period:
                start, end = period.split('-')
                start_min = parse_time(start)
                end_min = parse_time(end)
                rain_periods.append((start_min, end_min))
    
    # 合并重叠时间段
    rain_periods.sort()
    merged = []
    for start, end in rain_periods:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    
    return merged


def split_time_range(time_range, rain_periods):
    """
    将时间段按下雨时间拆分
    
    返回: [{"time_range": "0000-0200", "hours": 2.0, "is_rain": True}, ...]
    """
    start_str, end_str = time_range.split('-')
    start_min = parse_time(start_str)
    end_min = parse_time(end_str)
    
    segments = []
    current = start_min
    
    for rain_start, rain_end in rain_periods:
        # 跳过完全在时间段之前的下雨
        if rain_end <= current:
            continue
        
        # 截断到当前时间段范围内
        rain_start = max(rain_start, current)
        rain_end = min(rain_end, end_min)
        
        if rain_start > current:
            # 非下雨时间段
            segments.append({
                "time_range": f"{minutes_to_time(current)}-{minutes_to_time(rain_start)}",
                "hours": (rain_start - current) / 60,
                "is_rain": False
            })
        
        if rain_end > rain_start:
            # 下雨时间段
            segments.append({
                "time_range": f"{minutes_to_time(rain_start)}-{minutes_to_time(rain_end)}",
                "hours": (rain_end - rain_start) / 60,
                "is_rain": True
            })
        
        current = rain_end
    
    # 最后一段非下雨时间
    if current < end_min:
        segments.append({
            "time_range": f"{minutes_to_time(current)}-{minutes_to_time(end_min)}",
            "hours": (end_min - current) / 60,
            "is_rain": False
        })
    
    return segments


def process_record(record):
    """
    处理单条记录，拆分复合事件
    
    返回: [拆分后的记录]
    """
    event = record.get('event', '')
    time_range = record.get('time_range', '')
    hours = record.get('hours', 0)
    
    rain_periods = parse_rain_periods(event)
    
    if not rain_periods:
        # 无复合事件，直接返回
        record['is_rain'] = 'RAIN' in event.upper() or 'SUSPENDED DISCHARGE DUE TO RAIN' in event
        return [record]
    
    # 有下雨时间段，拆分
    segments = split_time_range(time_range, rain_periods)
    
    if not segments:
        return [record]
    
    new_records = []
    for seg in segments:
        new_record = record.copy()
        new_record['time_range'] = seg['time_range']
        new_record['hours'] = round(seg['hours'], 2)
        new_record['is_rain'] = seg['is_rain']
        new_record['original_event'] = event
        new_record['split_from'] = time_range
        
        if seg['is_rain']:
            new_record['event'] = f"RAIN DURING {event.split('.')[0]}"
        else:
            new_record['event'] = event.split('.')[0].strip()
        
        new_records.append(new_record)
    
    return new_records


def process_timeline(timeline):
    """处理整个timeline"""
    new_timeline = []
    
    for record in timeline:
        split_records = process_record(record)
        new_timeline.extend(split_records)
    
    return new_timeline


def process_single_port(data):
    """处理单港案例"""
    if 'timeline' in data:
        data['timeline'] = process_timeline(data['timeline'])
    return data


def process_dual_port(data):
    """处理双港案例"""
    if 'ports' in data:
        for port_key in data['ports']:
            if 'timeline' in data['ports'][port_key]:
                data['ports'][port_key]['timeline'] = process_timeline(
                    data['ports'][port_key]['timeline']
                )
    return data


def main(case_dir):
    """主函数"""
    case_path = Path(case_dir)
    extracted_dir = case_path / 'extracted'
    
    # 读取输入文件
    input_file = None
    if (extracted_dir / 'judgments.json').exists():
        input_file = extracted_dir / 'judgments.json'
    elif (extracted_dir / 'sof_parsed.json').exists():
        input_file = extracted_dir / 'sof_parsed.json'
    else:
        print("❌ 找不到输入文件")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 判断单港还是双港
    if 'ports' in data:
        data = process_dual_port(data)
        print("🚢 双港案例拆分完成")
    else:
        data = process_single_port(data)
        print("🚢 单港案例拆分完成")
    
    # 保存
    output_file = extracted_dir / 'timeline_split.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 拆分完成，输出: {output_file}")
    
    # 统计拆分情况
    if 'ports' in data:
        total_orig = 0
        total_split = 0
        for port_key in data['ports']:
            timeline = data['ports'][port_key].get('timeline', [])
            split_count = sum(1 for r in timeline if 'split_from' in r)
            total_split += split_count
            total_orig += len(timeline) - split_count + len(set(r.get('split_from') for r in timeline if 'split_from' in r))
        print(f"   原始记录: {total_orig} 条")
        print(f"   拆分后: {len(data['ports'][list(data['ports'].keys())[0]].get('timeline', []))} 条")
    else:
        timeline = data.get('timeline', [])
        split_count = sum(1 for r in timeline if 'split_from' in r)
        print(f"   原始记录: {len(timeline) - split_count + len(set(r.get('split_from') for r in timeline if 'split_from' in r))} 条")
        print(f"   拆分后: {len(timeline)} 条")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python preprocess_timeline.py <案例目录>")
        sys.exit(1)
    
    main(sys.argv[1])
