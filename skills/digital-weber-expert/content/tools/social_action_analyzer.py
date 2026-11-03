#!/usr/bin/env python3
"""
digital-weber-expert - 社会行动类型分析工具
分析社会行动类型：目的理性、价值理性、传统、情感
基于韦伯社会行动理论

【方法论说明】
本工具不包含任何硬编码关键词匹配。所有行动类型判断由LLM根据理论备忘录完成。
工具仅负责：数据清洗、空结构返回、方法论引导。
"""

from typing import Dict, List, Any, TypedDict
import json


# ---------------------------------------------------------------------------
# 韦伯社会行动类型备忘录（供LLM判断时参考）
# ---------------------------------------------------------------------------
SOCIAL_ACTION_THEORY_MEMO = """
=== 韦伯社会行动理论备忘录 ===

【四类社会行动类型】（ideal type，非现实中的固定类别）

1. 目的理性行动（Zweckrationales Handeln）:
   - 行动者对手段和目标进行理性计算
   - 对不同目标的相对价值进行权衡
   - 分析要点：是否有目标-手段推理链？是否提及成本/收益/效率？
   - 陷阱：出现"目标"等词不等于目的理性，要看是否有计算过程

2. 价值理性行动（Wertrationales Handeln）:
   - 由对某种伦理、美学、宗教或其他形式的内在价值信仰驱动
   - 行动本身被视为有价值的，不考虑后果
   - 分析要点：是否有绝对价值表述？"无论结果如何都要做"？
   - 典型信号：义务、信念、原则、使命、责任

3. 情感行动（Affektives Handeln）:
   - 由情感状态（激情、愤怒、爱、恐惧）直接驱动
   - 未经深思熟虑，是非理性的或前理性的
   - 分析要点：是否有强烈情感词汇？是否描述即时反应而非计划行动？
   - 韦伯视角：情感行动在前现代占主导

4. 传统行动（Traditionales Handeln）:
   - 基于根深蒂固的习惯
   - 行动理由是"这件事一直这样做"
   - 分析要点：是否引用先例/传统/惯例作为行动依据？
   - 与情感行动一样属于"习惯性"行动

【分析方法论】
- 四种类型是理想类型（ideal type），现实行动通常是混合型
- 同一行动者可能同时展现多种类型，需分析主次
- 关注行动者的自我诠释（self-interpretation）
- 社会行动的主观意义（subjective meaning）是分析核心
"""


class SocialActionType(TypedDict, total=False):
    type: str | None       # 行动类型
    score: float | None    # 强度评分（LLM填充）
    evidence: List[str]    # 证据片段列表（LLM填充）
    description: str        # 类型描述


class SocialActionResult(TypedDict):
    types: Dict[str, SocialActionType]
    dominant: str | None        # 主导类型（LLM填充）
    dominant_score: float | None
    explanation: str
    theory_memo: str            # 方法论备忘录
    raw_data_for_llm: str       # 供LLM分析的原始文本


class SocialActionAnalyzer:
    """社会行动类型分析器（无关键词匹配版）"""

    def __init__(self):
        pass

    def analyze_social_action(self, data: Any) -> Dict:
        """
        分析社会行动类型（返回空结构供LLM填充）

        参数:
            data: 分析数据

        返回:
            含空结构的行动类型分析结果，需LLM根据 theory_memo 填充
        """
        raw_text = self._convert_to_text(data)

        result: Dict = {
            "types": {
                "purposive_rational": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "目的理性行动 - 目标导向的工具合理性",
                },
                "value_rational": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "价值理性行动 - 价值信念导向的合理性",
                },
                "affective": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "情感行动 - 情感/激情驱动的非理性行动",
                },
                "traditional": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "传统行动 - 基于习惯和惯例的行动",
                },
            },
            "dominant": None,
            "dominant_score": None,
            "explanation": "",
            "theory_memo": SOCIAL_ACTION_THEORY_MEMO.strip(),
            "raw_data_for_llm": raw_text[:5000],
        }
        return result

    def _convert_to_text(self, data: Any) -> str:
        if isinstance(data, str):
            return data
        return json.dumps(data, ensure_ascii=False)


def analyze_social_action(data: Any) -> Dict:
    """社会行动分析入口函数"""
    return SocialActionAnalyzer().analyze_social_action(data)


if __name__ == "__main__":
    test_data = "人们根据目标选择手段，通过理性计算来决定行动。"
    result = analyze_social_action(test_data)
    print("dominant:", result["dominant"])
    print("dominant_score:", result["dominant_score"])
    print("\n理论备忘录（首300字）:")
    print(result["theory_memo"][:300])
