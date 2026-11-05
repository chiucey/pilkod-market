"""
连锁茶饮企业多部门协作Agent系统 - 使用示例
Tea Enterprise Multi-Agent Collaboration System - Usage Examples

本文件提供各种协作场景的使用示例，帮助用户快速上手系统。

Author: MiniMax Agent
Version: 1.0.0
"""

from agent_system import (
    TeaEnterpriseCollaborationSystem,
    TaskType,
    Department
)


def example_1_new_product_launch():
    """
    示例1: 新品上市全部门联动
    场景：春季新品上市，需要研发、供应链、运营、市场、财务协同
    """
    print("\n" + "=" * 70)
    print("【示例1】新品上市 - 多部门联动协作")
    print("=" * 70)

    system = TeaEnterpriseCollaborationSystem()

    user_request = """
    公司计划在4月推出三款春季新品：
    - 茉莉花茶鲜奶茶
    - 樱花乌龙茶
    - 青梅绿茶

    需要协调研发部确认配方，供应链部准备原料，
    运营部进行门店准备，市场部制定推广策略，
    财务部审批预算。
    """

    print(f"\n📝 用户请求：\n{user_request}\n")

    result = system.process_user_request(user_request)

    print("\n📊 任务分析结果：")
    print(f"   • 推断类型: {result['task_overview']['inferred_type']}")
    print(f"   • 主导部门: {result['ceo_analysis']['lead_department']}")
    print(f"   • 协作部门: {', '.join(result['ceo_analysis']['collaborating_departments'])}")

    print("\n🏢 各部门响应摘要：")

    for dept, content in result['department_contributions'].items():
        print(f"\n   【{dept}】")
        if isinstance(content, dict):
            # 显示关键信息
            for key in list(content.keys())[:3]:
                if isinstance(content[key], dict):
                    print(f"      • {key}: {list(content[key].keys())[:3]}...")
                elif isinstance(content[key], list):
                    print(f"      • {key}: {len(content[key])}项")
                else:
                    print(f"      • {key}: {content[key]}")

    return result


def example_2_marketing_campaign():
    """
    示例2: 营销活动跨部门协作
    场景：五一假期促销，需要市场、运营、客服、数据分析协同
    """
    print("\n" + "=" * 70)
    print("【示例2】营销活动 - 跨部门协作")
    print("=" * 70)

    system = TeaEnterpriseCollaborationSystem()

    user_request = """
    五一假期（5月1日-5月5日）计划推出会员专享促销活动：
    - 全场饮品第二杯半价
    - 会员积分翻倍
    - 邀请好友得优惠券

    需要市场部策划活动细则，运营部执行门店推广，
    客服部准备FAQ，数据分析部监控活动效果。
    """

    print(f"\n📝 用户请求：\n{user_request}\n")

    result = system.process_user_request(user_request)

    print("\n📊 任务分析结果：")
    print(f"   • 推断类型: {result['task_overview']['inferred_type']}")
    print(f"   • 主导部门: {result['ceo_analysis']['lead_department']}")

    # 展示市场部响应
    if '市场营销部' in result['department_contributions']:
        marketing = result['department_contributions']['市场营销部']
        print("\n📣 市场部活动方案：")
        if 'campaign_plan' in marketing:
            for key, value in marketing['campaign_plan'].items():
                print(f"   • {key}: {value}")

    return result


