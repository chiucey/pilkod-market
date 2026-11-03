#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源预算监控使用示例

作者: MiniMax Agent
版本: 1.0.0
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resource_monitor import (
    BudgetMonitor,
    create_monitor,
    ThresholdConfig,
    AlertLevel
)


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("基础使用示例")
    print("=" * 60)

    # 创建监控器
    monitor = create_monitor(
        data_dir="data/budget_tracking"
    )

    # 开始监控会话
    session = monitor.start_session("example_session")

    # 模拟 API 调用记录
    print("\n1. 记录 API 调用...")
    session.record_api_call(
        operation_type="code_generation",
        token_input=1500,
        token_output=3000,
        execution_time_ms=2500
    )

    # 记录更多调用
    session.record_api_call(
        operation_type="analysis",
        token_input=2000,
        token_output=1500,
        execution_time_ms=1800
    )

    session.record_api_call(
        operation_type="research",
        token_input=3000,
        token_output=2000,
        execution_time_ms=2200
    )

    # 获取当前状态
    print("\n2. 获取监控状态...")
    status = session.get_status()
    print(f"   今日 Token 消耗: {status['daily_token_total']:,}")
    print(f"   API 调用次数: {status['daily_api_calls']}")
    print(f"   当前调用频率: {status['current_rpm']} 次/分钟")
    print(f"   总执行时间: {status['daily_execution_time_ms']:,} ms")

    # 获取趋势分析
    print("\n3. Token 消耗趋势...")
    trend = session.get_trend("token_total")
    print(f"   平均值: {trend['average']:,.0f}")
    print(f"   最大值: {trend['max']:,}")
    print(f"   最小值: {trend['min']:,}")

    # 检查限流状态
    print("\n4. 检查限流状态...")
    if session.should_rate_limit():
        wait_time = session.get_rate_limit_wait()
        print(f"   当前处于限流状态，需要等待 {wait_time} 秒")
    else:
        print("   未触发限流")

    # 结束会话
    print("\n5. 结束会话...")
    stats = session.end_session()
    print(f"   会话时长: {stats['duration_seconds']:.2f} 秒")
    print(f"   总 Token: {stats['total_token']:,}")
    print(f"   总 API 调用: {stats['total_api_calls']}")

    print("\n基础使用示例完成！")


def example_custom_thresholds():
    """自定义阈值示例"""
    print("\n" + "=" * 60)
    print("自定义阈值示例")
    print("=" * 60)

    # 创建自定义阈值配置
    thresholds = ThresholdConfig(
        token_daily_soft=20000,
        token_daily_hard=30000,
        token_per_call_warning=5000,
        token_per_call_critical=8000,
        api_rpm_soft=30,
        api_rpm_hard=40,
        execution_time_ms_soft=20000,
        execution_time_ms_hard=40000
    )

    # 使用自定义阈值创建监控器
    monitor = BudgetMonitor(
        data_dir="data/budget_custom",
        thresholds=thresholds
    )

    session = monitor.start_session("custom_thresholds")

    # 模拟高消耗调用
    session.record_api_call(
        operation_type="large_generation",
        token_input=6000,
        token_output=4000,
        execution_time_ms=30000
    )

    # 获取状态
    status = session.get_status()
    print(f"\n使用自定义阈值:")
    print(f"   Token 软限制: {thresholds.token_daily_soft:,}")
    print(f"   Token 硬限制: {thresholds.token_daily_hard:,}")
    print(f"   当前 Token: {status['daily_token_total']:,}")

    session.end_session()
    print("\n自定义阈值示例完成！")


