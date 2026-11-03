#!/usr/bin/env python3
"""
LAYTIME计算脚本 - 第二轮：滞期后重新判断

输入: extracted/judgments1.json + extracted/interim_result.json
输出: extracted/judgments2.json

功能:
1. 读取滞期点信息
2. 滞期点之前的记录：保持不变
3. 滞期点那条记录：拆分（如果需要）
4. 滞期点之后的记录：应用"一旦滞期永久滞期"规则
   - 周末/节假日 → INCL
   - 雨天 → INCL
   - Shifting → 保持 EXCL
   - reason 改为 "On Demurrage"
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_json(path):
    """加载JSON文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, path):
    """保存JSON文件"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_always_excluded(event):
    """
    判断事件是否在滞期期间也排除
    
    这些事件即使在滞期期间也不计入：
    - Shifting（移泊）
    - 船东原因延误
    """
    event_lower = event.lower()
    always_excluded_keywords = [
        'anchor aweigh',
        'pilot on board',
        'proceeded to',
        'first line ashore',
        'all made fast',
        'shifting',
        'owner',
        'engine trouble',
        'crew',
    ]
    
    for keyword in always_excluded_keywords:
        if keyword in event_lower:
            return True
    
    return False


def process_record_after_demurrage(record, dp_info):
    """
    处理滞期点之后的记录
    
    返回: 处理后的记录
    """
    new_record = record.copy()
    
    # 如果是永远排除的事件，保持EXCL
    if is_always_excluded(record.get('event', '')):
        new_record['status'] = 'EXCL'
        new_record['reason'] = f"Excluded even on demurrage - {record.get('reason', '')}"
        new_record['on_demurrage'] = False
    else:
        # 其他情况：计入（周末/节假日/雨天都计入）
        new_record['status'] = 'INCL'
        new_record['reason'] = f"On Demurrage - {record.get('event', '')}"
        new_record['on_demurrage'] = True
    
    return new_record


def split_demurrage_record(record, hours_before, hours_after, dp_time):
    """
    拆分滞期点那条记录
    
    返回: [前半段, 后半段]
    """
    part1 = record.copy()
    part1['hours'] = hours_before
    part1['status'] = 'INCL'
    part1['reason'] = f"⚠️ DEMURRAGE STARTED at {dp_time}. {record.get('reason', '')}"
    part1['is_demurrage_point'] = True
    
    part2 = record.copy()
    part2['hours'] = hours_after
    part2['status'] = 'INCL'
    part2['reason'] = f"On Demurrage - {record.get('event', '')}"
    part2['on_demurrage'] = True
    
    return [part1, part2]


def process_single_port(judgments_data, interim_result):
    """处理单港案例"""
    timeline = judgments_data.get('timeline', [])
    dp = interim_result.get('demurrage_point', {})
    
    if not dp.get('found'):
        # 没有滞期，直接返回
        return {"timeline": timeline}
    
    dp_index = dp['index']
    hours_before = dp['hours_before_demurrage']
    hours_after = dp['hours_after_demurrage']
    dp_time = dp['exact_demurrage_time']
    
    new_timeline = []
    
    for i, record in enumerate(timeline):
        if i < dp_index:
            # 滞期点之前：保持不变
            new_timeline.append(record)
        elif i == dp_index:
            # 滞期点那条记录：拆分
            parts = split_demurrage_record(record, hours_before, hours_after, dp_time)
            new_timeline.extend(parts)
        else:
            # 滞期点之后：重新判断
            new_record = process_record_after_demurrage(record, dp)
            new_timeline.append(new_record)
    
    return {"timeline": new_timeline}


def process_dual_port(judgments_data, interim_result):
    """处理双港案例"""
    ports = judgments_data.get('ports', {})
    dp = interim_result.get('demurrage_point', {})
    
    if not dp.get('found'):
        # 没有滞期，直接返回
        return {"ports": ports}
    
    dp_index = dp['index']
    dp_port = dp.get('port_name')
    hours_before = dp['hours_before_demurrage']
    hours_after = dp['hours_after_demurrage']
    dp_time = dp['exact_demurrage_time']
    
    # 合并所有timeline
    all_timelines = []
    port_info = []  # 记录每个port的timeline起止索引
    
    for port_key in sorted(ports.keys()):
        port_data = ports[port_key]
        port_name = port_data.get('name')
        start_idx = len(all_timelines)
        port_timeline = port_data.get('timeline', [])
        
        for r in port_timeline:
            r['port_name'] = port_name
        
        all_timelines.extend(port_timeline)
        end_idx = len(all_timelines)
        
        port_info.append({
            'key': port_key,
            'name': port_name,
            'start_idx': start_idx,
            'end_idx': end_idx
        })
    
    # 处理timeline
    new_all_timelines = []
    
    for i, record in enumerate(all_timelines):
        if i < dp_index:
            # 滞期点之前：保持不变
            new_all_timelines.append(record)
        elif i == dp_index:
            # 滞期点那条记录：拆分
            parts = split_demurrage_record(record, hours_before, hours_after, dp_time)
            new_all_timelines.extend(parts)
        else:
            # 滞期点之后：重新判断
            new_record = process_record_after_demurrage(record, dp)
            new_all_timelines.append(new_record)
    
    # 重新分配到各个port
    new_ports = {}
    for info in port_info:
        port_key = info['key']
        new_ports[port_key] = {
            "name": info['name'],
            "cargo_quantity_mt": ports[port_key].get('cargo_quantity_mt'),
            "nor_tendered": ports[port_key].get('nor_tendered'),
            "laytime_commenced": ports[port_key].get('laytime_commenced'),
            "discharge_completed": ports[port_key].get('discharge_completed'),
            "timeline": new_all_timelines[info['start_idx']:info['end_idx']]
        }
    
    return {"ports": new_ports}


def main(case_dir):
    """主函数"""
    case_path = Path(case_dir)
    
    # 输入文件
    judgments1_path = case_path / "extracted" / "judgments1.json"
    interim_path = case_path / "extracted" / "interim_result.json"
    
    if not judgments1_path.exists():
        print(f"❌ 错误: 找不到 {judgments1_path}")
        sys.exit(1)
    
    if not interim_path.exists():
        print(f"❌ 错误: 找不到 {interim_path}")
        print("   请先运行 calculate_demurrage.py")
        sys.exit(1)
    
    # 加载数据
    judgments_data = load_json(judgments1_path)
    interim_result = load_json(interim_path)
    
    # 处理
    if 'ports' in judgments_data and isinstance(judgments_data['ports'], dict):
        print("🚢 处理双港案例")
        result = process_dual_port(judgments_data, interim_result)
        case_type = "dual"
    else:
        print("🚢 处理单港案例")
        result = process_single_port(judgments_data, interim_result)
        case_type = "single"
    
    # 保存
    judgments2 = {
        "case_id": judgments_data.get('case_id'),
        "vessel": judgments_data.get('vessel'),
        "voyage": judgments_data.get('voyage'),
        "charter_party_terms": judgments_data.get('charter_party_terms'),
        "notes": judgments_data.get('notes'),
        "processed_at": datetime.now().isoformat(),
        **result
    }
    
    output_path = case_path / "extracted" / "judgments2.json"
    save_json(judgments2, output_path)
    
    # 输出摘要
    dp = interim_result.get('demurrage_point', {})
    if dp.get('found'):
        print(f"\n✅ 第二轮判断完成")
        print(f"   滞期点: {dp['exact_demurrage_time']}")
        print(f"   滞期点后记录已重新判断")
        print(f"   - 周末/节假日/雨天: 计入")
        print(f"   - Shifting等: 保持排除")
    else:
        print(f"\n✅ 未滞期，无需重新判断")
    
    print(f"\n📄 输出: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python apply_demurrage_rules.py <案例目录>")
        print("示例: python apply_demurrage_rules.py 用户上传/BAKKEDAL_ZHANGZHOU_JIANGYIN_BARLEY")
        sys.exit(1)
    
    main(sys.argv[1])