def example_3_cost_optimization():
    """
    示例3: 成本优化专项协作
    场景：季度成本优化，需要供应链、财务、运营、数据分析协同
    """
    print("\n" + "=" * 70)
    print("【示例3】成本优化 - 专项协作")
    print("=" * 70)

    system = TeaEnterpriseCollaborationSystem()

    user_request = """
    公司本季度要求降低运营成本15%，重点优化：
    - 原材料采购成本
    - 物流配送效率
    - 门店人力成本

    供应链部负责采购议价，财务部分析成本结构，
    运营部优化排班，数据分析部提供决策支持。
    """

    print(f"\n📝 用户请求：\n{user_request}\n")

    result = system.process_user_request(user_request)

    print("\n📊 任务分析结果：")
    print(f"   • 推断类型: {result['task_overview']['inferred_type']}")
    print(f"   • 主导部门: {result['ceo_analysis']['lead_department']}")

    # 展示供应链部响应
    if '供应链部' in result['department_contributions']:
        supply = result['department_contributions']['供应链部']
        print("\n🚚 供应链部优化建议：")
        if 'optimization_opportunities' in supply:
            for i, item in enumerate(supply['optimization_opportunities'], 1):
                print(f"   {i}. {item}")
        if 'potential_savings' in supply:
            print(f"\n   💰 预计节省：")
            for k, v in supply['potential_savings'].items():
                print(f"      • {k}: {v}")

    # 展示财务部响应
    if '财务部' in result['department_contributions']:
        finance = result['department_contributions']['财务部']
        print("\n💼 财务部成本分析：")
        if 'current_financial_status' in finance:
            print(f"   • 成本结构: {finance['current_financial_status']}")

    return result


def example_4_staffing_expansion():
    """
    示例4: 人员扩张专项协作
    场景：新店扩张人员招聘，需要HR、运营、财务协同
    """
    print("\n" + "=" * 70)
    print("【示例4】人员扩张 - 招聘协作")
    print("=" * 70)

    system = TeaEnterpriseCollaborationSystem()

    user_request = """
    公司计划下半年新开50家门店，需要：
    - 新增员工500人（调茶师、店长等）
    - 招聘周期2个月
    - 培训周期1个月

    人力资源部负责招聘和培训，运营部提供人员需求明细，
    财务部审批招聘预算。
    """

    print(f"\n📝 用户请求：\n{user_request}\n")

    result = system.process_user_request(user_request)

    print("\n📊 任务分析结果：")
    print(f"   • 推断类型: {result['task_overview']['inferred_type']}")
    print(f"   • 主导部门: {result['ceo_analysis']['lead_department']}")

    # 展示HR响应
    if '人力资源部' in result['department_contributions']:
        hr = result['department_contributions']['人力资源部']
        print("\n👥 人力资源部招聘方案：")
        if 'recruitment_plan' in hr:
            for key, value in hr['recruitment_plan'].items():
                print(f"   • {key}: {value}")

    return result


def example_5_crisis_management():
    """
    示例5: 危机处理全部门联动
    场景：食品安全事件，需要CEO协调全部门响应
    """
    print("\n" + "=" * 70)
    print("【示例5】危机处理 - 全部门联动")
    print("=" * 70)

    system = TeaEnterpriseCollaborationSystem()

    user_request = """
    【紧急】某门店发生食品安全投诉事件，
    顾客在社交媒体发布负面信息引发关注。

    需要CEO协调全部门联动处理：
    - 运营部现场调查
    - 客服部联系顾客
    - 市场部舆情应对
    - 财务部准备赔偿预算
    """

    print(f"\n📝 用户请求：\n{user_request}\n")

    result = system.process_user_request(user_request)

    print("\n📊 任务分析结果：")
    print(f"   • 推断类型: {result['task_overview']['inferred_type']}")
    print(f"   • 主导部门: {result['ceo_analysis']['lead_department']}")
    print(f"   • 协作部门: {', '.join(result['ceo_analysis']['collaborating_departments'])}")

    # 展示各部门应急响应
    print("\n🚨 各部门应急响应：")
    for dept in ['运营部', '客服部', '市场营销部']:
        if dept in result['department_contributions']:
            content = result['department_contributions'][dept]
            print(f"\n   【{dept}】")
            # 显示immediate_actions或类似的关键响应
            for key in ['immediate_actions', 'response_timeline', 'coordination_needed']:
                if key in content:
                    print(f"      • {key}: {content[key]}")

    return result


def example_6_query_capabilities():
    """
    示例6: 查询系统能力
    展示系统所有Agent的能力
    """
    print("\n" + "=" * 70)
    print("【示例6】系统能力查询")
    print("=" * 70)

    system = TeaEnterpriseCollaborationSystem()

    print("\n🏢 茶饮企业多部门Agent协作系统")
    print("=" * 50)

    capabilities = system.list_all_capabilities()

    for dept, caps in capabilities.items():
        print(f"\n📋 {dept}")
        print("-" * 40)
        for i, cap in enumerate(caps, 1):
            print(f"   {i}. {cap}")

    # 查询特定部门状态
    print("\n\n📊 部门状态查询示例：")
    ops_status = system.get_department_status(Department.OPERATIONS)
    print(f"\n运营部状态：")
    print(f"   • 部门: {ops_status['department']}")
    print(f"   • Agent ID: {ops_status['agent_id']}")
    print(f"   • 状态: {ops_status['status']}")


