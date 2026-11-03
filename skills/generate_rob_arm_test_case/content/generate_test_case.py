#!/usr/bin/env python3
"""
机械臂调度系统测试用例生成器
generate_rob_arm_test_case

用法:
  python3 generate_test_case.py "<场景描述>" [机械臂数量] [测试类型]
"""

import sys
import json
import re

# 预置场景模板库（高质量规则模板，覆盖主流调度场景）
TEMPLATES = {
    "急停": {
        "title": "急停触发后机械臂安全暂停与断点恢复验证",
        "prerequisites": [
            "机械臂处于正常运行状态，完成原点复位",
            "调度系统启动，任务队列中存在待执行任务",
            "急停按钮可触发，安全回路正常",
            "示教器/控制面板可操作"
        ],
        "steps": [
            "启动机械臂，执行连续搬运或抓取任务",
            "在任务执行过程中触发急停按钮",
            "确认所有轴立即停止运动",
            "解除急停状态",
            '在控制面板点击"恢复"或"断点续传"',
            "观察机械臂动作与任务执行状态"
        ],
        "expected": [
            "急停触发后，所有轴立即停止运动，系统进入安全状态",
            "急停期间，机械臂保持当前位置，无异常偏移",
            "恢复后，任务从断点位置继续执行或提示人工确认",
            "整个过程无碰撞、无设备损伤"
        ],
        "priority": "P0",
        "coverage": "安全控制模块、状态机恢复逻辑、紧急停止回路"
    },
    "路径冲突": {
        "title": "多臂路径空间干涉时的避碰重规划验证",
        "prerequisites": [
            "两台及以上机械臂共用同一工作空间",
            "调度系统运行正常，路径规划模块已加载",
            "空间中存在可触发路径交叉的障碍物或目标点"
        ],
        "steps": [
            "向两台机械臂同时下发存在空间干涉的作业任务",
            "观察调度器对路径冲突的检测与处理",
            "记录路径重规划决策与机械臂实际运动轨迹"
        ],
        "expected": [
            "调度器成功检测到路径干涉",
            "通过等待、重规划或速度调节等机制避免碰撞",
            "两台机械臂按序完成作业，无接触、无死锁"
        ],
        "priority": "P0",
        "coverage": "碰撞检测模块、路径重规划算法、协同调度策略"
    },
    "多任务抢占": {
        "title": "高优先级任务抢占低优先级任务的调度验证",
        "prerequisites": [
            "调度系统运行正常，支持优先级队列",
            "队列中存在等待中的低优先级任务",
            "高优先级任务触发条件可配置"
        ],
        "steps": [
            "向调度系统提交若干低优先级任务（任务A、B）",
            "在任务A执行过程中，触发高优先级任务C",
            "观察调度器对任务C的响应及对任务A的处理"
        ],
        "expected": [
            "任务C立即获得调度资源",
            "任务A被正确挂起或降级处理",
            "任务C完成后，任务A按策略恢复执行（立即续跑或重新排队）",
            "调度日志正确记录抢占事件与时间戳"
        ],
        "priority": "P1",
        "coverage": "优先级队列管理、任务状态机、调度算法"
    },
    "双臂同时抓取同一工位": {
        "title": "双臂同时抓取同一工位时的互斥机制验证",
        "prerequisites": [
            "两台机械臂（臂A、臂B）均已完成标定，处于就绪状态",
            "工位台有且仅有一个待抓取目标物",
            "调度系统运行正常，通信链路畅通"
        ],
        "steps": [
            "同时向臂A和臂B下发抓取同一工位的任务指令",
            "观察调度器任务分配决策",
            "记录实际执行结果与机械臂运动轨迹"
        ],
        "expected": [
            "调度器根据优先级或轮询策略仅将任务分配给其中一台机械臂",
            "另一台机械臂保持待机或重新规划路径",
            "抓取动作成功完成，无碰撞、无任务丢失"
        ],
        "priority": "P0",
        "coverage": "资源互斥机制、任务分配策略、碰撞检测模块"
    },
    "任务中断后恢复": {
        "title": "任务被中断后断点续传的正确性验证",
        "prerequisites": [
            "机械臂正在执行多步骤连续任务（如抓取→搬运→放置）",
            "支持断点记录功能"
        ],
        "steps": [
            "启动多步骤任务",
            "在中间步骤人为制造中断（断电/急停/通信中断）",
            "恢复后触发断点续传",
            "验证任务完成度与执行正确性"
        ],
        "expected": [
            "系统正确保存断点状态信息",
            "续传后从中断步骤继续，不重复执行已完成步骤",
            "最终任务正确完成，结果符合预期"
        ],
        "priority": "P1",
        "coverage": "断点保存机制、状态恢复逻辑、任务连续性保障"
    },
    "通信超时": {
        "title": "控制器与机械臂通信超时故障处理验证",
        "prerequisites": [
            "调度系统与机械臂通信正常",
            "通信超时阈值可配置"
        ],
        "steps": [
            "机械臂执行任务中，人为制造网络中断",
            "观察系统在超时后的响应行为",
            "恢复通信后观察任务状态"
        ],
        "expected": [
            "超时后系统正确识别通信故障并报警",
            "机械臂进入安全停止状态",
            "恢复通信后可重新建立连接并继续任务"
        ],
        "priority": "P1",
        "coverage": "通信心跳机制、超时检测、故障恢复策略"
    },
    "负载均衡": {
        "title": "多任务场景下调度器负载均衡策略验证",
        "prerequisites": [
            "三台及以上机械臂接入调度系统",
            "存在多个并行任务待分配"
        ],
        "steps": [
            "向调度系统同时提交多个任务",
            "观察任务在多机械臂间的分配情况",
            "记录各机械臂负载状态与任务完成时间"
        ],
        "expected": [
            "任务按调度策略合理分配至各机械臂",
            "无单一机械臂过载导致任务堆积",
            "整体任务完成时间最优或符合预设策略"
        ],
        "priority": "P2",
        "coverage": "负载均衡算法、多臂协同调度策略"
    }
}


