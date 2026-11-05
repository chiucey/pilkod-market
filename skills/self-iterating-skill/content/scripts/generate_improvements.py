#!/usr/bin/env python3
"""
自我迭代技能 - 改进建议生成器
基于分析报告生成具体的改进方案
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

def load_analysis_report(analysis_path: str) -> Dict[str, Any]:
    """加载分析报告"""
    if os.path.exists(analysis_path):
        with open(analysis_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def suggest_skill_md_improvements(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    """建议 SKILL.md 内容改进"""
    suggestions = []

    # 基于改进机会生成建议
    for area in analysis.get('improvement_areas', []):
        if area['type'] == 'accuracy':
            suggestions.append({
                'category': 'skill_content',
                'priority': area['priority'],
                'title': f"增强 {area['task_type']} 任务的处理逻辑",
                'description': f"在 SKILL.md 中添加针对 {area['task_type']} 的详细指导",
                'action': 'update_skill_md',
                'target': 'SKILL.md'
            })

        if area['type'] == 'efficiency':
            suggestions.append({
                'category': 'workflow',
                'priority': area['priority'],
                'title': f"优化 {area['task_type']} 执行流程",
                'description': f"减少 {area['task_type']} 的处理步骤或添加预处理",
                'action': 'optimize_workflow',
                'target': 'SKILL.md'
            })

    # 基于失败原因生成建议
    for task_type, reasons in analysis.get('failure_reasons', {}).items():
        for reason in reasons:
            if '边界' in reason or '异常' in reason:
                suggestions.append({
                    'category': 'robustness',
                    'priority': 'high',
                    'title': f"为 {task_type} 添加边界情况处理",
                    'description': f"在 references/ 中添加 {task_type} 的边界情况指南",
                    'action': 'add_reference',
                    'target': f'references/{task_type}_edge_cases.md'
                })

    return suggestions

def suggest_script_automations(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    """建议新增脚本自动化"""
    suggestions = []

    total = analysis.get('total_executions', 0)
    if total > 10:
        suggestions.append({
            'category': 'automation',
            'priority': 'medium',
            'title': '添加性能趋势分析脚本',
            'description': '基于历史数据生成可视化趋势报告',
            'action': 'new_script',
            'target': 'scripts/trend_analysis.py'
        })

    # 检查是否有重复模式
    task_patterns = analysis.get('task_patterns', {})
    for task_type, count in task_patterns.items():
        if count >= 5:
            suggestions.append({
                'category': 'optimization',
                'priority': 'medium',
                'title': f'为 {task_type} 添加专用优化脚本',
                'description': f'{task_type} 出现频率高，考虑添加专用处理脚本',
                'action': 'new_script',
                'target': f'scripts/optimize_{task_type}.py'
            })

    return suggestions

def suggest_reference_additions(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    """建议添加参考文档"""
    suggestions = []

    improvement_areas = analysis.get('improvement_areas', [])
    if improvement_areas:
        suggestions.append({
            'category': 'documentation',
            'priority': 'medium',
            'title': '添加自我分析框架文档',
            'description': '在 references/ 中添加详细的自我分析框架',
            'action': 'new_reference',
            'target': 'references/self_analysis_framework.md'
        })

    # 检查是否缺乏某些任务类型的模式文档
    task_patterns = analysis.get('task_patterns', {})
    for task_type in task_patterns.keys():
        ref_path = f'references/{task_type}_patterns.md'
        suggestions.append({
            'category': 'documentation',
            'priority': 'low',
            'title': f'添加 {task_type} 最佳实践文档',
            'description': f'记录 {task_type} 的成功模式和注意事项',
            'action': 'new_reference',
            'target': ref_path
        })

    return suggestions

def prioritize_suggestions(suggestions: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """对建议进行优先级排序"""
    priority_map = {'high': 0, 'medium': 1, 'low': 2}
    return sorted(suggestions, key=lambda x: priority_map.get(x['priority'], 3))

def generate_improvement_plan(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """生成完整的改进计划"""
    plan = {
        'timestamp': datetime.now().isoformat(),
        'based_on_analysis': analysis.get('timestamp', 'unknown'),
        'suggestions': {
            'skill_md': prioritize_suggestions(suggest_skill_md_improvements(analysis)),
            'scripts': prioritize_suggestions(suggest_script_automations(analysis)),
            'references': prioritize_suggestions(suggest_reference_additions(analysis))
        },
        'summary': {
            'total_suggestions': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0
        }
    }

    # 统计优先级
    all_suggestions = (
        plan['suggestions']['skill_md'] +
        plan['suggestions']['scripts'] +
        plan['suggestions']['references']
    )

    for s in all_suggestions:
        plan['summary']['total_suggestions'] += 1
        priority = s['priority']
        if priority == 'high':
            plan['summary']['high_priority'] += 1
        elif priority == 'medium':
            plan['summary']['medium_priority'] += 1
        else:
            plan['summary']['low_priority'] += 1

    return plan

def print_plan(plan: Dict[str, Any]) -> None:
    """格式化打印改进计划"""
    print("\n" + "="*60)
    print("自我迭代改进计划")
    print("="*60)
    print(f"\n生成时间: {plan['timestamp']}")
    print(f"基于分析: {plan['based_on_analysis']}")

    print(f"\n【计划摘要】")
    print(f"  总建议数: {plan['summary']['total_suggestions']}")
    print(f"  高优先级: {plan['summary']['high_priority']}")
    print(f"  中优先级: {plan['summary']['medium_priority']}")
    print(f"  低优先级: {plan['summary']['low_priority']}")

    categories = [
        ('skill_md', 'SKILL.md 改进'),
        ('scripts', '脚本自动化'),
        ('references', '参考文档')
    ]

    for key, title in categories:
        items = plan['suggestions'][key]
        if items:
            print(f"\n【{title}】")
            for item in items:
                priority_tag = {'high': '[高]', 'medium': '[中]', 'low': '[低]'}.get(item['priority'], '')
                print(f"  {priority_tag} {item['title']}")
                print(f"      {item['description']}")
                print(f"      操作: {item['action']} → {item['target']}")

    print("\n" + "="*60)

if __name__ == '__main__':
    # 尝试加载分析报告
    skill_dir = os.path.dirname(os.path.dirname(__file__))
    analysis_path = os.path.join(skill_dir, 'data', 'analysis_report.json')

    # 如果没有分析报告，使用模拟数据
    analysis = load_analysis_report(analysis_path)
    if not analysis:
        # 使用空分析的默认建议
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_executions': 0,
            'improvement_areas': [],
            'failure_reasons': {},
            'task_patterns': {}
        }

    plan = generate_improvement_plan(analysis)
    print_plan(plan)