def example_7_guided_collaboration():
    """
    示例7: 引导式协作流程
    展示如何按步骤引导用户完成协作
    """
    print("\n" + "=" * 70)
    print("【示例7】引导式协作流程")
    print("=" * 70)

    system = TeaEnterpriseCollaborationSystem()

    # 步骤1: 接收需求
    user_input = "我想推出一个新品"

    print("\n📌 步骤1: 接收需求")
    print(f"   用户: {user_input}")

    # 步骤2: 识别任务类型
    result = system.process_user_request(user_input)
    task_type = result['task_overview']['inferred_type']

    print(f"\n📌 步骤2: 识别任务类型")
    print(f"   系统识别为: 【{task_type}】")

    # 步骤3: 显示协作方案
    print(f"\n📌 步骤3: 协作方案预览")
    print(f"   主导部门: {result['ceo_analysis']['lead_department']}")
    print(f"   协作部门: {', '.join(result['ceo_analysis']['collaborating_departments'])}")

    # 步骤4: 确认并执行
    print(f"\n📌 步骤4: 执行协作")
    print("   系统正在协调各部门...")

    for dept in result['department_contributions'].keys():
        print(f"   ✓ {dept} 已响应")

    print(f"\n📌 步骤5: 生成报告")
    print(f"   协作完成！各部门意见已整合。")


def example_8_specific_task_type():
    """
    示例8: 指定任务类型的协作
    直接指定TaskType进行精确协作
    """
    print("\n" + "=" * 70)
    print("【示例8】指定任务类型协作")
    print("=" * 70)

    system = TeaEnterpriseCollaborationSystem()

    user_request = "需要进行季度经营分析"

    print(f"\n📝 用户请求：{user_request}")
    print("🎯 指定任务类型：数据分析")

    # 指定任务类型
    result = system.process_user_request(
        user_request,
        task_type=TaskType.DATA_ANALYSIS
    )

    print("\n📊 任务分析结果：")
    print(f"   • 指定类型: {result['task_overview']['inferred_type']}")
    print(f"   • 主导部门: {result['ceo_analysis']['lead_department']}")

    # 展示数据分析部响应
    if '数据分析部' in result['department_contributions']:
        data = result['department_contributions']['数据分析部']
        print("\n📈 数据分析部支持：")
        if 'data_availability' in data:
            print("   可用数据：")
            for key, value in data['data_availability'].items():
                print(f"      • {key}: {'✓' if value else '✗'}")
        if 'analysis_capabilities' in data:
            print("   分析能力：")
            for cap in data['analysis_capabilities']:
                print(f"      • {cap}")


def run_all_examples():
    """运行所有示例"""
    print("\n" + "🌟" * 35)
    print("连锁茶饮企业多部门协作Agent系统 - 完整示例演示")
    print("🌟" * 35)

    try:
        example_1_new_product_launch()
        input("\n按Enter继续下一个示例...")

        example_2_marketing_campaign()
        input("\n按Enter继续下一个示例...")

        example_3_cost_optimization()
        input("\n按Enter继续下一个示例...")

        example_4_staffing_expansion()
        input("\n按Enter继续下一个示例...")

        example_5_crisis_management()
        input("\n按Enter继续下一个示例...")

        example_6_query_capabilities()
        input("\n按Enter继续下一个示例...")

        example_7_guided_collaboration()
        input("\n按Enter继续下一个示例...")

        example_8_specific_task_type()

        print("\n\n" + "=" * 70)
        print("✅ 所有示例演示完成！")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n演示已取消")


if __name__ == "__main__":
    # 运行单个示例测试
    print("请选择运行模式：")
    print("1. 运行所有示例")
    print("2. 运行特定示例")

    # 默认运行所有示例
    run_all_examples()
