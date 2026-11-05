#!/usr/bin/env python3
"""
actor-network-analysis-expert - 主分析协调器
协调 ANT 分析流程：行动者提取 → 对称性分析 → 翻译四阶段 → 争议记录 → 饱和度评估

核心原则：定性分析决策（行动者分类、翻译阶段判断）由 LLM 完成。
本工具管理数据结构和工作流。
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from actor_extractor import ActorExtractor
from symmetry_checker import check_symmetry
from translation_stage_controller import TranslationStageController
from controversy_recorder import ControversyRecorder, CONTROVERSY_METHODOLOGY_MEMO
import assess_network_saturation as saturation


class SkillAnalyzer:
    """ANT 分析协调器"""

    WORKFLOW_STAGES = [
        "actor_extraction",
        "symmetry_check",
        "translation",
        "controversy",
        "saturation",
    ]

    def __init__(self, working_dir: str = "./session"):
        self.working_dir = working_dir
        self.session_file = os.path.join(working_dir, "session_state.json")
        self._ensure_working_dir()

    def _ensure_working_dir(self):
        os.makedirs(self.working_dir, exist_ok=True)

    def analyze(
        self,
        data: Dict[str, Any],
        stage: str = "actor_extraction",
        **kwargs,
    ) -> Dict[str, Any]:
        raw_text = data.get("text", "") or data.get("input_text", "")
        parsed_actors = data.get("actors", [])  # from parse_markdown_case

        # ── 阶段1: 行动者提取 ──────────────────────────────────────────
        actor_result = self._run_actor_extraction(raw_text, parsed_actors)

        # ── 阶段2: 对称性分析 ────────────────────────────────────────
        symmetry_result = self._run_symmetry(actor_result)

        # ── 阶段3: 翻译四阶段 ─────────────────────────────────────────
        translation_result = self._run_translation(actor_result)

        # ── 阶段4: 争议记录 ──────────────────────────────────────────
        controversy_result = self._run_controversy(raw_text, actor_result)

        # ── 阶段5: 饱和度评估 ────────────────────────────────────────
        saturation_result = self._run_saturation(actor_result, translation_result)

        analysis_results = {
            "actors": actor_result,
            "symmetry": symmetry_result,
            "translation_stages": translation_result,
            "controversies": controversy_result,
            "saturation": saturation_result,
        }

        result = {
            "status": "success",
            "skill": "actor-network-analysis-expert",
            "timestamp": datetime.now().isoformat(),
            "mode": "llm_coordinated",
            "message": (
                "⚠️ 定性分析决策（行动者分类、翻译阶段判断、争议识别）"
                "由 LLM 基于 ANT 理论原则完成。本工具管理数据结构和工作流。"
            ),
            "workflow": self._workflow_status(stage),
            "analysis_results": analysis_results,
            "data": data,
        }

        self._save_session(result)
        return result

    def _run_actor_extraction(self, text: str, parsed_actors: List = None) -> Dict:
        parsed_actors = parsed_actors or []

        if parsed_actors:
            # Markdown parser already extracted actors — use them
            extractor = ActorExtractor()
            for a in parsed_actors:
                extractor.extracted_actors.add(a.get("name", ""))
                if a.get("role"):
                    extractor.actor_types[a.get("name", "")] = "unknown"

            return {
                "status": "completed",
                "phase": "actor_extraction",
                "actors_found": parsed_actors,
                "actor_count": len(parsed_actors),
                "categories": {
                    "human": [],
                    "organization": [],
                    "technology": [],
                    "artifact": [],
                    "concept": [],
                    "unclassified": [],
                },
                "human_count": None,
                "nonhuman_count": None,
                "symmetry_warning": None,
                "relationships_found": [],
                "message": "行动者由 parse_markdown_case 提取，分类需 LLM 完成",
            }

        if not text:
            return {
                "status": "needs_llm",
                "phase": "actor_extraction",
                "actors_found": [],
                "actor_count": 0,
                "message": "无文本数据，请 LLM 根据研究背景提取行动者",
            }

        extractor = ActorExtractor()
        result = extractor.extract_from_text(text, source_type="document")
        result["status"] = "completed"
        result["phase"] = "actor_extraction"
        return result

    def _run_symmetry(self, actor_result: Dict) -> Dict:
        actors = actor_result.get("actors_found", [])
        actor_names = [a.get("name") or a.get("actor_name", "") for a in actors]
        actor_names = [n for n in actor_names if n]

        if not actor_names:
            return {
                "status": "needs_llm",
                "phase": "symmetry_check",
                "message": "无行动者数据，请 LLM 填充后重新检查对称性",
            }

        # check_symmetry calls classify_actor which returns None (keyword matching disabled).
        # Build symmetry result directly without calling the buggy helper.
        categories = actor_result.get("categories", {})
        # Count typed actors if LLM filled categories
        typed = sum(len(v) for v in categories.values() if isinstance(v, list))
        if typed > 0:
            result = check_symmetry(actor_names, categories)
        else:
            result = {
                "human_count": 0,
                "nonhuman_count": 0,
                "human_ratio": None,
                "nonhuman_ratio": None,
                "symmetry_warning": "分类待 LLM 完成，无法评估对称性",
                "symmetry_status": "pending",
                "total_actors": len(actor_names),
            }
        result["status"] = "completed"
        result["phase"] = "symmetry_check"
        return result

    def _run_translation(self, actor_result: Dict) -> Dict:
        controller = TranslationStageController()

        actors = actor_result.get("actors_found", [])
        actor_names = [a.get("name") or a.get("actor_name", "") for a in actors]
        actor_names = [n for n in actor_names if n]

        # 初始化所有阶段（LLM 填充内容）
        if actor_names:
            controller.stages["problematization"]["actors"] = actor_names[:1] if actor_names else []
            controller.stages["attribution"]["actors"] = actor_names
            controller.stages["enrollment"]["actors"] = actor_names
            controller.stages["mobilization"]["actors"] = actor_names

        export = controller.export_state()
        return {
            "status": "completed",
            "phase": "translation",
            "stages": export["stages"],
            "all_stages": controller.get_all_stages(),
            "theory_memo": controller.theory_memo,
            "message": "翻译阶段结构已初始化，内容需 LLM 根据 ANT 理论填充",
        }

    def _run_controversy(self, text: str, actor_result: Dict) -> Dict:
        recorder = ControversyRecorder()

        actors = actor_result.get("actors_found", [])
        actor_names = [a.get("name") or a.get("actor_name", "") for a in actors]
        actor_names = [n for n in actor_names if n]

        if not text:
            return {
                "status": "needs_llm",
                "phase": "controversy",
                "controversies": [],
                "message": "无文本数据，请 LLM 根据行动者互动识别争议",
            }

        # 调用文本检测（返回空结构，LLM 填充）
        detected = recorder.detect_controversies_from_text(
            text, source_actors=actor_names if actor_names else None
        )

        return {
            "status": "completed",
            "phase": "controversy",
            "controversies": recorder.controversies,
            "unresolved": recorder.unresolved,
            "resolved": recorder.resolved,
            "total": len(recorder.controversies),
            "theory_memo": CONTROVERSY_METHODOLOGY_MEMO.strip(),
        }

    def _run_saturation(
        self, actor_result: Dict, translation_result: Dict
    ) -> Dict:
        actors = actor_result.get("actors_found", [])
        actor_names = [a.get("name") or a.get("actor_name", "") for a in actors]

        existing_stages = translation_result.get("stages", {})

        actor_data = {
            "actors": set(actor_names),
            "relationships": actor_result.get("relationships_found", []),
            "translation_stages": existing_stages,
            "complete_stages": set(),
        }

        # Bypass the buggy assess_network_saturation when no actors yet.
        # Pass non-empty new_data to avoid the KeyError path.
        if not actor_names:
            return {
                "phase": "saturation",
                "overall_score": 0,
                "overall_status": "needs_data",
                "message": "无行动者数据，请 LLM 提取行动者后重新评估",
            }

        result = saturation.assess_network_saturation(actor_data, new_data=actor_data)
        result["phase"] = "saturation"
        return result

    def _workflow_status(self, current_stage: str) -> Dict[str, Any]:
        current_idx = (
            self.WORKFLOW_STAGES.index(current_stage)
            if current_stage in self.WORKFLOW_STAGES
            else len(self.WORKFLOW_STAGES)
        )
        return {
            "all_stages": self.WORKFLOW_STAGES,
            "current_stage": current_stage,
            "completed_stages": self.WORKFLOW_STAGES[:current_idx],
            "remaining_stages": self.WORKFLOW_STAGES[current_idx + 1:],
            "progress_pct": int((current_idx + 1) / len(self.WORKFLOW_STAGES) * 100),
        }

    def _save_session(self, result: Dict):
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    def load_session(self) -> Optional[Dict]:
        if os.path.exists(self.session_file):
            with open(self.session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def get_prompt_guide(self, stage: str) -> str:
        guides = {
            "actor_extraction": (
                "ANT 行动者提取方法论指导（Latour 1992, Callon 1986）:\n"
                "1. 行动者定义：任何通过行动产生差异的都是行动者\n"
                "2. 不预设人类/非人二分法，关注行动者角色而非名称标签\n"
                "3. 五类行动者：人类、组织、技术、制品、概念\n"
                "4. 对称性原则：非人行动者应占 ≥30%（否则需反思技术能动性）\n"
                "5. LLM 需填充 actors_found 列表和 categories 分类结果"
            ),
            "symmetry_check": (
                "ANT 对称性分析指导:\n"
                "1. 非人行动者占比 <30% → 警告（可能遗漏技术能动性）\n"
                "2. 关注形式对称 vs 实质对称\n"
                "3. 技术、文本、制度应被赋予与人类同等的行动者资格\n"
                "4. LLM 需判断对称性是真实的还是表面化的"
            ),
            "translation": (
                "ANT 翻译四阶段方法论指导（Callon 1986）:\n"
                "1. 问题化：谁是关键行动者？谁设置 OPP（必经点）？\n"
                "2. 利益赋予：各行动者利益如何被重新定义？\n"
                "3. 招募：通过什么策略招募其他行动者？\n"
                "4. 动员：被招募者是否真正代表网络行动？\n"
                "5. 四阶段是分析框架，可能循环/倒退，LLM 需识别关键转译节点"
            ),
            "controversy": (
                "ANT 争议识别方法论指导:\n"
                "1. 争议必须被记录，无论是否已解决\n"
                "2. 争议类型：technical/ethical/economic/political/social/organizational\n"
                "3. 分析争议如何影响网络稳定性\n"
                "4. 关注转译失败点和阻力\n"
                "5. 证据必须来自具体行动者互动描述，不是关键词"
            ),
            "saturation": (
                "ANT 网络饱和度评估指导:\n"
                "1. 行动者饱和：新行动者出现率 <10%\n"
                "2. 关系饱和：新关系出现率 <7%\n"
                "3. 翻译阶段饱和：四阶段均有实质性内容\n"
                "4. 综合评分 ≥85 = 饱和，可进行最终分析\n"
                "5. 饱和度评估决定是否需要更多数据源"
            ),
        }
        return guides.get(
            stage,
            "请参考 SKILL.md 中的 ANT 方法论指导，由 LLM 做定性判断。",
        )


# ─── Markdown case parser ──────────────────────────────────────────────────────

def parse_markdown_case(text: str) -> Dict[str, Any]:
    """解析 ANT markdown 案例文本，提取行动者和关系信息。

    格式：
        ## Phase 1: Actor Identification
        - 李明（工程师）
        - 华为公司
        ## Translation Process
        ### Problematization
        ...
    """
    if not text or not text.strip():
        return {"text": "", "actors": [], "metadata": {}}

    actors = []

    # 提取 bullet list 行动者（- 开头的行）
    actor_pattern = re.compile(r"^[-*]\s+(.+?)(?:\s*[\(|（](.+?)[\)|）])?\s*$", re.MULTILINE)
    for m in actor_pattern.finditer(text):
        name = m.group(1).strip()
        role = m.group(2).strip() if m.group(2) else ""
        actors.append({"name": name, "role": role})

    # 提取标题作为元数据
    headings = []
    heading_pattern = re.compile(r"^#{1,4}\s+(.+)$", re.MULTILINE)
    for m in heading_pattern.finditer(text):
        headings.append(m.group(1).strip())

    return {
        "text": text,
        "actors": actors,
        "metadata": {
            "headings": headings,
            "actor_count": len(actors),
            "section_count": len(headings),
        },
    }


# ─── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="actor-network-analysis-expert 分析协调器"
    )
    parser.add_argument(
        "--stage",
        default="actor_extraction",
        choices=SkillAnalyzer.WORKFLOW_STAGES,
        help="当前分析阶段",
    )
    parser.add_argument(
        "--data",
        default="{}",
        help="输入数据(JSON)，包含 text/input_text 字段",
    )
    parser.add_argument(
        "--case",
        default=None,
        help="ANT 案例 markdown 文本（优先级高于 --data）",
    )
    parser.add_argument(
        "--dir",
        default="./session",
        help="工作目录",
    )
    args = parser.parse_args()

    analyzer = SkillAnalyzer(working_dir=args.dir)

    if args.case:
        parsed = parse_markdown_case(args.case)
    else:
        try:
            parsed = json.loads(args.data)
        except json.JSONDecodeError:
            parsed = {}

    result = analyzer.analyze(parsed, stage=args.stage)
    print(json.dumps(result, ensure_ascii=False, indent=2))
