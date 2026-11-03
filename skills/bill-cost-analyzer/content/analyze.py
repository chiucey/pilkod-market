#!/usr/bin/env python3
"""
账单成本分析脚本
分析账单数据中各业务的成本分布
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


def analyze_bill_cost(csv_path: str) -> dict:
    """
    分析账单成本数据

    Args:
        csv_path: CSV文件路径

    Returns:
        包含成本分析结果的字典
    """

    # 业务关键词映射
    BUSINESS_KEYWORDS = {
        'union': 'union',
        'cpd': 'cpd',
        'feeds': 'feeds',
        'push': 'push',
        'brand': 'brand',
        'search': 'search/srh',
    }

    # 存储各业务的成本和实例数
    business_costs = defaultdict(lambda: {'cost': 0.0, 'count': 0, 'instances': set()})

    # 读取CSV文件
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                groupname = row.get('groupname', '').lower()
                cost_str = row.get('cost', '0')
                instance_id = row.get('id', '')

                try:
                    cost = float(cost_str) if cost_str else 0.0
                except ValueError:
                    cost = 0.0

                # 判断业务类型
                matched_business = None
                matched_keyword = None

                if 'union' in groupname:
                    matched_business = 'union'
                    matched_keyword = 'union'
                elif 'cpd' in groupname:
                    matched_business = 'cpd'
                    matched_keyword = 'cpd'
                elif 'feeds' in groupname:
                    matched_business = 'feeds'
                    matched_keyword = 'feeds'
                elif 'push' in groupname:
                    matched_business = 'push'
                    matched_keyword = 'push'
                elif 'brand' in groupname:
                    matched_business = 'brand'
                    matched_keyword = 'brand'
                elif 'search' in groupname or 'srh' in groupname:
                    matched_business = 'search(srh)'
                    matched_keyword = 'search/srh'
                else:
                    # 公共业务
                    matched_business = 'common'
                    matched_keyword = '公共业务'

                # 累加成本
                business_costs[matched_business]['cost'] += cost
                business_costs[matched_business]['count'] += 1
                business_costs[matched_business]['instances'].add(instance_id)

    except FileNotFoundError:
        print(f"错误: 文件不存在 - {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {str(e)}")
        sys.exit(1)

    # 计算总成本
    total_cost = sum(data['cost'] for data in business_costs.values())

    # 构建结果
    details = []
    for business in ['union', 'cpd', 'feeds', 'push', 'brand', 'search(srh)', 'common']:
        if business in business_costs:
            data = business_costs[business]
            percentage = (data['cost'] / total_cost * 100) if total_cost > 0 else 0

            keyword_map = {
                'union': 'union',
                'cpd': 'cpd',
                'feeds': 'feeds',
                'push': 'push',
                'brand': 'brand',
                'search(srh)': 'search/srh',
                'common': '公共业务'
            }

            details.append({
                'business': business,
                'keyword': keyword_map[business],
                'cost': round(data['cost'], 4),
                'percentage': round(percentage, 2),
                'instance_count': len(data['instances']),
                'record_count': data['count']
            })

    # 按成本降序排序
    details.sort(key=lambda x: x['cost'], reverse=True)

    result = {
        'summary': {
            'total_cost': round(total_cost, 4),
            'business_count': len([d for d in details if d['cost'] > 0])
        },
        'details': details
    }

    return result


def format_output(result: dict) -> str:
    """格式化输出结果"""

    lines = []
    lines.append("=" * 60)
    lines.append("账单成本分析报告")
    lines.append("=" * 60)
    lines.append("")

    # 总览
    summary = result['summary']
    lines.append(f"总成本: ¥{summary['total_cost']:,.4f}")
    lines.append(f"涉及业务数: {summary['business_count']}")
    lines.append("")

    # 详细数据
    lines.append("-" * 60)
    lines.append(f"{'业务':<15} {'关键词':<12} {'成本':>12} {'占比':>8} {'实例数':>8}")
    lines.append("-" * 60)

    for detail in result['details']:
        if detail['cost'] > 0:
            lines.append(
                f"{detail['business']:<15} {detail['keyword']:<12} "
                f"¥{detail['cost']:>10,.4f} {detail['percentage']:>6.2f}% "
                f"{detail['instance_count']:>8}"
            )

    lines.append("-" * 60)
    lines.append("")

    # 成本占比柱状图
    lines.append("成本占比分布:")
    lines.append("")
    for detail in result['details']:
        if detail['cost'] > 0:
            bar_length = int(detail['percentage'] / 2)  # 缩放显示
            bar = "█" * bar_length
            lines.append(f"  {detail['business']:<12} {bar} {detail['percentage']:.1f}%")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python analyze.py <csv_file_path>")
        sys.exit(1)

    csv_path = sys.argv[1]

    print(f"正在分析账单数据: {csv_path}")
    print()

    result = analyze_bill_cost(csv_path)
    output = format_output(result)
    print(output)

    # 如果需要JSON输出
    if '--json' in sys.argv:
        print()
        print("JSON输出:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
