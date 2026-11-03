#!/usr/bin/env python3
"""
bourdieu-field-analysis-expert - 习性检测工具
识别行动者的习性模式与场域对应关系
纯数据结构管理 + 方法论备忘录，引导LLM做定性判断
"""

from typing import Dict, List, Any
import json


# 惯习理论方法论备忘录（供LLM参考的判断原则，不含任何关键词）
HABITUS_THEORY_MEMO = [
    "惯习定义：惯习（habitus）是行动者在特定社会条件（尤其是不平等的社会结构，如阶级惯习）中被塑造的持久、可转换的性情系统。它是历史经验的结晶，表现为行动者的性情倾向、实践与品位。惯习不是习惯（habit），它是比习惯更深层的、往往无意识的社会结构内化。",
    "性情倾向判断：如何从文本中识别性情倾向？性情倾向是'结构化的结构'（来自阶级经验）同时也是'建构性的结构'（产生实践与表征）。判断要点：（1）反复出现的行为模式（非一次性事件）；（2）行动者的自我叙述（'我总是……'、'我倾向于……'）；（3）无意识的偏好与选择（不需要刻意追求，自然而然）；（4）区分不同场域的性情（如'学术性情'vs.'商业性情'）。",
    "实践判断：实践（practice）是惯习在特定场域中的具体展现。判断要点：（1）行动者的行为是否具有系统性（而非随机）；（2）行动者的策略是否'合乎情理'地符合其在场域中的位置；（3）实践是否体现了对场域规则的掌握（既有能力又有倾向）；（4）注意：同样的实践（如'阅读'）在不同阶级惯习中具有完全不同的意义。",
    "品位判断：品位（taste/titish）是惯习的表征维度，是行动者进行社会区分（distinction）的工具。判断要点：（1）行动者对特定文化对象的偏好（音乐、艺术、阅读）；（2）行动者对'品味'的自我评价（'我有品位'）；（3）品位作为区隔工具（'我喜欢X，因为它代表Y'，暗含排斥Z）；（4）注意：布迪厄的核心论点是品位不是'自然'的，而是阶级惯习的产物。",
    "惯习-场域对应分析：惯习与场域的关系是双向的：（1）惯习是场域的产物（阶级经验、场域位置塑造惯习）；（2）惯习是进入场域的条件（特定惯习才能感知并进入特定场域）；（3）惯习产生场域适合的实践（惯习与场域'合拍'时，行动者感到'如鱼得水'）；（4）惯习与场域错位时产生张力（行动者感到格格不入或需要刻意调适）。LLM需要分析具体文本中行动者的惯习与其在场域中的位置是否匹配。",
    "身体化指标：最深的惯习是身体化的（incorporated），表现为：（1）身体语言与姿态；（2）语言风格与用词；（3）时间感与空间感（如中产阶级对'准时'的强调）；（4）情绪反应模式（如面对权威时的反应）。这些往往在文本中通过第三方描述体现，而非行动者自我陈述。",
]


