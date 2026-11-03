#!/usr/bin/env python3
"""
digital-marx-expert - 劳动过程分析工具
分析劳动过程：分工、协作、劳动控制等
基于马克思《资本论》和布雷弗曼《劳动与垄断资本》

本文件不包含任何硬编码关键词判断，仅作为数据结构容器+方法论备忘录，
所有实质性判断由LLM基于劳动过程理论框架完成。
"""

from typing import Dict, List, Any
import json


# ---------------------------------------------------------------------------
# 劳动过程理论备忘录（给LLM的引导）
# ---------------------------------------------------------------------------
LABOR_PROCESS_THEORY_MEMO = """
=== 劳动过程理论备忘录：布雷弗曼《劳动与垄断资本》===

【布雷弗曼核心论点】
布雷弗曼在《劳动与垄断资本》（1974）中揭示了资本主义劳动过程的演变逻辑：
- 科学管理（泰勒制）：将知识与执行分离，工人成为"执行者"
- 工作细分：将复杂劳动分解为简单操作，消除技艺壁垒
- 劳动控制：从"外部控制"到"内心顺从"的转变

【分析维度框架】

1. 劳动分工（Division of Labor）
   - 考察：劳动是被细分为简单操作还是保持完整性？
   - 识别：是否存在专业化/部门化/流水线分工？
   - 理论问题：谁设计了分工方案？工人是否有重新整合劳动的机会？
   - 填入 type: "detailed"（细分型） / "moderate"（适度型） / "integrated"（整合型）

2. 协作模式（Cooperation）
   - 考察：劳动者之间是孤立的还是存在有机协作？
   - 识别：是否存在团队劳动/集体组织/社会化的生产联系？
   - 理论问题：协作是自发的还是被管理的？协作是否增强了工人的社会性？
   - 填入 type: "managerial"（管理驱动） / "organic"（有机自发） / "isolated"（孤立劳动）

3. 劳动控制（Labor Control）
   - 考察：资本家/管理层通过什么手段控制劳动过程？
   - 控制手段类型：
     * 直接监督：工头/监工在场
     * 机器控制：通过机器节奏/自动化约束
     * 规则制度：规程/考核/纪律
     * 内心顺从：将控制内化为自我管理
   - 理论问题：控制是可见的还是隐蔽的？工人是否参与控制规则的制定？
   - 填入 type: "direct"（直接监督） / "technical"（技术控制） / "bureaucratic"（制度管控） / "self"（自我管理）

4. 技术与自动化（Technology & Automation）
   - 考察：技术是被用来解放劳动者还是强化对劳动的控制？
   - 马克思视角：机器既是减轻劳动的手段，也可能成为支配劳动的力量
   - 布雷弗曼视角：自动化往往导致工作内容的贫乏化
   - 填入 type: "emancipatory"（解放型） / "dominating"（支配型） / "neutral"（中性型）

5. 劳动异化（Alienation）
   - 考察：劳动过程中劳动者的主观体验如何？
   - 识别：劳动者对劳动是认同还是疏离？劳动是否有意义感？
   - 马克思：异化劳动是外在的、强制的、无意义的
   - 填入 type: "alienated"（异化型） / "dehumanized"（非人化型） / "meaningful"（有意义型）

【劳动控制模式识别指南】

模式A — 泰勒制（高度控制-异化型）:
   - 特征：科学管理 + 直接监督 + 劳动细分 + 高度异化
   - 布雷弗曼所说的"技艺被剥夺"，知识与执行完全分离
   - 典型：流水线工厂、外卖骑手（算法驱动）

模式B — 新型劳动控制（表面自主实则控制）:
   - 特征：赋予劳动者表面自主权（如弹性工作），但通过 KPI/评分隐形控制
   - 劳动者承担风险（如平台经济中的"自雇"伪装）
   - 典型：互联网平台劳动、自由职业者

模式C — 制度化管控（规范型）:
   - 特征：通过规章制度、绩效考核进行中层控制
   - 劳动者有一定空间但受规则约束
   - 典型：官僚制企业

模式D — 自主性劳动（较少控制）:
   - 特征：劳动者对劳动过程有较大控制权
   - 技艺/知识型劳动，难以被完全分解
   - 典型：工匠、独立专业人士

【评估原则】
- LLM应基于上述五个维度和四种控制模式，结合文本进行整体判断
- 不依赖关键词频率，而依赖对劳动关系和控制机制的深度分析
- 判断结果填入返回结构中的 None 字段
"""


class LaborProcessAnalyzer:
    """劳动过程分析器（无硬编码关键词）"""

    def __init__(self):
        self.analysis_results = []

    def analyze_labor_process(self, data: Any, industry: str = None) -> Dict:
        """
        分析劳动过程

        参数:
            data: 分析数据（文本、字典或列表）
            industry: 行业类型

        返回:
            劳动过程分析结果（各维度 type=None，供LLM填充）
        """
        result = {
            "data_type": type(data).__name__,
            "industry": industry,
            "theory_memo": LABOR_PROCESS_THEORY_MEMO.strip(),
            "dimensions": {
                # 以下 type=None 表示需要LLM根据理论框架判断填充
                "division_of_labor": {
                    "type": None,  # "detailed"/"moderate"/"integrated"
                    "evidence": None,  # LLM提取的证据文本
                    "description": "劳动分工程度",
                },
                "cooperation": {
                    "type": None,  # "managerial"/"organic"/"isolated"
                    "evidence": None,
                    "description": "劳动协作程度与模式",
                },
                "labor_control": {
                    "type": None,  # "direct"/"technical"/"bureaucratic"/"self"
                    "evidence": None,
                    "description": "劳动控制程度与手段",
                },
                "technology": {
                    "type": None,  # "emancipatory"/"dominating"/"neutral"
                    "evidence": None,
                    "description": "技术条件与自动化程度",
                },
                "alienation": {
                    "type": None,  # "alienated"/"dehumanized"/"meaningful"
                    "evidence": None,
                    "description": "劳动过程中的异化程度",
                },
            },
            "overall_score": None,  # LLM综合评分: 0.0-1.0
            "control_mode": None,  # LLM判断: "泰勒制"/"新型控制"/"制度化管控"/"自主性劳动"
            "explanation": None,  # LLM基于布雷弗曼理论的解释
        }

        self.analysis_results.append(result)
        return result


def analyze_labor_process(data: Any, industry: str = None) -> Dict:
    """
    劳动过程分析入口函数

    参数:
        data: 分析数据
        industry: 行业类型

    返回:
        劳动过程分析结果（空结构 + 方法论备忘录）
    """
    analyzer = LaborProcessAnalyzer()
    return analyzer.analyze_labor_process(data, industry)


if __name__ == "__main__":
    # 测试
    test_data = """
    该工厂采用泰勒制的科学管理方法。劳动分工精细，
    每个工人只负责一个简单的操作动作。管理人员监督严格，
    工人必须按照规定的节奏工作。劳动单调重复，
    工人感到疏离和无意义。生产自动化程度不断提高。
    """

    result = analyze_labor_process(test_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
