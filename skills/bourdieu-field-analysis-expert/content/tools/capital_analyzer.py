#!/usr/bin/env python3
"""
bourdieu-field-analysis-expert - 资本分析工具
分析经济资本、文化资本、社会资本、象征资本的分布
纯数据结构管理 + 方法论备忘录，引导LLM做定性判断
"""

from typing import Dict, List, Any
from collections import defaultdict
import json


# 资本理论方法论备忘录（供LLM参考的判断原则，不含任何关键词）
CAPITAL_THEORY_MEMO = [
    "资本定义：资本是积累的劳动，是场域中行动者争夺的核心对象。布迪厄的核心洞见是：不同类型的资本可以相互转换（conversion），但转换需要付出代价，且不同场域对不同资本的兑换率不同。",
    "经济资本判断标准：如何识别文本中的经济资本描述？关注：（1）物质财富（金钱、房产、车辆、收藏品）；（2）收入与薪酬相关描述；（3）投资、利润、资产相关行为。注意区分：描述拥有某物（静态资本）vs. 描述资本运作行为（动态过程）。",
    "文化资本判断标准：文化资本有三种存在形态，需分别判断：（1）身体化状态（内化于身心的文化知识、教养、品位，往往'自然而然'不刻意）；（2）客观化状态（书籍、艺术品、乐器等文化商品）；（3）制度化状态（学历文凭、资格证书、职称）。文本中分别对应什么形态？",
    "社会资本判断标准：社会资本是行动者通过社会网络能够获取的资源总和。判断要点：（1）强关系 vs. 弱关系（家庭/密友 vs. 泛泛之交）；（2）网络规模与异质性（能触及多少不同圈子的人）；（3）网络密度（同质性高意味着重复资源，异质性高意味着信息优势）；（4）动员社会资本的能力（是否'用得上'这些人脉）。",
    "符号资本判断标准：符号资本（象征资本）是社会公认的声望与荣誉，可被用来换取其他资本。判断要点：（1）头衔、称号、荣誉（如'教授'、'大师'、'获奖者'）；（2）声誉描述（'德高望重'、'广受尊敬'）；（3）符号资本具有相对性（在A场域的荣誉到B场域可能无效）。",
    "资本转换分析：资本转换（conversion）是场域运作的关键机制。常见转换路径：（1）经济→文化：用金钱购买教育、文化商品（买学区房、请家教）；（2）文化→经济：将学历、知识变现（高学历带来高收入）；（3）社会→文化：通过关系获得教育机会；（4）符号→经济：声誉变现（代言、品牌合作）。分析文本中是否存在这些转换行为。",
]


class CapitalAnalyzer:
    """资本分析器（纯数据管理 + 方法论引导）"""

    def __init__(self):
        self.capital_distributions: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.actor_capitals: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.capital_conversions: List[Dict[str, Any]] = []

    def analyze_capital_distribution(self, text: str, actors: List[str] = None) -> Dict:
        """
        分析资本分布

        参数:
            text: 分析文本
            actors: 行动者列表（可选）

        返回:
            资本分布分析结果（空结构，由LLM填充定性判断）
        """
        return {
            # LLM需要判断：文本中出现了哪些类型的资本？
            "capital_types": {},  # {capital_type: [evidence_objects, ...], ...} — LLM自行判断
            # LLM需要判断：每个行动者分别拥有哪些资本？量级如何？
            "actor_capitals": {},  # {actor_name: {economic, cultural, social, symbolic, evidence}, ...}
            # LLM需要汇总各类型资本的总体分布情况
            "total_capitals": {},  # {capital_type: total_count_or_score, ...}
            # LLM需要识别文本中的资本转换行为
            "conversions": [],  # [{type, description, evidence_segment}, ...]
            # LLM需要计算资本分布的异质性程度
            "heterogeneity_score": None,  # 0.0-1.0 / None
            # 方法论备忘录，供LLM参考
            "methodology_memo": CAPITAL_THEORY_MEMO,
        }

    def generate_capital_report(self, analysis_result: Dict) -> str:
        """
        生成资本分析报告

        参数:
            analysis_result: analyze_capital_distribution() 的返回结果

        返回:
            格式化报告文本
        """
        lines = []
        lines.append("# 资本分布分析报告\n")
        lines.append("> 本报告由LLM基于布迪厄资本理论生成，工具仅提供数据结构管理。\n")

        capitals = analysis_result.get("total_capitals", {})
        if capitals:
            lines.append("## 资本分布\n")
            cap_names = {
                "economic": "经济资本",
                "cultural": "文化资本",
                "social": "社会资本",
                "symbolic": "象征资本",
            }
            for cap_type, val in capitals.items():
                lines.append(f"- {cap_names.get(cap_type, cap_type)}: {val}")
            lines.append("")
        else:
            lines.append("## 资本分布\n")
            lines.append("- 未检测到明确的资本类型\n")
            lines.append("")

        hetero = analysis_result.get("heterogeneity_score")
        lines.append("## 资本异质性\n")
        if hetero is not None:
            lines.append(f"异质性分数: {hetero:.2%}")
        else:
            lines.append("异质性分数: 未评估")
        lines.append("")

        actor_capitals = analysis_result.get("actor_capitals", {})
        if actor_capitals:
            lines.append("## 行动者资本状况\n")
            cap_names_short = {
                "economic": "经济",
                "cultural": "文化",
                "social": "社会",
                "symbolic": "象征",
            }
            for actor, caps in actor_capitals.items():
                lines.append(f"### {actor}\n")
                for cap_type, val in caps.items():
                    if cap_type == "evidence":
                        continue
                    cname = cap_names_short.get(cap_type, cap_type)
                    lines.append(f"- {cname}资本: {val}")
                ev_list = caps.get("evidence", [])
                if ev_list:
                    lines.append(f"- 证据摘要: {', '.join(str(e) for e in ev_list[:3])}")
            lines.append("")

        conversions = analysis_result.get("conversions", [])
        if conversions:
            lines.append("## 资本转换\n")
            for conv in conversions[:5]:
                ctype = conv.get("type", "未分类")
                desc = conv.get("description", "")
                lines.append(f"- **{ctype}**: {desc}")
            lines.append("")

        memo = analysis_result.get("methodology_memo", [])
        if memo:
            lines.append("## 资本理论方法论备忘录\n")
            for i, m in enumerate(memo, 1):
                lines.append(f"{i}. {m}")
            lines.append("")

        return "\n".join(lines)


def analyze_capital_distribution(text: str, actors: List[str] = None) -> Dict:
    """资本分析入口函数"""
    analyzer = CapitalAnalyzer()
    return analyzer.analyze_capital_distribution(text, actors)


if __name__ == "__main__":
    test_text = """
    王教授拥有高学历（文化资本）和大学教职（象征资本）。
    他通过教学和研究积累学术声誉，每年收入数十万元（经济资本）。
    他与社会各界人士有广泛联系（社会资本），经常参加学术会议。

    张企业家拥有大量财富（经济资本），投资教育事业，
    购买艺术品收藏（文化资本），与社会名流交往（社会资本），
    获得慈善家称号（象征资本）。
    """

    actors = ["王教授", "张企业家"]
    result = analyze_capital_distribution(test_text, actors)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n" + "=" * 60)
    print(CapitalAnalyzer().generate_capital_report(result))
