#!/usr/bin/env python3
"""
自我迭代技能 - 性能分析器
分析执行历史，识别模式和改进机会
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

def load_execution_log(log_path: str) -> List[Dict]:
    """加载执行日志"""
    if not os.path.exists(log_path):
        return []
    with open(log_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_execution_log(log_path: str, logs: List[Dict]) -> None:
    """保存执行日志"""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def calculate_success_rate(logs: List[Dict]) -> float:
    """计算成功率"""
    if not logs:
        return 0.0
    successes = sum(1 for log in logs if log.get('result') == 'success')
    return successes / len(logs) * 100

def identify_task_patterns(logs: List[Dict]) -> Dict[str, int]:
    """识别任务类型模式"""
    patterns = defaultdict(int)
    for log in logs:
        task_type = log.get('task_type', 'unknown')
        patterns[task_type] += 1
    return dict(patterns)

def analyze_failure_reasons(logs: List[Dict]) -> Dict[str, List[str]]:
    """分析失败原因"""
    failures = defaultdict(list)
    for log in logs:
        if log.get('result') in ['failure', 'partial']:
            task_type = log.get('task_type', 'unknown')
            reason = log.get('failure_reason', 'unknown')
            if reason not in failures[task_type]:
                failures[task_type].append(reason)
    return dict(failures)

def calculate_average_duration(logs: List[Dict]) -> float:
    """计算平均执行时间"""
    durations = [log.get('duration_ms', 0) for log in logs if 'duration_ms' in log]
    return sum(durations) / len(durations) if durations else 0

def identify_improvement_areas(logs: List[Dict]) -> List[Dict[str, Any]]:
    """识别改进机会"""
    areas = []

    # 分析成功率低的领域
    task_results = defaultdict(lambda: {'success': 0, 'total': 0})
    for log in logs:
        task_type = log.get('task_type', 'unknown')
        task_results[task_type]['total'] += 1
        if log.get('result') == 'success':
            task_results[task_type]['success'] += 1

    for task_type, stats in task_results.items():
        if stats['total'] >= 3:  # 至少3次执行才有统计意义
            rate = stats['success'] / stats['total'] * 100
            if rate < 70:
                areas.append({
                    'type': 'accuracy',
                    'priority': 'high' if rate < 50 else 'medium',
                    'description': f'{task_type} 任务成功率仅 {rate:.1f}%',
                    'task_type': task_type,
                    'current_rate': rate
                })

    # 分析响应时间异常的领域
    task_durations = defaultdict(list)
    for log in logs:
        if 'duration_ms' in log:
            task_durations[log.get('task_type', 'unknown')].append(log['duration_ms'])

    for task_type, durations in task_durations.items():
        if len(durations) >= 3:
            avg = sum(durations) / len(durations)
            if avg > 5000:  # 超过5秒标记为慢
                areas.append({
                    'type': 'efficiency',
                    'priority': 'medium',
                    'description': f'{task_type} 平均响应时间 {avg:.0f}ms',
                    'task_type': task_type,
                    'avg_duration': avg
                })

    return areas

def identify_strength_patterns(logs: List[Dict]) -> List[Dict[str, Any]]:
    """识别优势模式"""
    strengths = []

    # 分析成功率高的领域
    task_results = defaultdict(lambda: {'success': 0, 'total': 0})
    for log in logs:
        task_type = log.get('task_type', 'unknown')
        task_results[task_type]['total'] += 1
        if log.get('result') == 'success':
            task_results[task_type]['success'] += 1

    for task_type, stats in task_results.items():
        if stats['total'] >= 2 and stats['success'] == stats['total']:
            strengths.append({
                'pattern': f'{task_type} 任务执行稳定',
                'task_type': task_type,
                'success_rate': 100.0
            })

    return strengths

def generate_analysis_report(log_path: str) -> Dict[str, Any]:
    """生成完整分析报告"""
    logs = load_execution_log(log_path)

    report = {
        'timestamp': datetime.now().isoformat(),
        'total_executions': len(logs),
        'success_rate': calculate_success_rate(logs),
        'average_duration_ms': calculate_average_duration(logs),
        'task_patterns': identify_task_patterns(logs),
        'failure_reasons': analyze_failure_reasons(logs),
        'improvement_areas': identify_improvement_areas(logs),
        'strength_patterns': identify_strength_patterns(logs)
    }

    return report

def print_report(report: Dict[str, Any]) -> None:
    """格式化打印报告"""
    print("\n" + "="*60)
    print("自我迭代分析报告")
    print("="*60)
    print(f"\n生成时间: {report['timestamp']}")
    print(f"\n【执行历史摘要】")
    print(f"  总执行次数: {report['total_executions']}")
    print(f"  成功率: {report['success_rate']:.1f}%")
    print(f"  平均响应时间: {report['average_duration_ms']:.0f}ms")

    print(f"\n【任务类型分布】")
    for task_type, count in report['task_patterns'].items():
        print(f"  - {task_type}: {count}次")

    if report['failure_reasons']:
        print(f"\n【失败原因分析】")
        for task_type, reasons in report['failure_reasons'].items():
            print(f"  {task_type}:")
            for reason in reasons:
                print(f"    - {reason}")

    if report['improvement_areas']:
        print(f"\n【改进机会（按优先级）】")
        for area in sorted(report['improvement_areas'],
                          key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 3)):
            priority_tag = {'high': '[高]', 'medium': '[中]', 'low': '[低]'}.get(area['priority'], '')
            print(f"  {priority_tag} {area['description']}")

    if report['strength_patterns']:
        print(f"\n【优势模式（保持）】")
        for strength in report['strength_patterns']:
            print(f"  - {strength['pattern']}")

    print("\n" + "="*60)

if __name__ == '__main__':
    log_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'execution_log.json')
    report = generate_analysis_report(log_path)
    print_report(report)
