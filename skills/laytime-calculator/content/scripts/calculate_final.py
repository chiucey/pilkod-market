#!/usr/bin/env python3
"""
LAYTIME计算脚本 - 最终计算（支持双港）

输入: extracted/judgments_final.json 或 extracted/judgments2.json
输出: calculation/result.json

功能:
1. 读取最终判断结果
2. 累加所有INCL的时间
3. 计算滞期费/速遣费
4. 输出标准result.json
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


def process_single_port(judgments_data, contract_data=None):
    """处理单港案例"""
    timeline = judgments_data.get('timeline', [])
    allowed_hours = judgments_data.get('allowed_hours', 0)
    
    # 累加时间
    acc_hours = 0
    final_timeline = []
    demurrage_info = None
    
    for i, record in enumerate(timeline):
        final_record = {
            "date": record.get('date'),
            "day": record.get('day'),
            "time_range": record.get('time_range'),
            "event": record.get('event'),
            "hours": record.get('hours'),
            "status": record.get('status'),
            "reason": record.get('reason'),
            "count_h": None,
            "cumulative": None
        }
        
        if record.get('status') == 'INCL':
            prev_acc = acc_hours
            acc_hours += record.get('hours', 0)
            final_record['count_h'] = record.get('hours')
            final_record['cumulative'] = acc_hours
            
            # 检查是否是滞期点
            if record.get('is_demurrage_point'):
                demurrage_info = {
                    "demurrage_point_date": record.get('date'),
                    "demurrage_point_time": record.get('time_range'),
                    "hours_at_demurrage": allowed_hours
                }
        else:
            final_record['cumulative'] = acc_hours
        
        if record.get('user_modified'):
            final_record['user_modified'] = True
        
        final_timeline.append(final_record)
    
    # 计算费率
    demurrage_rate = judgments_data.get('demurrage_rate', 0)
    despatch_rate = judgments_data.get('despatch_rate', 0)
    if contract_data:
        demurrage_rate = contract_data.get('demurrage_rate', demurrage_rate)
        despatch_rate = contract_data.get('despatch_rate', despatch_rate)
    
    # 计算结果
    if acc_hours <= allowed_hours:
        time_saved = allowed_hours - acc_hours
        time_result = {"type": "DESPATCH", "hours": time_saved, "days": time_saved / 24}
        amount_value = time_saved * (despatch_rate / 24)
        amount = {"type": "DESPATCH", "value": round(amount_value, 2), "currency": "USD"}
    else:
        time_exceeded = acc_hours - allowed_hours
        time_result = {"type": "DEMURRAGE", "hours": time_exceeded, "days": time_exceeded / 24}
        amount_value = time_exceeded * (demurrage_rate / 24)
        amount = {"type": "DEMURRAGE", "value": round(amount_value, 2), "currency": "USD"}
    
    # 构建result
    result = {
        "case_id": judgments_data.get('case_id'),
        "vessel": judgments_data.get('vessel'),
        "port": judgments_data.get('port'),
        "cargo": judgments_data.get('cargo'),
        "discharge_rate": judgments_data.get('discharge_rate'),
        "allowed_laytime": {"hours": allowed_hours, "days": allowed_hours / 24},
        "time_used": {"hours": acc_hours, "days": acc_hours / 24},
        "time_result": time_result,
        "rates": {"demurrage_per_day": demurrage_rate, "despatch_per_day": despatch_rate},
        "amount": amount,
        "timeline": final_timeline,
        "key_dates": judgments_data.get('key_dates', {}),
        "calculated_at": datetime.now().isoformat()
    }
    
    if demurrage_info:
        result['demurrage_info'] = demurrage_info
    
    return result


def process_dual_port(judgments_data, contract_data=None):
    """处理双港案例"""
    ports = judgments_data.get('ports', {})
    charter_terms = judgments_data.get('charter_party_terms', {})
    
    # 计算每港的允许时间和使用时间
    port_results = []
    total_allowed = 0
    total_used = 0
    
    # ⚠️ 关键：双港累加需要延续
    global_acc_hours = 0
    
    for port_key in sorted(ports.keys()):
        port_data = ports[port_key]
        cargo_qty = port_data.get('cargo_quantity_mt', 0)
        rate = charter_terms.get('discharge_rate', {}).get('rate', 8000)
        
        # 单港允许时间
        port_allowed = (cargo_qty / rate) * 24 if rate > 0 else 0
        total_allowed += port_allowed
        
        # 累加时间（从上一个港口结束时的累计值继续）
        timeline = port_data.get('timeline', [])
        acc_hours = global_acc_hours  # ← 关键修改：延续上一港的累计值
        port_start_acc = acc_hours  # 记录本港开始时的累计值
        final_timeline = []
        
        for record in timeline:
            final_record = {
                "date": record.get('date'),
                "day": record.get('day'),
                "time_range": record.get('time_range'),
                "event": record.get('event'),
                "hours": record.get('hours'),
                "status": record.get('status'),
                "reason": record.get('reason'),
                "count_h": None,
                "cumulative": None
            }
            
            if record.get('status') == 'INCL':
                acc_hours += record.get('hours', 0)
                final_record['count_h'] = record.get('hours')
                final_record['cumulative'] = acc_hours
            else:
                final_record['cumulative'] = acc_hours
            
            final_timeline.append(final_record)
        
        # 更新全局累计值
        global_acc_hours = acc_hours
        
        # 本港使用时间 = 结束累计 - 开始累计
        port_used = acc_hours - port_start_acc
        total_used += port_used
        
        port_results.append({
            "name": port_data.get('name'),
            "cargo": {"type": judgments_data.get('notes', [''])[0] if judgments_data.get('notes') else 'UNKNOWN', "quantity_mt": cargo_qty},
            "discharge_rate": charter_terms.get('discharge_rate', {}),
            "allowed_laytime": {"hours": port_allowed, "days": port_allowed / 24},
            "time_used": {"hours": port_used, "days": port_used / 24},
            "key_dates": {
                "nor_tendered": port_data.get('nor_tendered'),
                "laytime_commenced": port_data.get('laytime_commenced'),
                "operation_completed": port_data.get('discharge_completed')
            },
            "timeline": final_timeline
        })
    
    # 费率
    demurrage_rate = charter_terms.get('demurrage_rate', 0)
    despatch_rate = charter_terms.get('despatch_rate', 0)
    
    # 计算结果
    if total_used <= total_allowed:
        time_saved = total_allowed - total_used
        time_result = {"type": "DESPATCH", "hours": time_saved, "days": time_saved / 24}
        amount_value = time_saved * (despatch_rate / 24)
        amount = {"type": "DESPATCH", "value": round(amount_value, 2), "currency": "USD"}
    else:
        time_exceeded = total_used - total_allowed
        time_result = {"type": "DEMURRAGE", "hours": time_exceeded, "days": time_exceeded / 24}
        amount_value = time_exceeded * (demurrage_rate / 24)
        amount = {"type": "DEMURRAGE", "value": round(amount_value, 2), "currency": "USD"}
    
    # 构建result
    result = {
        "case_id": judgments_data.get('case_id'),
        "vessel": judgments_data.get('vessel'),
        "calculation_type": "REVERSIBLE",
        "reversible_note": "两港允许时间可逆转合并计算",
        "cargo": {"type": "AUSTRALIAN BARLEY IN BULK", "quantity_mt": sum(p['cargo']['quantity_mt'] for p in port_results)},
        "allowed_laytime": {"hours": total_allowed, "days": total_allowed / 24},
        "time_used": {"hours": total_used, "days": total_used / 24},
        "time_result": time_result,
        "rates": {"demurrage_per_day": demurrage_rate, "despatch_per_day": despatch_rate},
        "amount": amount,
        "ports": port_results,
        "calculated_at": datetime.now().isoformat()
    }
    
    return result


def main(case_dir):
    """主函数"""
    case_path = Path(case_dir)
    
    # 查找输入文件
    judgments_final_path = case_path / "extracted" / "judgments_final.json"
    judgments2_path = case_path / "extracted" / "judgments2.json"
    contract_path = case_path / "extracted" / "contract.json"
    
    if judgments_final_path.exists():
        judgments_path = judgments_final_path
        print("📄 读取: judgments_final.json")
    elif judgments2_path.exists():
        judgments_path = judgments2_path
        print("📄 读取: judgments2.json")
    else:
        print(f"❌ 错误: 找不到判断文件")
        sys.exit(1)
    
    # 加载数据
    judgments_data = load_json(judgments_path)
    
    contract_data = None
    if contract_path.exists():
        contract_data = load_json(contract_path)
        print("📄 读取: contract.json")
    
    # 判断案例类型
    if 'ports' in judgments_data and isinstance(judgments_data['ports'], dict):
        print("🚢 双港案例计算")
        result = process_dual_port(judgments_data, contract_data)
        case_type = "dual"
    else:
        print("🚢 单港案例计算")
        result = process_single_port(judgments_data, contract_data)
        case_type = "single"
    
    # 保存
    output_dir = case_path / "calculation"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "result.json"
    save_json(result, output_path)
    
    # 输出摘要
    print(f"\n✅ 最终计算完成")
    print(f"   允许时间: {result['allowed_laytime']['hours']:.2f}h ({result['allowed_laytime']['days']:.2f}d)")
    print(f"   使用时间: {result['time_used']['hours']:.2f}h ({result['time_used']['days']:.2f}d)")
    
    if result['time_result']['type'] == 'DEMURRAGE':
        print(f"   ⚠️ 滞期: {result['time_result']['hours']:.2f}h ({result['time_result']['days']:.2f}d)")
        print(f"   滞期费: ${result['amount']['value']:,.2f} USD")
    else:
        print(f"   ✅ 速遣: {result['time_result']['hours']:.2f}h ({result['time_result']['days']:.2f}d)")
        print(f"   速遣费: ${result['amount']['value']:,.2f} USD")
    
    print(f"\n📄 输出: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python calculate_final.py <案例目录>")
        print("示例: python calculate_final.py 用户上传/BAKKEDAL_ZHANGZHOU_JIANGYIN_BARLEY")
        sys.exit(1)
    
    main(sys.argv[1])