class HabitustDetector:
    """习性检测器（纯数据管理 + 方法论引导）"""

    def __init__(self):
        self.habitus_patterns: Dict[str, List[Any]] = {}
        self.actor_habitus: Dict[str, Dict[str, Any]] = {}
        self.habitus_field_correspondence: List[Dict[str, Any]] = []

    def detect_habitus(self, text: str, actors: List[str] = None) -> Dict:
        """
        检测习性模式

        参数:
            text: 分析文本
            actors: 行动者列表（可选）

        返回:
            习性检测结果（空结构，由LLM填充定性判断）
        """
        return {
            # LLM需要判断：文本中有哪些习性指标？分别对应哪种类型？
            "indicators": {},  # {indicator_type: count_or_evidence, ...} — LLM自行判断
            # LLM需要为每个行动者分析其惯习的各个维度
            "actor_habitus": {},  # {actor_name: {dispositions, practices, tastes, incorporated, habitus_type}, ...}
            # LLM需要分析惯习与场域的对应关系
            "field_correspondence": [],  # [{actor, fields, habitus_type, correspondence_strength, analysis}, ...]
            # LLM需要判断：文本中体现的惯习强度如何？
            "habitus_strength": None,  # "strong" / "moderate" / "weak" / None
            # 方法论备忘录，供LLM参考
            "methodology_memo": HABITUS_THEORY_MEMO,
        }

    def generate_habitus_report(self, analysis_result: Dict) -> str:
        """
        生成习性分析报告

        参数:
            analysis_result: detect_habitus() 的返回结果

        返回:
            格式化报告文本
        """
        lines = []
        lines.append("# 习性分析报告\n")
        lines.append("> 本报告由LLM基于布迪厄惯习理论生成，工具仅提供数据结构管理。\n")

        indicators = analysis_result.get("indicators", {})
        if indicators:
            lines.append("## 习性指标\n")
            for ind_type, ev in indicators.items():
                lines.append(f"- {ind_type}: {ev}")
            lines.append("")
        else:
            lines.append("## 习性指标\n")
            lines.append("- 未检测到明确的习性指标\n")
            lines.append("")

        strength = analysis_result.get("habitus_strength")
        lines.append("## 惯习强度评估\n")
        lines.append(f"强度等级: {strength if strength else '未评估'}")
        lines.append("")

        actor_habitus = analysis_result.get("actor_habitus", {})
        if actor_habitus:
            lines.append("## 行动者惯习分析\n")
            for actor, habitus in actor_habitus.items():
                hab_type = habitus.get("habitus_type", "未分类")
                lines.append(f"### {actor}\n")
                lines.append(f"- 惯习类型: {hab_type}")
                disp = habitus.get("dispositions", [])
                pract = habitus.get("practices", [])
                tast = habitus.get("tastes", [])
                incorp = habitus.get("incorporated", [])
                lines.append(f"- 性情倾向: {len(disp)}项 — {disp if disp else '无明确描述'}")
                lines.append(f"- 实践模式: {len(pract)}项 — {pract if pract else '无明确描述'}")
                lines.append(f"- 品位表征: {len(tast)}项 — {tast if tast else '无明确描述'}")
                lines.append(f"- 身体化指标: {len(incorp)}项 — {incorp if incorp else '无明确描述'}")
            lines.append("")

        corr = analysis_result.get("field_correspondence", [])
        if corr:
            lines.append("## 惯习-场域对应分析\n")
            for c in corr[:3]:
                actor = c.get("actor", "未知")
                fields = c.get("fields", [])
                hab_type = c.get("habitus_type", "未知")
                strength_corr = c.get("correspondence_strength", "N/A")
                analysis = c.get("analysis", "")
                lines.append(f"### {actor}\n")
                lines.append(f"- 惯习类型: {hab_type}")
                lines.append(f"- 涉及场域: {', '.join(fields) if fields else '未识别'}")
                lines.append(f"- 对应强度: {strength_corr}")
                if analysis:
                    lines.append(f"- 对应分析: {analysis}")
            lines.append("")

        memo = analysis_result.get("methodology_memo", [])
        if memo:
            lines.append("## 惯习理论方法论备忘录\n")
            for i, m in enumerate(memo, 1):
                lines.append(f"{i}. {m}")
            lines.append("")

        return "\n".join(lines)


def detect_habitus(text: str, actors: List[str] = None) -> Dict:
    """习性检测入口函数"""
    detector = HabitustDetector()
    return detector.detect_habitus(text, actors)


if __name__ == "__main__":
    test_text = """
    王教授习惯于每天早上去图书馆研究，倾向于选择理论性强的课题。
    他自然而然地用学术标准评判事物，不自觉地维护学术场域的规则。
    他的品位偏向理论深度，实践中总是追求创新。

    张企业家习惯于应酬交际，倾向于投资回报率高的项目。
    他自然而然地用商业眼光看问题，实践中总是追求利润最大化。
    他的品位偏向实用价值。
    """

    actors = ["王教授", "张企业家"]
    result = detect_habitus(test_text, actors)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n" + "=" * 60)
    print(HabitustDetector().generate_habitus_report(result))
