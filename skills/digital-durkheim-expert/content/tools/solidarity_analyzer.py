#!/usr/bin/env python3
"""
digital-durkheim-expert - 团结类型分析工具
分析社会团结类型：机械团结、有机团结、混合型
基于涂尔干《社会分工论》

【方法论说明】
本工具不包含任何硬编码关键词匹配。所有团结类型判断由LLM根据理论备忘录完成。
工具仅负责：数据清洗、空结构返回、方法论引导。
"""

from typing import Dict, List, Any, TypedDict
import json


# ---------------------------------------------------------------------------
# 涂尔干社会团结理论备忘录（供LLM判断时参考）
# ---------------------------------------------------------------------------
SOLIDARITY_THEORY_MEMO = """
=== 涂尔干社会团结理论备忘录 ===

【核心问题】涂尔干之问：什么使社会成为可能？社会秩序如何维系？

【两种团结类型的对比】（ideal type）

1. 机械团结（Mechanical Solidarity）:
   - 存在于分工不发达的社会（传统社会）
   - 团结基础：成员之间的"相似性"（likeness）
   - 共同意识（collective conscience）强烈
   - 个人人格（individual personality）不发达
   - 分析要点：
     * 成员是否从事类似工作？
     * 是否有强烈的共同价值观/信仰/习惯？
     * 个体差异是否被压制？
   - 集体意识的两个层面：
     * 共享的情绪（shared sentiments）
     * 共享的道德准则（shared moral rules）

2. 有机团结（Organic Solidarity）:
   - 存在于高度分工的现代社会
   - 团结基础：成员之间的"差异性"（difference）+ 功能相互依赖
   - 共同意识弱化，个人人格发展
   - 分析要点：
     * 社会分工是否发达？
     * 不同职业/角色之间是否有功能依赖？
     * 个人权利意识是否增强？
   - 关键机制："看不见的手"——每个人的功能都服务于整体

3. 过渡型团结（Transitional Solidarity）:
   - 机械团结和有机团结并存
   - 社会转型期的典型特征
   - 分析要点：两种机制是否同时可见？

【团结强度分析】
- 团结强度不等于团结类型
- 机械团结强度：相似性程度 X 集体意识强度
- 有机团结强度：分工发达程度 X 相互依赖程度
- 现代性问题：有机团结的规范基础是否足够稳固？

【集体意识概念】
- 涂尔干：集体意识是"社会成员平均拥有的信仰和情感的共同体"
- 功能：维系社会整合，将个体联结为整体
- 现代性悖论：有机团结中集体意识弱化，但需要新的"契约性规范"替代

【分析方法论】
- 不能简单地说"传统社会=机械团结，现代社会=有机团结"
- 需分析具体社会机制的运作，而非仅凭"分工"等词
- 团结类型可能是共存的（阶层差异、地区差异）
- 关注团结的制度化形式：法律系统、宗教、教育
"""


class SolidarityType(TypedDict, total=False):
    type: str | None       # 团结类型
    score: float | None    # 强度评分（LLM填充）
    evidence: List[str]    # 证据列表（LLM填充）
    description: str        # 类型描述


class SolidarityAnalyzer:
    """团结类型分析器（无关键词匹配版）"""

    def __init__(self):
        self.analysis_results: List[Dict] = []

    def analyze_solidarity(self, data: Any, society_type: str = None) -> Dict:
        """
        分析社会团结类型（返回空结构供LLM填充）

        参数:
            data: 分析数据
            society_type: 社会类型（传统/现代/转型）

        返回:
            含空结构的团结类型分析结果，需LLM根据 theory_memo 填充
        """
        raw_text = self._convert_to_text(data)

        result: Dict = {
            "data_type": type(data).__name__,
            "society_type": society_type,
            "types": {
                "mechanical": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "机械团结 - 基于成员相似性和共同集体意识",
                },
                "organic": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "有机团结 - 基于社会分工和成员间的功能相互依赖",
                },
                "transitional": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "过渡型团结 - 机械团结向有机团结转变的混合状态",
                },
            },
            "dominant_type": None,
            "dominant_type_score": None,
            "solidarity_strength": None,
            "explanation": "",
            # --- 方法论引导 ---
            "theory_memo": SOLIDARITY_THEORY_MEMO.strip(),
            "raw_data_for_llm": raw_text[:5000],
        }

        self.analysis_results.append(result)
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


def analyze_solidarity(data: Any, society_type: str = None) -> Dict:
    """团结类型分析入口函数"""
    return SolidarityAnalyzer().analyze_solidarity(data, society_type)


if __name__ == "__main__":
    test_data = """
    在传统农村社会，成员之间高度相似，共享相同的价值观和信念。
    集体意识强烈，社会规范约束着每个人的行为。
    人们从事类似的工作，遵循相同的传统习俗。
    个人与集体紧密联系，社会凝聚力强。
    """
    result = analyze_solidarity(test_data)
    print("=== 返回结构（需LLM填充） ===")
    print(f"dominant_type: {result['dominant_type']}")
    print(f"solidarity_strength: {result['solidarity_strength']}")
    print(f"\n理论备忘录（前300字）:\n{result['theory_memo'][:300]}")
