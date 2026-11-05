#!/usr/bin/env python3
"""
digital-durkheim-expert - 失范程度计算工具
计算社会失范（anomie）程度
基于涂尔干《自杀论》

【方法论说明】
本工具不包含任何硬编码关键词匹配。所有失范维度判断由LLM根据理论备忘录完成。
工具仅负责：数据清洗、空结构返回、方法论引导。
"""

from typing import Dict, List, Any, TypedDict
import json


# ---------------------------------------------------------------------------
# 涂尔干失范理论备忘录（供LLM判断时参考）
# ---------------------------------------------------------------------------
ANOMIE_THEORY_MEMO = """
=== 涂尔干失范（Anomie）理论备忘录 ===

【核心概念】
失范（Anomie）：社会规范对社会成员的约束力减弱或消失的状态。
涂尔干在《自杀论》中提出：社会失范导致个体联结断裂，是利己型自杀的重要原因。

【失范产生的社会条件】
1. 社会快速变迁期：传统规范失去效力，新规范尚未建立
   - 信号：人们谈论"规则变了"、"没有标准了"
2. 社会分工不完善：道德规范未随经济分工扩展
   - 信号：缺乏行业道德、职业伦理
3. 社会联结（social bonds）断裂
   - 涂尔干三要素：社会整合（social integration）的缺失

【失范的五个分析维度】（本工具预设维度，强度由LLM判断）

1. 规范真空（Normlessness）:
   - 社会规范缺失、混乱或相互冲突
   - 分析要点：人们是否表达"没有规则可循"、"规则不清楚"？
   - 涂尔干核心：规范是社会整合的制度化表达

2. 价值崩溃（Value Collapse）:
   - 共同价值观瓦解，道德相对主义弥漫
   - 分析要点：是否出现"没有对错"、"价值观多元到虚无"？
   - 信号词：道德滑坡、信念缺失、相对主义

3. 目标迷失（Goal Disorientation）:
   - 社会或个体层面的目标感丧失
   - 分析要点：是否表达"不知道追求什么"、"没有方向"？
   - 涂尔干分析：欲望的无限性与满足手段的有限性之间的张力

4. 失控感（Control Loss）:
   - 对社会或个人命运失去控制
   - 分析要点：是否表达"无法控制局面"、"不确定性增加"？
   - 心理后果：焦虑、无力感、抑郁

5. 社会联结断裂（Social Disintegration）:
   - 社会整合机制失效，个体原子化
   - 分析要点：是否表达"社会不团结"、"人际疏离"？
   - 最严重形式：涂尔干所谓的"社会解体"

【失范与自杀的关联】
- 利己型自杀（Egoistic）：社会整合过低
- 利他型自杀（Altruistic）：社会整合过高
- 失范型自杀（Anomic）：规范失效
- 现代性悖论：物质进步但道德规范未能同步发展

【分析方法论】
- 失范是程度问题，不是二元判断
- 同一社会中不同群体的失范程度可能不同（需分层分析）
- 纵向比较：比较不同历史时期或生命周期的失范变化
- 不能仅凭出现"迷茫"等词就判定失范，需分析其社会结构性原因
"""


class AnomieDimension(TypedDict, total=False):
    type: str | None       # 维度类型
    score: float | None    # 强度评分（LLM填充）
    evidence: List[str]    # 证据列表（LLM填充）
    description: str        # 维度描述


class AnomieLevel(TypedDict, total=False):
    level: str | None      # 失范等级（LLM填充）
    degree: float | None   # 程度值（LLM填充）
    explanation: str


class AnomieCalculator:
    """失范程度计算器（无关键词匹配版）

    所有失范维度判断由调用方/LLM完成。
    """

    def __init__(self):
        self.anomie_scores: List[float] = []

    def calculate_anomie(self, data: Any, time_period: str = None) -> Dict:
        """
        计算失范程度（返回空结构供LLM填充）

        参数:
            data: 分析数据
            time_period: 时间段（用于纵向比较）

        返回:
            含空结构的失范分析结果，需LLM根据 theory_memo 填充
        """
        raw_text = self._convert_to_text(data)

        result: Dict = {
            "data_type": type(data).__name__,
            "time_period": time_period,
            "dimensions": {
                "normlessness": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "规范真空 - 社会规范缺失或相互冲突",
                },
                "value_collapse": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "价值崩溃 - 共同价值观瓦解",
                },
                "goal_disorientation": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "目标迷失 - 目标感和方向感丧失",
                },
                "control_loss": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "失控感 - 对社会或个人命运失去控制",
                },
                "disintegration": {
                    "type": None,
                    "score": None,
                    "evidence": [],
                    "description": "社会联结断裂 - 社会整合机制失效",
                },
            },
            "overall_anomie": None,
            "anomie_level": None,
            "sources": [],              # 主要来源（LLM填充）
            "explanation": "",
            # --- 方法论引导 ---
            "theory_memo": ANOMIE_THEORY_MEMO.strip(),
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


def calculate_anomie(data: Any, time_period: str = None) -> Dict:
    """失范程度计算入口函数"""
    return AnomieCalculator().calculate_anomie(data, time_period)


if __name__ == "__main__":
    test_data = """
    当前社会处于快速转型期，传统规范失去约束力，
    新的规范尚未建立。价值观念多元化，传统道德滑坡。
    很多人感到迷茫和无所适从，不知道什么是正确的。
    社会不稳定因素增加，不确定性增强。
    """
    result = calculate_anomie(test_data)
    print("=== 返回结构（需LLM填充） ===")
    print(f"overall_anomie: {result['overall_anomie']}")
    print(f"anomie_level: {result['anomie_level']}")
    print(f"\n理论备忘录（前300字）:\n{result['theory_memo'][:300]}")
