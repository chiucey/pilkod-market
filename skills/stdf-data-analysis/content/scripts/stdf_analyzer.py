#!/usr/bin/env python3
"""
STDF 数据分析器
计算 CPK、异常点、分布特征，生成风险评估报告
"""
import sys
import math
from collections import defaultdict


def calculate_statistics(values):
    """计算统计数据"""
    if not values or len(values) < 2:
        return None

    values_sorted = sorted(values)
    n = len(values_sorted)
    mean = sum(values) / n

    # 标准差 (样本标准差，除以 n-1)
    variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0
    std = variance ** 0.5

    # 中位数
    if n % 2 == 0:
        median = (values_sorted[n // 2 - 1] + values_sorted[n // 2]) / 2
    else:
        median = values_sorted[n // 2]

    return {
        'count': n,
        'mean': mean,
        'median': median,
        'std': std,
        'min': min(values),
        'max': max(values)
    }


def calculate_cpk(lower_limit, upper_limit, mean, std):
    """计算 CPK (过程能力指数)"""
    if std == 0:
        return None

    cpu = (upper_limit - mean) / (3 * std)  # 上限能力指数
    cpl = (mean - lower_limit) / (3 * std)  # 下限能力指数

    return min(cpu, cpl)


def detect_distribution_pattern(values, mean, std):
    """检测分布模式"""
    if not values or std == 0:
        return "unknown"

    n = len(values)

    # 检测双峰
    hist = defaultdict(int)
    bucket_size = std / 4 if std > 0 else 0.1
    for v in values:
        bucket = int((v - min(values)) / bucket_size) if bucket_size > 0 else 0
        hist[bucket] += 1

    peaks = sum(1 for count in hist.values() if count > n * 0.1 and count == max(hist.values()))

    if peaks >= 2:
        return "bimodal"

    # 检测偏态
    skewness = sum((x - mean) ** 3 for x in values) / (n * std ** 3) if std > 0 else 0

    if skewness > 0.5:
        return "right_skewed"
    elif skewness < -0.5:
        return "left_skewed"

    return "normal"


def analyze_test_data(test_data, lower_limit=None, upper_limit=None):
    """分析单个测试项数据"""
    stats = calculate_statistics(test_data)
    if not stats:
        return None

    # 计算 CPK
    cpk = None
    if lower_limit is not None and upper_limit is not None:
        cpk = calculate_cpk(lower_limit, upper_limit, stats['mean'], stats['std'])

    # 检测异常点 (超过 3σ)
    outliers = []
    for v in test_data:
        if abs(v - stats['mean']) > 3 * stats['std']:
            outliers.append(v)

    # 分布模式
    pattern = detect_distribution_pattern(test_data, stats['mean'], stats['std'])

    return {
        'stats': stats,
        'cpk': cpk,
        'lower_limit': lower_limit,
        'upper_limit': upper_limit,
        'outliers_3sigma': len(outliers),
        'distribution': pattern,
        'outlier_values': outliers[:5]  # 最多5个异常点样本
    }


def generate_risk_report(statistics, cpk_threshold=1.33, outlier_threshold=3):
    """生成风险评估报告"""
    report = {
        'critical_risks': [],
        'warnings': [],
        'stable_items': []
    }

    for name, data in statistics.items():
        if not data:
            continue

        issues = []

        # 检查 CPK (如果存在)
        cpk_val = data.get('cpk')
        if cpk_val is not None:
            if cpk_val < 1.0:
                issues.append(f"CPK严重不足 ({cpk_val:.2f} < 1.0)")
            elif cpk_val < cpk_threshold:
                issues.append(f"CPK偏低 ({cpk_val:.2f} < {cpk_threshold})")

        # 检查异常点
        outliers_val = data.get('outliers_3sigma', 0)
        if outliers_val >= outlier_threshold:
            issues.append(f"异常点过多 ({outliers_val}个)")

        # 检查分布 (如果存在)
        distribution_val = data.get('distribution')
        if distribution_val:
            if distribution_val == 'bimodal':
                issues.append("分布呈双峰特征")
            elif distribution_val in ['right_skewed', 'left_skewed']:
                issues.append(f"分布偏态 ({distribution_val})")

        # 分类
        if issues:
            if cpk_val is not None and cpk_val < 1.0:
                report['critical_risks'].append({
                    'test_name': name,
                    'issues': issues,
                    'cpk': cpk_val,
                    'outliers': outliers_val,
                    'mean': data.get('stats', {}).get('mean'),
                    'std': data.get('stats', {}).get('std')
                })
            else:
                report['warnings'].append({
                    'test_name': name,
                    'issues': issues,
                    'cpk': cpk_val,
                    'outliers': outliers_val
                })
        else:
            if cpk_val is not None and cpk_val >= cpk_threshold:
                report['stable_items'].append({
                    'test_name': name,
                    'cpk': cpk_val
                })

    # 按 CPK 排序
    report['critical_risks'].sort(key=lambda x: x.get('cpk', 999) or 999)
    report['warnings'].sort(key=lambda x: x.get('cpk', 999) or 999)

    return report


def format_report(statistics, risk_report, total_duts, passed, failed):
    """格式化输出报告"""
    yield_rate = (passed / total_duts * 100) if total_duts > 0 else 0

    output = []
    output.append("=" * 70)
    output.append("STDF 数据分析报告")
    output.append("=" * 70)
    output.append("")
    output.append("【批次概况】")
    output.append(f"  测试数量: {total_duts} DUTs")
    output.append(f"  通过数量: {passed} ({passed/total_duts*100:.1f}%)" if total_duts > 0 else "  通过数量: 0")
    output.append(f"  失败数量: {failed} ({failed/total_duts*100:.1f}%)" if total_duts > 0 else "  失败数量: 0")
    output.append(f"  良率: {yield_rate:.2f}%")
    output.append("")

    output.append("【整体生产状态评价】")
    if not risk_report['critical_risks'] and not risk_report['warnings']:
        output.append("  批次质量整体可控，所有测试项 CPK ≥ 1.33，分布正常。")
    else:
        if risk_report['critical_risks']:
            output.append(f"  警告: 发现 {len(risk_report['critical_risks'])} 个高风险测试项，CPK < 1.0")
        if risk_report['warnings']:
            output.append(f"  注意: 发现 {len(risk_report['warnings'])} 个需关注项")
    output.append("")

    if risk_report['critical_risks']:
        output.append("【关键风险项 - CPK < 1.0】")
        for item in risk_report['critical_risks'][:10]:
            output.append(f"  - {item['test_name']}")
            output.append(f"    CPK={item.get('cpk', 'N/A'):.2f if item.get('cpk') else 'N/A'}, "
                         f"异常点={item['outliers']}个, 均值={item['mean']:.4f}")
            for issue in item['issues']:
                output.append(f"    问题: {issue}")
        output.append("")

    if risk_report['warnings']:
        output.append("【需关注项 - CPK < 1.33】")
        for item in risk_report['warnings'][:10]:
            output.append(f"  - {item['test_name']}")
            output.append(f"    CPK={item.get('cpk', 'N/A'):.2f if item.get('cpk') else 'N/A'}, "
                         f"异常点={item['outliers']}个")
        output.append("")

    output.append("【可能原因分析】")
    if risk_report['critical_risks'] or risk_report['warnings']:
        output.append("  - 测试设备通道稳定性可能存在问题")
        output.append("  - 工艺波动可能导致参数分布展宽")
        output.append("  - 批次混料或不同供应商晶圆可能导致双峰分布")
        output.append("  - 材料批次差异需要进一步排查")
    else:
        output.append("  - 所有测试项表现正常，未发现明显异常模式")
    output.append("")

    output.append("【改进建议】")
    if risk_report['critical_risks']:
        output.append("  1. 立即复查高风险测试项对应的测试机台校准记录")
        output.append("  2. 对异常点 DUT 进行物理失效分析 (PFA)")
        output.append("  3. 建议增加 WAT 与 FT 数据的关联分析")
        output.append("  4. 检查测试程序 Limits 设置是否合理")
    elif risk_report['warnings']:
        output.append("  1. 持续监控 CPK 偏低测试项的趋势变化")
        output.append("  2. 建议增加抽检比例验证稳定性")
    else:
        output.append("  1. 继续保持当前生产状态")
        output.append("  2. 定期进行 CPK 趋势监控")
    output.append("")
    output.append("=" * 70)

    return "\n".join(output)


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: stdf_analyzer.py <statistics.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        data = json.load(f)

    risk_report = generate_risk_report(data['statistics'])
    report = format_report(
        data['statistics'],
        risk_report,
        data['total_duts'],
        data['passed'],
        data['failed']
    )

    print(report)
