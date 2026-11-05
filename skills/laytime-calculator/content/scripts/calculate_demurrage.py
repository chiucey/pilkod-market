#!/usr/bin/env python3
"""
LAYTIME计算脚本 - 第一轮：累加 + 找滞期点（支持双港）

输入: extracted/judgments1.json
输出: extracted/interim_result.json

功能:
1. 读取第一轮判断结果
2. 累加所有INCL的时间（支持单港/双港）
3. 找到第一条cumulative > allowed_hours的记录
4. 标记滞期点位置
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


def load_json(path):
    """加载JSON文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, path):
    """保存JSON文件"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_exact_demurrage_time(record, hours_into_record):
    """
    计算精确的滞期时间点
    """
    time_range = record.get('time_range', '')
    date = record.get('date', '')
    
    if time_range and date:
        try:
            start_time_str = time_range.split('-')[0]
            # 格式: 1030 -> 10:30
            hour = start_time_str[:2] if len(start_time_str) >= 2 else '00'
            minute = start_time_str[2:] if len(start_time_str) >= 4 else '00'
            
            # 构造datetime
            date_parts = date.split('-')
            dt = datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]), 
                         int(hour), int(minute))
            
            exact_time = dt + timedelta(hours=hours_into_record)
            return exact_time.strftime('%Y-%m-%d %H:%M')
        except:
            pass
    
    return f"{date} {time_range}"


def find_demurrage_point_in_timeline(timeline, allowed_hours, cumulative_offset=0):
    """
    在timeline中找滞期点
    
    参数:
    - timeline: 时间线数组
    - allowed_hours: 允许时间（总允许时间）
    - cumulative_offset: 之前累计的时间（用于多港情况）
    
    返回: demurrage_point信息 或 None
    """
    acc_hours = cumulative_offset
    prev_acc = cumulative_offset
    
    for i, record in enumerate(timeline):
        if record.get('status') == 'INCL':
            prev_acc = acc_hours
            hours = record.get('hours', 0)
            acc_hours += hours
            
            # 检查是否刚超过allowed
            if prev_acc < allowed_hours and acc_hours >= allowed_hours:
                hours_before = allowed_hours - prev_acc
                hours_after = acc_hours - allowed_hours
                
                return {
                    "found": True,
                    "index": i,
                    "date": record.get('date'),
                    "time_range": record.get('time_range'),
                    "event": record.get('event'),
                    "day": record.get('day'),
                    "total_hours_in_record": hours,
                    "hours_before_demurrage": hours_before,
                    "hours_after_demurrage": hours_after,
                    "exact_demurrage_time": calculate_exact_demurrage_time(record, hours_before),
                    "cumulative_at_demurrage": allowed_hours,
                    "cumulative_after_record": acc_hours
                }
    
    return {"found": False, "total_hours": acc_hours}


def process_single_port(judgments_data):
    """处理单港案例"""
    timeline = judgments_data.get('timeline', [])
    allowed_hours = judgments_data.get('allowed_hours', 0)
    
    demurrage_point = find_demurrage_point_in_timeline(timeline, allowed_hours)
    
    # 计算总使用时间
    total_hours = sum(r.get('hours', 0) for r in timeline if r.get('status') == 'INCL')
    
    return {
        "timeline": timeline,
        "demurrage_point": demurrage_point,
        "summary": {
            "allowed_hours": allowed_hours,
            "used_hours": total_hours,
            "exceeded_hours": max(0, total_hours - allowed_hours),
            "saved_hours": max(0, allowed_hours - total_hours)
        }
    }


def process_dual_port(judgments_data):
    """处理双港案例"""
    ports = judgments_data.get('ports', {})
    charter_terms = judgments_data.get('charter_party_terms', {})
    
    # 计算每港的允许时间和使用时间
    port_results = []
    total_allowed = 0
    all_timelines = []  # 合并所有timeline用于找滞期点
    
    for port_key in sorted(ports.keys()):
        port_data = ports[port_key]
        cargo_qty = port_data.get('cargo_quantity_mt', 0)
        rate = charter_terms.get('discharge_rate', {}).get('rate', 8000)
        
        # 单港允许时间（小时）
        port_allowed = (cargo_qty / rate) * 24 if rate > 0 else 0
        total_allowed += port_allowed
        
        # 单港使用时间
        port_timeline = port_data.get('timeline', [])
        port_used = sum(r.get('hours', 0) for r in port_timeline if r.get('status') == 'INCL')
        
        # 添加port_name到每条记录
        for r in port_timeline:
            r['port_name'] = port_data.get('name')
        
        all_timelines.extend(port_timeline)
        
        port_results.append({
            "name": port_data.get('name'),
            "cargo_mt": cargo_qty,
            "allowed_hours": port_allowed,
            "used_hours": port_used,
            "timeline_count": len(port_timeline)
        })
    
    # 在合并的timeline中找滞期点
    demurrage_point = find_demurrage_point_in_timeline(all_timelines, total_allowed, 0)
    
    # 如果找到滞期点，补充port信息
    if demurrage_point['found']:
        idx = demurrage_point['index']
        demurrage_point['port_name'] = all_timelines[idx].get('port_name')
    
    total_used = sum(p['used_hours'] for p in port_results)
    
    return {
        "ports": port_results,
        "demurrage_point": demurrage_point,
        "summary": {
            "allowed_hours": total_allowed,
            "used_hours": total_used,
            "exceeded_hours": max(0, total_used - total_allowed),
            "saved_hours": max(0, total_allowed - total_used)
        }
    }


def main(case_dir):
    """主函数"""
    case_path = Path(case_dir)
    
    # 输入文件
    judgments1_path = case_path / "extracted" / "judgments1.json"
    
    if not judgments1_path.exists():
        print(f"❌ 错误: 找不到 {judgments1_path}")
        sys.exit(1)
    
    # 加载数据
    judgments_data = load_json(judgments1_path)
    
    # 判断是单港还是双港
    if 'ports' in judgments_data and isinstance(judgments_data['ports'], dict):
        print("🚢 检测到双港案例")
        result = process_dual_port(judgments_data)
        case_type = "dual"
    else:
        print("🚢 检测到单港案例")
        result = process_single_port(judgments_data)
        case_type = "single"
    
    # 保存结果
    interim_result = {
        "case_id": judgments_data.get('case_id'),
        "vessel": judgments_data.get('vessel'),
        "case_type": case_type,
        "processed_at": datetime.now().isoformat(),
        **result
    }
    
    output_path = case_path / "extracted" / "interim_result.json"
    save_json(interim_result, output_path)
    
    # 输出摘要
    print(f"\n✅ 第一轮计算完成")
    
    if case_type == "dual":
        for p in result['ports']:
            print(f"   {p['name']}: {p['used_hours']:.2f}h / {p['allowed_hours']:.2f}h")
    
    print(f"   总允许时间: {result['summary']['allowed_hours']:.2f}h")
    print(f"   总使用时间: {result['summary']['used_hours']:.2f}h")
    
    if result['demurrage_point'] and result['demurrage_point']['found']:
        dp = result['demurrage_point']
        print(f"\n   ⚠️ 滞期点:")
        print(f"      港口: {dp.get('port_name', 'N/A')}")
        print(f"      日期: {dp['date']} ({dp.get('day', 'N/A')})")
        print(f"      时间段: {dp['time_range']}")
        print(f"      事件: {dp['event']}")
        print(f"      精确滞期时间: {dp['exact_demurrage_time']}")
        print(f"      该条记录拆分: 前{dp['hours_before_demurrage']:.2f}h + 后{dp['hours_after_demurrage']:.2f}h")
        print(f"      累计达到: {dp['cumulative_at_demurrage']:.2f}h (允许{result['summary']['allowed_hours']:.2f}h)")
    else:
        print(f"\n   ✅ 未滞期，节省: {result['summary']['saved_hours']:.2f}h")
    
    print(f"\n📄 输出: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python calculate_demurrage.py <案例目录>")
        print("示例: python calculate_demurrage.py 用户上传/BAKKEDAL_ZHANGZHOU_JIANGYIN_BARLEY")
        sys.exit(1)
    
    main(sys.argv[1])