def detect_scenario(scenario: str) -> str:
    """根据关键词匹配最相似的预置场景"""
    scenario_lower = scenario.lower()
    for keyword, template in TEMPLATES.items():
        if keyword in scenario_lower:
            return keyword
    return "generic"


def generate_from_template(scenario: str, arm_count: int, test_type: str, keyword: str) -> str:
    """从预置模板生成测试用例"""
    t = TEMPLATES[keyword]

    # 动态替换机械臂数量
    arm_word = f"{arm_count}台机械臂" if arm_count > 1 else "单台机械臂"
    arms_desc = "、".join([f"臂{i+1}" for i in range(arm_count)])

    steps = "\n".join([f"{i+1}. {s}" for i, s in enumerate(t["steps"])])
    expected = "\n".join([f"{i+1}. {e}" for i, e in enumerate(t["expected"])])
    prereqs = "\n".join([f"{i+1}. {p}" for i, p in enumerate(t["prerequisites"])])

    return f"""【用例标题】{t["title"]}

【前置条件】
{prereqs}

【测试步骤】
{steps}

【预期结果】
{expected}

【优先级】{t["priority"]}

【覆盖需求】{t["coverage"]}"""


def generate_generic(scenario: str, arm_count: int, test_type: str) -> str:
    """无预置模板时，通过规则+大模型风格生成测试用例"""
    priority_map = {
        "异常测试": "P0",
        "安全测试": "P0",
        "性能测试": "P1",
        "功能测试": "P1",
        "回归测试": "P2"
    }
    priority = priority_map.get(test_type, "P1")

    return f"""【用例标题】{scenario} — {test_type}

【前置条件】
1. 调度系统运行正常，{arm_count}台机械臂在线并已完成标定
2. 通信链路畅通，各单元状态可实时监控
3. 测试环境已搭建完成，包括工位、工具及目标物

【测试步骤】
1. 配置测试场景：{scenario}
2. 向调度系统下发任务触发指令
3. 监控调度日志、机械臂运动轨迹及系统状态
4. 记录关键事件与时间戳

【预期结果】
1. 系统按预定调度策略正确处理该场景
2. 各机械臂运动安全协调，无碰撞、无死锁
3. 任务正确完成，调度日志完整准确

【优先级】{priority}

【覆盖需求】任务调度算法、冲突检测模块、安全互斥机制、通信协议"""


def format_output(result: str, scenario: str, arm_count: int, test_type: str) -> str:
    """统一格式化输出"""
    header = f"�机械臂调度测试用例生成结果\n{'='*40}\n"
    header += f"📋 场景：{scenario}\n"
    header += f"🦾 机械臂数量：{arm_count}\n"
    header += f"🧪 测试类型：{test_type}\n"
    header += f"{'='*40}\n\n"
    return header + result


def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_test_case.py <场景描述> [机械臂数量] [测试类型]")
        sys.exit(1)

    scenario = sys.argv[1]
    arm_count = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    test_type = sys.argv[3] if len(sys.argv) > 3 else "功能测试"

    arm_count = max(1, min(10, arm_count))

    keyword = detect_scenario(scenario)

    if keyword != "generic":
        result = generate_from_template(scenario, arm_count, test_type, keyword)
    else:
        result = generate_generic(scenario, arm_count, test_type)

    print(format_output(result, scenario, arm_count, test_type))


if __name__ == "__main__":
    main()
