#!/usr/bin/env python3
"""分析 example.std 输出数据，生成完整报告"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

def calculate_statistics(values):
    """计算统计数据"""
    if not values:
        return None

    values = [v for v in values if v is not None and not math.isnan(v)]
    if not values:
        return None

    values_sorted = sorted(values)
    n = len(values_sorted)
    mean = sum(values) / n

    variance = sum((x - mean) ** 2 for x in values) / n
    std = variance ** 0.5 if variance > 0 else 0

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

def calculate_cpk(lower, upper, mean, std):
    """计算 CPK"""
    if std == 0 or lower is None or upper is None:
        return None
    cpu = (upper - mean) / (3 * std)
    cpl = (mean - lower) / (3 * std)
    return min(cpu, cpl)

def detect_distribution(values, mean, std):
    """检测分布模式"""
    if not values or std == 0:
        return "unknown"
    n = len(values)
    hist = defaultdict(int)
    bucket_size = std / 4 if std > 0 else 0.1
    min_val = min(values)
    for v in values:
        bucket = int((v - min_val) / bucket_size) if bucket_size > 0 else 0
        hist[bucket] += 1
    peaks = sum(1 for c in hist.values() if c > n * 0.1 and c == max(hist.values()))
    if peaks >= 2:
        return "bimodal"
    skewness = sum((x - mean) ** 3 for x in values) / (n * std ** 3) if std > 0 else 0
    if skewness > 0.5:
        return "right_skewed"
    elif skewness < -0.5:
        return "left_skewed"
    return "normal"

# 读取 example.csv 获取 limits
limits = {}
with open('/workspace/user_input_files/example.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    rows = list(reader)
    test_names = rows[0][10:]  # 从第11列开始是测试名
    upper_limits = rows[2][10:]
    lower_limits = rows[3][10:]

    for i, name in enumerate(test_names):
        try:
            ul = float(upper_limits[i]) if upper_limits[i] not in ['N/A', ''] else None
            ll = float(lower_limits[i]) if lower_limits[i] not in ['N/A', ''] else None
            if name:
                limits[name] = {'upper': ul, 'lower': ll}
        except:
            pass

# 读取解析后的数据
dut_data = []
with open('/workspace/user_input_files/example_output.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        dut_data.append(row)

# 提取测试数据
test_columns = [col for col in dut_data[0].keys() if col not in ['Part ID', 'Head', 'Site', 'Hard Bin', 'Soft Bin', 'Pass']]

# 计算统计数据
statistics = {}
for test_name in test_columns:
    values = []
    for dut in dut_data:
        val_str = dut.get(test_name, '')
        if val_str and val_str.strip():
            try:
                values.append(float(val_str))
            except:
                pass

    if not values:
        continue

    stats = calculate_statistics(values)
    if not stats:
        continue

    limit_info = limits.get(test_name, {'upper': None, 'lower': None})
    cpk = calculate_cpk(limit_info['lower'], limit_info['upper'], stats['mean'], stats['std'])

    # 计算异常点
    outliers = sum(1 for v in values if abs(v - stats['mean']) > 3 * stats['std'])
    distribution = detect_distribution(values, stats['mean'], stats['std'])

    statistics[test_name] = {
        'count': stats['count'],
        'mean': stats['mean'],
        'median': stats['median'],
        'std': stats['std'],
        'min': stats['min'],
        'max': stats['max'],
        'cpk': cpk,
        'lower_limit': limit_info['lower'],
        'upper_limit': limit_info['upper'],
        'outliers_3sigma': outliers,
        'distribution': distribution,
        'pass_rate': sum(1 for v in values if
            (limit_info['lower'] is None or v >= limit_info['lower']) and
            (limit_info['upper'] is None or v <= limit_info['upper'])
        ) / len(values) * 100 if limit_info['lower'] is not None or limit_info['upper'] is not None else None
    }

# 生成风险报告
critical_risks = []
warnings = []
stable = []

for name, data in statistics.items():
    if data['cpk'] is not None:
        issues = []
        if data['cpk'] < 1.0:
            issues.append(f"CPK严重不足 ({data['cpk']:.2f})")
        elif data['cpk'] < 1.33:
            issues.append(f"CPK偏低 ({data['cpk']:.2f})")

        if data['outliers_3sigma'] >= 5:
            issues.append(f"异常点过多 ({data['outliers_3sigma']}个)")

        if data['distribution'] == 'bimodal':
            issues.append("分布呈双峰特征")
        elif data['distribution'] in ['right_skewed', 'left_skewed']:
            issues.append(f"分布偏态 ({data['distribution']})")

        if issues:
            if data['cpk'] < 1.0:
                critical_risks.append({'name': name, 'cpk': data['cpk'], 'issues': issues, 'data': data})
            else:
                warnings.append({'name': name, 'cpk': data['cpk'], 'issues': issues, 'data': data})
        elif data['cpk'] >= 1.33:
            stable.append({'name': name, 'cpk': data['cpk']})

critical_risks.sort(key=lambda x: x['cpk'] or 999)
warnings.sort(key=lambda x: x['cpk'] or 999)

# 计算良率
passed = sum(1 for d in dut_data if d['Pass'] == 'Pass')
failed = len(dut_data) - passed
yield_rate = passed / len(dut_data) * 100

# 输出报告
print("=" * 80)
print("STDF 数据分析报告 - example.std")
print("=" * 80)
print()
print("【批次概况】")
print(f"  测试数量: {len(dut_data)} DUTs")
print(f"  测试项数: {len(statistics)} 项")
print(f"  通过数量: {passed} ({passed/len(dut_data)*100:.1f}%)")
print(f"  失败数量: {failed} ({failed/len(dut_data)*100:.1f}%)")
print(f"  良率: {yield_rate:.2f}%")
print()

print("【整体生产状态评价】")
if not critical_risks and not warnings:
    print("  批次质量整体可控，所有测试项 CPK ≥ 1.33，分布正常。")
else:
    if critical_risks:
        print(f"  警告: 发现 {len(critical_risks)} 个高风险测试项 (CPK < 1.0)")
    if warnings:
        print(f"  注意: 发现 {len(warnings)} 个需关注项 (CPK < 1.33)")
print()

if critical_risks:
    print("【关键风险项 - CPK < 1.0】(按 CPK 从低到高排序)")
    for item in critical_risks[:15]:
        print(f"  {item['name']}")
        print(f"    CPK={item['cpk']:.2f}, 均值={item['data']['mean']:.4f}, 标准差={item['data']['std']:.4f}")
        print(f"    范围=[{item['data']['min']:.4f}, {item['data']['max']:.4f}]")
        if item['data']['lower_limit']:
            print(f"    规格限=[{item['data']['lower_limit']}, {item['data']['upper_limit']}]")
        print(f"    异常点={item['data']['outliers_3sigma']}个, 分布={item['data']['distribution']}")
    print()

if warnings:
    print("【需关注项 - CPK < 1.33】(前15项)")
    for item in warnings[:15]:
        print(f"  {item['name']}")
        print(f"    CPK={item['cpk']:.2f}, 异常点={item['data']['outliers_3sigma']}个")
    print()

print("【可能原因分析】")
if critical_risks or warnings:
    print("  - 测试设备通道稳定性可能存在问题")
    print("  - 工艺波动可能导致参数分布展宽")
    print("  - 批次混料或不同供应商晶圆可能导致双峰分布")
    print("  - 材料批次差异需要进一步排查")
else:
    print("  - 所有测试项表现正常，未发现明显异常模式")
print()

print("【改进建议】")
if critical_risks:
    print("  1. 立即复查高风险测试项对应的测试机台校准记录")
    print("  2. 对异常点 DUT 进行物理失效分析 (PFA)")
    print("  3. 建议增加 WAT 与 FT 数据的关联分析")
    print("  4. 检查测试程序 Limits 设置是否合理")
elif warnings:
    print("  1. 持续监控 CPK 偏低测试项的趋势变化")
    print("  2. 建议增加抽检比例验证稳定性")
else:
    print("  1. 继续保持当前生产状态")
    print("  2. 定期进行 CPK 趋势监控")
print()

# ChipID 统计
chipid_stats = defaultdict(int)
for dut in dut_data:
    key = tuple(dut.get(f'read_chipid_{i}', '?') for i in range(4))
    chipid_stats[key] += 1

print("【ChipID 分布统计】")
unique_chips = len(chipid_stats)
print(f"  唯一 ChipID 组合数: {unique_chips}")
print("  前10个最常见组合:")
sorted_chips = sorted(chipid_stats.items(), key=lambda x: -x[1])
for i, (chipid, count) in enumerate(sorted_chips[:10]):
    print(f"    {i+1}. ID=({chipid[0]},{chipid[1]},{chipid[2]},{chipid[3]}) - {count} DUTs")

print()
print("=" * 80)
print("报告生成完成")
print("=" * 80)