def example_alert_handling():
    """告警处理示例"""
    print("\n" + "=" * 60)
    print("告警处理示例")
    print("=" * 60)

    # 创建监控器
    monitor = create_monitor(data_dir="data/budget_alerts")

    # 定义自定义告警处理器
    def custom_alert_handler(alert):
        level = alert["level"]
        message = alert["message"]
        details = alert["details"]

        print(f"\n[自定义告警处理器] {level.upper()}: {message}")
        if level == "critical":
            print(f"   详情: {details}")
            print(f"   建议操作: {details.get('action', 'N/A')}")

    # 注册自定义处理器
    monitor.alert_manager.add_listener(custom_alert_handler)

    session = monitor.start_session("alert_test")

    # 模拟触发警告
    print("\n模拟触发 Token 警告...")
    session.record_api_call(
        operation_type="high_consumption",
        token_input=9000,
        token_output=8000,  # 总计 17000，超过 warning 阈值 8000
        execution_time_ms=50000  # 超过执行时间阈值
    )

    # 获取告警历史
    print("\n告警历史:")
    alerts = monitor.alert_manager.get_recent_alerts()
    for alert in alerts:
        print(f"   - [{alert['level']}] {alert['message']}")

    session.end_session()
    print("\n告警处理示例完成！")


def example_report_generation():
    """报告生成示例"""
    print("\n" + "=" * 60)
    print("报告生成示例")
    print("=" * 60)

    # 创建监控器并模拟一些数据
    monitor = create_monitor(data_dir="data/budget_reports")
    session = monitor.start_session("report_generation")

    # 模拟多次调用
    for i in range(5):
        session.record_api_call(
            operation_type="sample_operation",
            token_input=1000 + i * 100,
            token_output=2000 + i * 200,
            execution_time_ms=1500 + i * 100
        )

    # 生成日报
    print("\n生成日报...")
    report = monitor.generate_report(period="daily", format="markdown")
    print(report)

    # 保存报告
    output_path = "reports/budget_daily_report.md"
    os.makedirs("reports", exist_ok=True)
    monitor.save_report(report, output_path)
    print(f"\n报告已保存到: {output_path}")

    # 生成 JSON 格式报告
    print("\n生成 JSON 格式报告...")
    json_report = monitor.generate_report(period="daily", format="json")
    print(json_report[:500] + "..." if len(json_report) > 500 else json_report)

    session.end_session()
    print("\n报告生成示例完成！")


def example_integration_with_self_improvement():
    """与自我成长技能集成示例"""
    print("\n" + "=" * 60)
    print("与自我成长技能集成示例")
    print("=" * 60)

    # 创建监控器
    monitor = create_monitor(data_dir="data/budget_self_improvement")

    # 模拟自我成长循环
    def self_improvement_loop(max_iterations=10):
        """模拟带资源监控的自我成长循环"""
        iteration = 0
        total_budget_used = 0

        while iteration < max_iterations:
            # 检查是否应该继续
            status = monitor.get_current_session().get_status()

            # 检查 Token 预算
            if status['daily_token_total'] >= 20000:
                print(f"\n⚠️ Token 预算接近上限 ({status['daily_token_total']:,}/20,000)")
                print("   暂停自我成长，等待预算恢复...")
                break

            # 检查是否限流
            if status['is_rate_limited']:
                wait_time = monitor.get_current_session().get_rate_limit_wait()
                print(f"\n⏳ 触发限流，等待 {wait_time} 秒...")
                import time
                time.sleep(min(wait_time, 5))
                continue

            # 执行一次成长迭代
            iteration += 1
            print(f"\n执行成长迭代 {iteration}/{max_iterations}...")

            session = monitor.get_current_session()
            session.record_api_call(
                operation_type="self_improvement",
                token_input=2000,
                token_output=1500,
                execution_time_ms=3000
            )

            current_status = session.get_status()
            total_budget_used = current_status['daily_token_total']
            print(f"   当前 Token 消耗: {total_budget_used:,}")

        return iteration, total_budget_used

    # 开始监控会话
    session = monitor.start_session("self_improvement_task")

    # 执行成长循环
    iterations, budget_used = self_improvement_loop(max_iterations=10)

    print("\n" + "-" * 40)
    print(f"自我成长循环完成")
    print(f"完成迭代次数: {iterations}")
    print(f"总 Token 消耗: {budget_used:,}")

    # 获取最终报告
    print("\n生成最终报告...")
    report = monitor.generate_report(period="daily", format="markdown")
    print(report)

    session.end_session()
    print("\n与自我成长技能集成示例完成！")


def main():
    """主函数"""
    print("\n资源预算监控技能使用示例")
    print("=" * 60)

    try:
        example_basic_usage()
        example_custom_thresholds()
        example_alert_handling()
        example_report_generation()
        example_integration_with_self_improvement()

        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
