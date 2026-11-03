#!/usr/bin/env python3
"""
债务还款分析技能 - 快速验证脚本
"""

import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from debt_calculator import (
    parse_debt_input,
    calculate_debt_progress,
    calculate_total_summary,
    analyze_and_report,
    Debt
)


def test_basic_calculation():
    """测试基本计算功能"""
    print("=" * 60)
    print("测试 1: 基本计算功能")
    print("=" * 60)

    debt = Debt(
        name="测试信用卡",
        debt_type="信用卡",
        principal=50000,
        annual_rate=18,
        term_months=12,
        paid_months=3,
        monthly_payment=4500
    )

    result = calculate_debt_progress(debt)

    print(f"  债务名称: {debt.name}")
    print(f"  本金: ¥{debt.principal:,.0f}")
    print(f"  年利率: {debt.annual_rate}%")
    print(f"  进度: {result['progress_pct']:.1f}%")
    print(f"  剩余本金: ¥{result['remaining_principal']:,.0f}")

    assert result['progress_pct'] == 25.0, "进度计算错误"
    print("  ✓ 基本计算测试通过\n")


def test_parse_input():
    """测试输入解析"""
    print("=" * 60)
    print("测试 2: 输入解析功能")
    print("=" * 60)

    test_input = """信用卡1  信用卡  50000  18  12  3  4500
信用贷1  信用贷  100000  12  24  6  5000"""

    debts = parse_debt_input(test_input)

    print(f"  解析到 {len(debts)} 笔债务:")
    for d in debts:
        print(f"    - {d.name}: ¥{d.principal:,.0f} @ {d.annual_rate}%")

    assert len(debts) == 2, "解析笔数错误"
    print("  ✓ 输入解析测试通过\n")


def test_summary_calculation():
    """测试汇总计算"""
    print("=" * 60)
    print("测试 3: 汇总计算功能")
    print("=" * 60)

    debts = [
        Debt("卡1", "信用卡", 50000, 18, 12, 3, 4500),
        Debt("贷1", "信用贷", 100000, 12, 24, 6, 5000)
    ]

    progress = [calculate_debt_progress(d) for d in debts]
    summary = calculate_total_summary(debts, progress)

    print(f"  总债务笔数: {summary['total_debt_count']}")
    print(f"  总本金: ¥{summary['total_principal']:,.0f}")
    print(f"  月还款总额: ¥{summary['total_monthly_payment']:,.0f}")
    print(f"  平均利率: {summary['avg_annual_rate']:.2f}%")

    assert summary['total_principal'] == 150000, "总本金计算错误"
    print("  ✓ 汇总计算测试通过\n")


def test_full_report():
    """测试完整报表生成"""
    print("=" * 60)
    print("测试 4: 完整报表生成")
    print("=" * 60)

    test_input = """信用卡1  信用卡  50000  18  12  3  4500
信用贷1  信用贷  100000  12  24  6  5000"""

    report = analyze_and_report(test_input, extra_payment=1000)

    # 检查报表关键内容
    checks = [
        ("总债务笔数：2 笔" in report, "债务笔数"),
        ("总负债本金" in report, "总本金"),
        ("月还款总额" in report, "月还款"),
        ("雪球法" in report, "雪球法"),
        ("雪崩法" in report, "雪崩法"),
        ("优化建议" in report, "优化建议"),
    ]

    all_passed = True
    for check, name in checks:
        status = "✓" if check else "✗"
        print(f"  {status} {name}检查")
        if not check:
            all_passed = False

    print()
    if all_passed:
        print("  ✓ 完整报表测试通过\n")
    else:
        print("  ✗ 完整报表测试失败\n")
        return False

    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("债务还款分析技能 - 测试套件")
    print("=" * 60 + "\n")

    try:
        test_basic_calculation()
        test_parse_input()
        test_summary_calculation()
        success = test_full_report()

        if success:
            print("=" * 60)
            print("所有测试通过！✓")
            print("=" * 60)
            return True
        else:
            print("=" * 60)
            print("部分测试失败，请检查。")
            print("=" * 60)
            return False

    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
