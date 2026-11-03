"""
工期统计通报Skill - 测试脚本

使用方法：
1. 确保已安装依赖：pip install pandas openpyxl
2. 运行脚本：python test_skill.py
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from duration_calculator import (
    load_project_data,
    parse_date,
    add_days,
    add_months,
    calculate_construction_period_required,
    calculate_construction_phase_required,
    calculate_acceptance_control_required,
    determine_duration_status,
    is_provincial_project,
    check_pms_closed,
    determine_project_type,
    calculate_standard_duration,
    process_high_quality_duration_report,
    process_standard_duration_report,
    CONSTRUCTION_PERIOD_DAYS,
    CONSTRUCTION_PHASE_DAYS,
    ACCEPTANCE_CONTROL_DAYS,
    PROJECT_TYPE_STANDARDS
)


def test_date_functions():
    """测试日期处理函数"""
    print("\n" + "=" * 60)
    print("测试1：日期处理函数")
    print("=" * 60)

    # 测试日期解析
    test_date = "2025-01-15"
    parsed = parse_date(test_date)
    print(f"  解析日期 '{test_date}': {parsed}")

    # 测试加天数
    result = add_days(parsed, 274)
    print(f"  加{CONSTRUCTION_PERIOD_DAYS}天: {result.strftime('%Y-%m-%d')}")

    # 测试加月数
    result = add_months(parsed, 11)
    print(f"  加11月: {result.strftime('%Y-%m-%d')}")

    # 测试空值处理
    empty_result = parse_date(None)
    print(f"  解析None: {empty_result}")

    print("  ✓ 日期函数测试通过")


def test_duration_calculation():
    """测试工期计算"""
    print("\n" + "=" * 60)
    print("测试2：工期计算规则")
    print("=" * 60)

    approval_date = "2025-01-15"
    start_date = "2025-03-01"
    handover_date = "2025-08-15"

    # 计算要求时间
    construction_required = calculate_construction_period_required(approval_date)
    phase_required = calculate_construction_phase_required(start_date)
    acceptance_required = calculate_acceptance_control_required(handover_date)

    print(f"  立项批复时间: {approval_date}")
    print(f"  开工报告时间: {start_date}")
    print(f"  割接上线交维时间: {handover_date}")
    print()
    print(f"  优质工程建设期要求交维时间: {construction_required.strftime('%Y-%m-%d') if construction_required else 'N/A'}")
    print(f"  优质工程施工期要求交维时间: {phase_required.strftime('%Y-%m-%d') if phase_required else 'N/A'}")
    print(f"  优质工程验收控制要求竣工时间: {acceptance_required.strftime('%Y-%m-%d') if acceptance_required else 'N/A'}")

    print("  ✓ 工期计算测试通过")


def test_duration_status():
    """测试工期管控判定"""
    print("\n" + "=" * 60)
    print("测试3：工期管控状态判定")
    print("=" * 60)

    # 场景1：符合管控
    status1 = determine_duration_status(
        handover_date="2025-08-01",
        completion_date="2025-10-01",
        construction_required="2025-10-16",
        phase_required="2025-08-31",
        acceptance_required="2025-12-31"
    )
    print(f"  场景1（符合管控）: {status1} - {'✓' if status1 == 1 else '✗'}")

    # 场景2：超期
    status2 = determine_duration_status(
        handover_date="2025-11-01",
        completion_date="2025-12-01",
        construction_required="2025-10-16",
        phase_required="2025-08-31",
        acceptance_required="2025-12-31"
    )
    print(f"  场景2（工期超期）: {status2} - {'✓' if status2 == 3 else '✗'}")

    # 场景3：未到管控期（有空值）
    status3 = determine_duration_status(
        handover_date="2025-08-01",
        completion_date=None,
        construction_required="2025-10-16",
        phase_required="2025-08-31",
        acceptance_required="2025-12-31"
    )
    print(f"  场景3（未到管控期）: {status3} - {'✓' if status3 == 2 else '✗'}")


def test_provincial_project():
    """测试省管项目判断"""
    print("\n" + "=" * 60)
    print("测试4：省管项目判断")
    print("=" * 60)

    test_cases = [
        ("河源分公司", None, "仅河源分公司 → 非省管"),
        ("工程建设部,河源分公司", 1, "多单位 → 省管"),
        ("省公司,河源分公司,其他", 1, "多次出现 → 省管"),
        ("工程建设部", 1, "不含河源 → 省管")
    ]

    for unit, expected, description in test_cases:
        result = is_provincial_project(unit)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{unit}': {result} → {description}")


def test_pms_closed():
    """测试PMS关闭状态判断"""
    print("\n" + "=" * 60)
    print("测试5：PMS关闭状态判断")
    print("=" * 60)

    result1 = check_pms_closed("2025-06-15")
    result2 = check_pms_closed(None)
    print(f"  PMS关闭时间存在: {result1} - ✓")
    print(f"  PMS关闭时间为空: {result2} - ✓")


def test_project_type():
    """测试项目类型判定"""
    print("\n" + "=" * 60)
    print("测试6：项目类型判定")
    print("=" * 60)

    test_cases = [
        ("广东无线_主设备项目流程模板（两阶段设计模式）", None, "主设备模板"),
        ("传输系统-省内干线项目", "传输系统-省内干线", "传输系统"),
        ("软件开发项目流程", "纯软件-定制开发类", "软件开发"),
        ("", None, "无模板")
    ]

    for template, expected, description in test_cases:
        result = determine_project_type(template)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {description}: {result}")


def test_standard_duration():
    """测试标准工期计算"""
    print("\n" + "=" * 60)
    print("测试7：标准工期计算")
    print("=" * 60)

    result = calculate_standard_duration(
        approval_date="2025-01-01",
        start_date="2025-04-01",
        handover_date="2025-08-01",
        project_type="传输系统-省内干线"
    )

    for key, value in result.items():
        if value:
            print(f"  {key}: {value.strftime('%Y-%m-%d')}")
        else:
            print(f"  {key}: N/A")

    print("  ✓ 标准工期计算测试通过")


def test_load_data():
    """测试数据加载"""
    print("\n" + "=" * 60)
    print("测试8：数据加载")
    print("=" * 60)

    # 检查测试数据文件是否存在
    test_file = "/workspace/user_input_files/项目数据表.xlsx"
    if not os.path.exists(test_file):
        print(f"  ⚠ 测试数据文件不存在: {test_file}")
        print("  请提供实际的项目数据表进行完整测试")
        return False

    try:
        df = load_project_data(test_file)
        print(f"  ✓ 成功加载数据")
        print(f"    - 行数: {len(df)}")
        print(f"    - 列数: {len(df.columns)}")
        print(f"    - 工作表: 项目明细查询报表")
        print(f"    - 表头行: 第2行")

        # 显示关键列是否存在
        key_columns = [
            "项目编码", "项目名称", "建设单位",
            "第一次立项批复完成时间", "开工报告完成（填报）时间",
            "割接上线交维（填报）时间", "竣工验收完成时间",
            "PMS第一次项目关闭时间"
        ]

        print(f"\n  关键列检查:")
        for col in key_columns:
            exists = "✓" if col in df.columns else "✗"
            print(f"    {exists} {col}")

        return True
    except Exception as e:
        print(f"  ✗ 数据加载失败: {e}")
        return False


def test_process_reports():
    """测试报表处理"""
    print("\n" + "=" * 60)
    print("测试9：报表处理（完整流程）")
    print("=" * 60)

    test_file = "/workspace/user_input_files/项目数据表.xlsx"
    if not os.path.exists(test_file):
        print(f"  ⚠ 跳过：测试数据文件不存在")
        return

    try:
        # 加载数据
        df = load_project_data(test_file)
        print(f"  ✓ 数据加载成功")

        # 创建空辅助表（用于测试）
        aux_df = None

        # 处理优质工期统计表
        enhanced_df, stats_df = process_high_quality_duration_report(df, aux_df)
        print(f"  ✓ 优质工期统计表处理完成")
        print(f"    - 增补列后项目数: {len(enhanced_df)}")
        print(f"    - 统计表记录数: {len(stats_df)}")

        # 处理标准工期统计表
        standard_df = process_standard_duration_report(df)
        print(f"  ✓ 标准工期统计表处理完成")
        print(f"    - 统计表记录数: {len(standard_df)}")

        # 显示统计结果
        if "是否满足优质工程交维时间" in enhanced_df.columns:
            status_counts = enhanced_df["是否满足优质工程交维时间"].value_counts()
            print(f"\n  工期管控状态分布:")
            for status, count in status_counts.items():
                label = {1: "符合管控", 2: "未到管控期", 3: "工期超期"}.get(status, "未知")
                print(f"    {label}: {count}个")

        if "项目类别" in standard_df.columns:
            type_counts = standard_df["项目类别"].value_counts()
            print(f"\n  项目类型分布:")
            for proj_type, count in type_counts.items():
                if proj_type:
                    print(f"    {proj_type}: {count}个")

    except Exception as e:
        print(f"  ✗ 报表处理失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("工期统计通报Skill - 功能测试")
    print("=" * 60)

    # 基础功能测试
    test_date_functions()
    test_duration_calculation()
    test_duration_status()
    test_provincial_project()
    test_pms_closed()
    test_project_type()
    test_standard_duration()

    # 数据和流程测试
    test_load_data()
    test_process_reports()

    # 打印配置信息
    print("\n" + "=" * 60)
    print("配置信息")
    print("=" * 60)
    print(f"  优质工期统计标准:")
    print(f"    - 建设期要求: {CONSTRUCTION_PERIOD_DAYS}天")
    print(f"    - 施工期要求: {CONSTRUCTION_PHASE_DAYS}天")
    print(f"    - 验收控制要求: {ACCEPTANCE_CONTROL_DAYS}天")
    print(f"\n  项目类型数量: {len(PROJECT_TYPE_STANDARDS)}")
    for proj_type in PROJECT_TYPE_STANDARDS:
        print(f"    - {proj_type}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
