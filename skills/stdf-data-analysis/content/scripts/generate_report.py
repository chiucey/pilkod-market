#!/usr/bin/env python3
"""生成完整的 STDF 数据分析报告"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from stdf_parser import STDFParser

def generate_full_report(std_file):
    """生成完整的分析报告"""
    # 解析文件
    parser = STDFParser(std_file)
    parser.parse()
    
    total = len(parser.dut_data)
    passed = sum(1 for d in parser.dut_data if d['pass'])
    failed = sum(1 for d in parser.dut_data if not d['pass'])
    bins = parser.get_bin_statistics()
    
    # 统计 PTR 测试项
    ptr_stats = {}
    for dut in parser.dut_data:
        for key, test in dut['tests'].items():
            if test.get('type') != 'PTR':
                continue
            name = test['test_name']
            if name not in ptr_stats:
                ptr_stats[name] = {'passed': 0, 'failed': 0, 'values': []}
            
            passed_test = test.get('passed', True)
            if passed_test:
                ptr_stats[name]['passed'] += 1
            else:
                ptr_stats[name]['failed'] += 1
            
            if test.get('result') is not None:
                ptr_stats[name]['values'].append(test['result'])
    
    # 统计 FTR
    ftr_passed = sum(1 for f in parser.ftr_records if f.get('passed', False))
    ftr_failed = len(parser.ftr_records) - ftr_passed
    
    # 输出报告
    print("=" * 70)
    print("STDF 数据分析报告")
    print("=" * 70)
    print()
    
    print("【批次概况】")
    print(f"  测试数量: {total} DUTs")
    print(f"  通过数量: {passed} ({passed/total*100:.1f}%)" if total > 0 else "  通过数量: 0")
    print(f"  失败数量: {failed} ({failed/total*100:.1f}%)" if total > 0 else "  失败数量: 0")
    print(f"  良率: {(passed/total*100):.2f}%" if total > 0 else "  良率: 0%")
    print()
    
    print("【Bin 分布分析】")
    print("  Hard Bin 分布:")
    for bin_num, count in sorted(bins['hard_bins'].items()):
        pct = count/total*100
        print(f"    Bin {bin_num}: {count} ({pct:.1f}%)")
    
    print("  Soft Bin 分布:")
    for bin_num, count in sorted(bins['soft_bins'].items()):
        pct = count/total*100
        print(f"    Bin {bin_num}: {count} ({pct:.1f}%)")
    print()
    
    print("【FTR 功能测试结果】")
    print(f"  FTR 总数: {len(parser.ftr_records)}")
    print(f"  FTR 通过: {ftr_passed} ({ftr_passed/len(parser.ftr_records)*100:.1f}%)")
    print(f"  FTR 失败: {ftr_failed} ({ftr_failed/len(parser.ftr_records)*100:.1f}%)")
    print()
    
    print("【PTR 测试项结果分布】")
    print(f"  共 {len(ptr_stats)} 个参数测试项")
    print()
    
    # 按失败数排序
    sorted_items = sorted(ptr_stats.items(), key=lambda x: x[1]['failed'], reverse=True)
    
    # 显示有失败的测试项
    failed_items = [(n, s) for n, s in sorted_items if s['failed'] > 0]
    if failed_items:
        print("  失败测试项 (前20):")
        for i, (name, stats) in enumerate(failed_items[:20]):
            total_test = stats['passed'] + stats['failed']
            fail_rate = stats['failed'] / total_test * 100
            print(f"    {i+1}. {name}")
            print(f"       通过: {stats['passed']}, 失败: {stats['failed']} ({fail_rate:.1f}%)")
            
            values = stats['values']
            if values:
                mean = sum(values) / len(values)
                print(f"       均值: {mean:.6f}, 范围: [{min(values):.6f}, {max(values):.6f}]")
            print()
    else:
        print("  所有测试项均通过 ✓")
        print()
    
    # 显示通过率最低的测试项
    print("  通过率最低的测试项 (前10):")
    low_pass_items = sorted(ptr_stats.items(), key=lambda x: x[1]['passed'] / (x[1]['passed'] + x[1]['failed']) if (x[1]['passed'] + x[1]['failed']) > 0 else 1)
    for i, (name, stats) in enumerate(low_pass_items[:10]):
        total_test = stats['passed'] + stats['failed']
        pass_rate = stats['passed'] / total_test * 100 if total_test > 0 else 0
        status = '⚠️' if stats['failed'] > 0 else '✓'
        print(f"    {i+1}. {name}: {pass_rate:.1f}% {status}")
    print()
    
    print("【失败 DUT 分析】")
    failed_duts = [d for d in parser.dut_data if not d['pass']]
    for dut in failed_duts:
        print(f"  DUT-{dut['part_idx']}: Hard Bin={dut['hard_bin']}, Soft Bin={dut['soft_bin']}")
    print()
    
    # 整体评价
    print("=" * 70)
    print("整体生产状态评价")
    print("=" * 70)
    if failed == 0:
        print("  批次质量良好，所有 DUT 均通过测试。")
    elif passed/total >= 0.9:
        print("  批次质量可控，良率 >= 90%。")
    elif passed/total >= 0.7:
        print(f"  批次良率为 {passed/total*100:.0f}%，存在一定失败率。")
    else:
        print("  批次良率偏低，建议分析失败原因。")
    print()
    
    print("【改进建议】")
    if failed > 0:
        print("  1. 复查失败 DUT 的详细测试数据")
        print("  2. 分析上述失败测试项的趋势变化")
        print("  3. 检查测试设备校准状态")
    else:
        print("  1. 继续保持当前生产状态")
        print("  2. 定期进行 CPK 趋势监控")
    print()
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <input.std>")
        sys.exit(1)
    
    generate_full_report(sys.argv[1])
