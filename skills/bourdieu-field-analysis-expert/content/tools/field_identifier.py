#!/usr/bin/env python3
"""
bourdieu-field-analysis-expert - 场域边界识别工具
基于布迪厄场域理论识别分析场域的边界
纯数据结构管理 + 方法论备忘录，引导LLM做定性判断
"""

from typing import Dict, List, Any, Optional
import json


# 场域理论方法论备忘录（供LLM参考的判断原则，不含任何关键词）
FIELD_THEORY_MEMO = [
    "场域定义：场域是围绕特定类型的资本争夺而组织起来的社会空间，具有相对自主性。识别场域的第一步是寻找围绕特定利益（stakes）展开争夺的行动者群体。",
    "行动者识别原则：谁是这场争夺中的参与者？注意区分：（1）掌权者（占据支配位置，利用规则维持优势）；（2）新人/挑战者（试图颠覆现有规则或进入场域）；（3）被排斥者（被排除在场域之外或处于被支配位置）。",
    "资本类型判断：场域中流通的资本是什么？布迪厄区分了四种基本资本类型——经济资本（物质财富与金钱）、文化资本（教育、知识、品位）、社会资本（关系网络与社会联系）、符号资本（声望、声誉、荣誉）。不同场域以不同类型的资本为主战场。",
    "位置关系分析：行动者之间的位置关系如何？注意：（1）客观位置（占据的职位、头衔、资源量）；（2）位置取用（position-taking，即对同一位置的策略性使用）；（3）位置知觉（行动者对自身位置的感知与评价）。",
    "场域边界判定：如何判断一个场域的边界？标准包括：（1）存在特定类型资本的争夺；（2）有一套相对独立的游戏规则和评判标准；（3）局内人与局外人有明显区别；（4）进入场域需要具备特定的入场资本。",
    "场域自主性评估：目标场域相对于其他场域的自主程度如何？高度自主的场域（如科学场域）有其内部逻辑；低度自主的场域（如政治场域）受外部力量（尤其是经济资本）强烈影响。评估自主性有助于理解场域运作规律。",
]


class FieldIdentifier:
    """场域边界识别器（纯数据管理 + 方法论引导）"""

    def __init__(self):
        self.identified_fields: List[str] = []
        self.field_actors: Dict[str, List[str]] = {}
        self.field_indicators: Dict[str, List[str]] = {}
        self.boundary_evidence: List[Dict[str, Any]] = []

    def identify_field_boundaries(self, text: str, context: Optional[str] = None) -> Dict:
        """
        识别场域边界

        参数:
            text: 分析文本
            context: 上下文信息（可选）

        返回:
            场域识别结果（空结构，由LLM填充定性判断）
        """
        return {
            # LLM需要判断：文本中是否存在明确的场域？若存在，指出场域名称
            "possible_fields": [],  # [{field_name, confidence, reasoning}, ...] — LLM自行判断
            # LLM需要判断：文本中出现了哪些场域指标类型？并说明判断依据
            "indicators_found": {},  # {indicator_type: [evidence_segments], ...} — LLM自行填充
            # LLM需要判断：基于文本证据，场域边界强度如何？给出理由
            "boundary_strength": {
                "strength": None,      # "strong" / "moderate" / "weak" / None
                "score": None,         # 0.0–1.0 / None
                "reasoning": None,    # 判断理由（字符串）
            },
            # LLM需要列出文本中出现的行动者，并判断他们属于哪个场域
            "field_actors": {},  # {field_name: [actor_names, ...], ...} — LLM自行判断
            # LLM需要列出支撑场域判断的文本证据片段
            "evidence": [],  # [{field, evidence_segment, indicator_type}, ...] — LLM自行填充
            # 方法论备忘录，供LLM参考
            "methodology_memo": FIELD_THEORY_MEMO,
        }

    def extract_field_actors(self, text: str, field_name: str) -> List[str]:
        """
        提取特定场域的行动者

        参数:
            text: 分析文本
            field_name: 场域名称

        返回:
            行动者列表（空结构，由LLM填充）
        """
        return []

    def generate_field_report(self, analysis_result: Dict) -> str:
        """
        生成场域识别报告

        参数:
            analysis_result: identify_field_boundaries() 的返回结果

        返回:
            格式化报告文本
        """
        lines = []
        lines.append("# 场域边界识别报告\n")
        lines.append("> 本报告由LLM基于布迪厄场域理论生成，工具仅提供数据结构管理。\n")

        fields = analysis_result.get("possible_fields", [])
        if fields:
            lines.append("## 识别的场域\n")
            for field in fields:
                fname = field.get("field_name", "未知场域")
                conf = field.get("confidence", "N/A")
                reasoning = field.get("reasoning", "")
                lines.append(f"- **{fname}**（置信度: {conf}）")
                if reasoning:
                    lines.append(f"  - 判断依据: {reasoning}")
            lines.append("")
        else:
            lines.append("## 识别的场域\n")
            lines.append("- 未能从文本中识别出明确的场域结构\n")
            lines.append("")

        boundary = analysis_result.get("boundary_strength", {})
        strength = boundary.get("strength", "未评估")
        score = boundary.get("score", "N/A")
        reasoning = boundary.get("reasoning", "")
        lines.append("## 场域边界强度评估\n")
        lines.append(f"- 强度等级: {strength}")
        lines.append(f"- 分数: {score}")
        if reasoning:
            lines.append(f"- 评估理由: {reasoning}")
        lines.append("")

        actors = analysis_result.get("field_actors", {})
        if actors:
            lines.append("## 场域行动者\n")
            for fname, actor_list in actors.items():
                lines.append(f"- **{fname}**: {', '.join(actor_list) if actor_list else '无'}")
            lines.append("")

        evidence = analysis_result.get("evidence", [])
        if evidence:
            lines.append("## 关键文本证据\n")
            for ev in evidence[:5]:
                seg = ev.get("evidence_segment", "")
                fld = ev.get("field", "")
                lines.append(f"- [{fld}] {seg}")
            lines.append("")

        memo = analysis_result.get("methodology_memo", [])
        if memo:
            lines.append("## 场域理论方法论备忘录\n")
            for i, m in enumerate(memo, 1):
                lines.append(f"{i}. {m}")
            lines.append("")

        return "\n".join(lines)


def identify_field_boundaries(text: str, context: Optional[str] = None) -> Dict:
    """场域边界识别入口函数"""
    identifier = FieldIdentifier()
    return identifier.identify_field_boundaries(text, context)


if __name__ == "__main__":
    test_text = """
    在学术场域中，大学教授和科研人员通过发表论文来竞争学术资本。
    学术期刊的编辑掌握着重要的符号资本，决定着哪些研究能够发表。
    大学的排名竞争日益激烈，各校争夺优秀的教授和学生资源。
    学术会议提供了交流和建立学术网络的平台。
    """

    result = identify_field_boundaries(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n" + "=" * 60)
    print(FieldIdentifier().generate_field_report(result))
