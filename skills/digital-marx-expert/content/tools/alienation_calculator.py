#!/usr/bin/env python3
"""
digital-marx-expert - 异化程度计算工具
计算劳动异化程度：产品异化、劳动过程异化、自我异化、类本质异化
基于马克思《1844年经济学哲学手稿》

本文件不包含任何硬编码关键词判断，仅作为数据结构容器+方法论备忘录，
所有实质性判断由LLM基于异化理论框架完成。
"""

from typing import Dict, List, Any
import json


# ---------------------------------------------------------------------------
# 异化理论备忘录（给LLM的引导）
# ---------------------------------------------------------------------------
ALIENATION_THEORY_MEMO = """
=== 异化理论备忘录：马克思《1844年经济学哲学手稿》===

【理论核心】
马克思在《1844年经济学哲学手稿》中指出，资本主义制度下劳动异化表现为四个基本维度：

1. 产品异化（Product Alienation）
   - 定义：劳动者创造的劳动产品不属于劳动者，而被资本家占有
   - 识别信号：劳动者失去对产品的控制，产品作为异己力量与劳动者对立
   - 提问方向：劳动者与产品之间是什么关系？谁占有产品？谁从中获益？

2. 劳动过程异化（Process Alienation）
   - 定义：劳动对劳动者来说是外在的、强制的、痛苦的活动，而非自我实现
   - 识别信号：劳动是被迫的、非自愿的，劳动者在劳动中感到痛苦和压抑
   - 提问方向：劳动者如何看待劳动过程？劳动是自我实现还是谋生手段？

3. 自我异化（Self Alienation）
   - 定义：劳动者无法实现自我的潜能和全面发展，人格被分裂
   - 识别信号：劳动者只是机器的附属品，无法发挥创造性和个性
   - 提问方向：劳动是否允许个人才能的发挥？劳动者是否有自我发展的空间？

4. 类本质异化（Species Alienation）
   - 定义：劳动者失去人的类本质——自由自觉的活动和社会性本质
   - 识别信号：劳动者与他人、与社会的联系被削弱，社会性交往受损
   - 提问方向：劳动者之间的社会关系如何？是否存在有意识的合作与交往？

【数字劳动异化扩展维度】（可选，针对数字劳动）
   - 数据监控：算法对劳动者的实时监控与评分
   - 平台控制：平台对劳动者的准入与淘汰机制
   - 算法管理：算法驱动的任务分配与绩效考核
   - 数据剥削：用户/劳动者数据的无偿占有

【评估原则】
- LLM应基于上述四个核心维度，结合具体文本内容进行判断
- 不依赖关键词频率，而依赖对劳动关系的整体理解
- 判断结果填入返回结构中的 None 字段
"""


class AlienationCalculator:
    """异化程度计算器（无硬编码关键词）"""

    def __init__(self):
        self.calculation_results = []

    def calculate_alienation(self, data: Any, labor_type: str = "general") -> Dict:
        """
        计算异化程度

        参数:
            data: 分析数据（文本、字典或列表）
            labor_type: 劳动类型（general/digital）

        返回:
            异化程度分析结果（各维度 type=None，供LLM填充）
        """
        # 结构化输出骨架（所有实质性类型判断由LLM完成）
        result = {
            "data_type": type(data).__name__,
            "labor_type": labor_type,
            "theory_memo": ALIENATION_THEORY_MEMO.strip(),
            "dimensions": {
                # 以下 type=None 表示需要LLM根据理论框架判断填充
                "product_alienation": {
                    "type": None,  # LLM判断: "high"/"medium"/"low"/"none"
                    "evidence": None,  # LLM提取的证据文本
                    "score": None,  # LLM评分: 0.0-1.0
                    "description": "产品异化 - 劳动产品不属于劳动者",
                },
                "process_alienation": {
                    "type": None,
                    "evidence": None,
                    "score": None,
                    "description": "劳动过程异化 - 劳动对劳动者来说是外在的",
                },
                "self_alienation": {
                    "type": None,
                    "evidence": None,
                    "score": None,
                    "description": "自我异化 - 劳动者无法实现自我",
                },
                "species_alienation": {
                    "type": None,
                    "evidence": None,
                    "score": None,
                    "description": "类本质异化 - 劳动者失去社会性",
                },
                "digital_alienation": {
                    "type": None,
                    "evidence": None,
                    "score": None,
                    "description": "数字劳动异化 - 数字时代的特殊异化形式（仅 digital 劳动类型填入）",
                },
            },
            "overall_alienation": None,  # LLM综合评分: 0.0-1.0
            "alienation_level": None,  # LLM判断: "极度异化"/"高度异化"/"中度异化"/"轻度异化"/"无明显异化"
            "main_sources": None,  # LLM识别的主要异化来源（top 3）
            "explanation": None,  # LLM基于理论的解释
        }

        self.calculation_results.append(result)
        return result


def calculate_alienation(data: Any, labor_type: str = "general") -> Dict:
    """
    异化程度计算入口函数

    参数:
        data: 分析数据
        labor_type: 劳动类型（general/digital）

    返回:
        异化程度分析结果（空结构 + 方法论备忘录）
    """
    calculator = AlienationCalculator()
    return calculator.calculate_alienation(data, labor_type)


if __name__ == "__main__":
    # 测试
    test_data = """
    该公司的流水线工人每天重复同样的动作十个小时。
    生产的产品不属于自己，而是被公司占有。
    工人只是机器的附属品，无法发挥创造性。
    劳动对他们来说只是谋生手段，没有任何乐趣。
    工作强度大，压力大，没有任何自我实现可言。
    """

    result = calculate_alienation(test_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
