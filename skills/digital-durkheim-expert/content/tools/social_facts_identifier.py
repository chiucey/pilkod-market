#!/usr/bin/env python3
"""
digital-durkheim-expert - 社会事实识别工具
识别数据中的社会事实（外在性、强制性、普遍性）
基于涂尔干《社会学方法的准则》

【方法论说明】
本工具不包含任何硬编码关键词匹配。所有社会事实判断由LLM根据理论备忘录完成。
工具仅负责：数据清洗、空结构返回、方法论引导。
"""

from typing import Dict, List, Any, TypedDict
import json


# ---------------------------------------------------------------------------
# 涂尔干社会事实理论备忘录（供LLM判断时参考）
# ---------------------------------------------------------------------------
SOCIAL_FACTS_THEORY_MEMO = """
=== 涂尔干社会事实（Social Facts）理论备忘录 ===

【核心定义】（《社会学方法的准则》, 1895）
"社会事实是存在于个人意识之外的任何行为方式，……具有强制性。"

【三大判别标准】

1. 外在性（Exteriority）:
   - 社会事实独立于个体意志而存在
   - 不是个人心理现象的简单加总
   - 分析要点：
     * 该规范/价值观/制度是否先于个体存在？
     * 个体能否单方面改变它？
     * 它是否超越个人生命周期？

2. 强制性（Constraint/Coerciveness）:
   - 社会事实对个体施加外在压力
   - 表现为：规范、期待、制裁
   - 分析要点：
     * 违背该社会事实会有什么后果？
     * 是否存在社会制裁（惩罚或奖励）？
     * 是否存在"应当/必须/禁止"的行为规范？

3. 普遍性（Generality）:
   - 社会事实在社会或群体中广泛存在
   - 不是个别现象
   - 分析要点：
     * 该现象在多大范围内被共享？
     * 是否具有跨个体的一致性？

【社会事实的两分法】

物质性社会事实（Material Social Facts）:
- 具有物理存在形式的外在制度
- 典型：法律、 政治组织、教育制度、宗教组织、经济制度
- 分析要点：是否有明确的机构/组织形态？

精神性社会事实（Non-material / Moral Social Facts）:
- 存在于集体意识中的道德/价值观/信仰
- 典型：集体情感、共同信念、社会潮流、时尚
- 分析要点：是否弥漫于社会但无物理形态？

【涂尔干法则（Durkheim's Rule）】
"将社会事实视为事物"（treat social facts as things）
—— 即用客观实证方法来研究主观意义的社会现象

【分析方法论】
- 三标准是分析性工具，不必全部满足才称为社会事实
- 关注制度化的程度：法律 > 惯例 > 时尚
- 社会事实是不断再生产的过程，需分析其再生产机制
- 典型社会事实类别（供LLM识别）：
  * 法律规范（外在+强制+普遍）
  * 道德规范（精神+强制+普遍）
  * 宗教信仰（精神+强制+普遍）
  * 社会制度/组织（物质+强制+普遍）
  * 集体意识/社会共识（精神+弱强制+普遍）
"""


class SocialFactDimension(TypedDict, total=False):
    type: str | None       # 维度类型
    score: float | None    # 强度评分（LLM填充）
    evidence: List[str]    # 证据列表（LLM填充）
    description: str        # 维度描述


class SpecificFact(TypedDict, total=False):
    type: str | None       # 具体类型（LLM填充）
    evidence: List[str]    # 证据（LLM填充）
    category: str | None   # 物质性/精神性（LLM填充）


class SocialFactsIdentifier:
    """社会事实识别器（无关键词匹配版）"""

    def __init__(self):
        self.identified_facts: List[Dict] = []

    def identify_social_facts(
        self, data: Any, analysis_type: str = "general"
    ) -> Dict:
        """
        识别社会事实（返回空结构供LLM填充）

        参数:
            data: 分析数据
            analysis_type: 分析类型

        返回:
            含空结构的社会事实识别结果，需LLM根据 theory_memo 填充
        """
        raw_text = self._convert_to_text(data)

        result: Dict = {
            "data_type": type(data).__name__,
            "analysis_type": analysis_type,
            "dimensions": {
                "externality": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "外在性 - 社会事实独立于个体存在",
                },
                "coerciveness": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "强制性 - 社会事实对个体施加外在压力",
                },
                "generality": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "普遍性 - 社会事实在社会中广泛存在",
                },
                "functionality": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "功能性 - 社会事实对社会具有维持整合的作用",
                },
                "materiality": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "物质性/精神性 - 社会事实的存在形式",
                },
            },
            "specific_facts": [],  # 具体社会事实列表（LLM填充）
            "strength": None,       # 社会事实强度（LLM填充）
            "classification": {
                "is_social_fact": None,  # 是否为社会事实（LLM填充）
                "fact_type": None,       # 物质性/精神性/混合型（LLM填充）
                "confidence": None,      # 置信度（LLM填充）
            },
            "verdict": None,          # 总体判断（LLM填充）
            # --- 方法论引导 ---
            "theory_memo": SOCIAL_FACTS_THEORY_MEMO.strip(),
            "raw_data_for_llm": raw_text[:5000],
        }

        return result

    def _convert_to_text(self, data: Any) -> str:
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            return json.dumps(data, ensure_ascii=False)
        elif isinstance(data, list):
            return " ".join(str(item) for item in data)
        else:
            return str(data)

    def generate_report(self, result: Dict) -> str:
        """生成分析报告框架（供LLM填充内容）"""
        lines = []
        lines.append("# 社会事实识别报告\n")
        lines.append(f"## 总体判断: {result.get('verdict', '（待LLM填充）')}\n")
        lines.append("## 维度分析（需LLM根据理论备忘录填充）\n")
        for dim_name, data in result.get("dimensions", {}).items():
            lines.append(f"- {dim_name}: score={data.get('score')}, evidence={data.get('evidence')}")
        lines.append("")
        lines.append("## 具体社会事实（需LLM识别）\n")
        for fact in result.get("specific_facts", []):
            lines.append(f"- type={fact.get('type')}, category={fact.get('category')}")
        return "\n".join(lines)


def identify_social_facts(data: Any, analysis_type: str = "general") -> Dict:
    """社会事实识别入口函数"""
    return SocialFactsIdentifier().identify_social_facts(data, analysis_type)


if __name__ == "__main__":
    test_data = """
    在现代社会，法律制度是典型的社会事实。法律具有外在性，
    它独立于个体存在，不以个人意志为转移。同时，法律具有强制性，
    公民必须遵守，否则将面临法律制裁。法律在社会中普遍存在，
    维护着社会秩序和稳定。
    """
    result = identify_social_facts(test_data)
    print("=== 返回结构（需LLM填充） ===")
    print(f"verdict: {result['verdict']}")
    print(f"strength: {result['strength']}")
    print(f"\n理论备忘录（前300字）:\n{result['theory_memo'][:300]}")
