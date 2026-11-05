#!/usr/bin/env python3
"""
qca-analysis-expert - 主分析协调器
协调 QCA 分析流程：校准 → 必要性分析 → 真值表 → 解公式

核心原则：定性分析决策由 LLM 完成，本工具管理数据结构和工作流。
"""

import os
import json
import csv
import io
from datetime import datetime
from typing import Dict, Any, List, Optional

from data_calibrator import DataCalibrator
from truth_table_builder import TruthTableBuilder
from solution_calculator import SolutionCalculator


class SkillAnalyzer:
    """QCA 分析协调器"""

    WORKFLOW_STAGES = [
        "calibration",
        "necessity",
        "sufficiency",
        "truth_table",
        "solution",
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
        stage: str = "solution",
        **kwargs,
    ) -> Dict[str, Any]:
        current_idx = self.WORKFLOW_STAGES.index(stage) if stage in self.WORKFLOW_STAGES else -1

        # ── 阶段1: 校准 ────────────────────────────────────────────────
        calibration_result = self._run_calibration(data)

        # ── 阶段2: 必要性分析 ─────────────────────────────────────────
        necessity_result = self._run_necessity(calibration_result)

        # ── 阶段3: 充分性分析 ─────────────────────────────────────────
        sufficiency_result = self._run_sufficiency(calibration_result)

        # ── 阶段4: 真值表 ────────────────────────────────────────────
        truth_table_result = self._run_truth_table(calibration_result)

        # ── 阶段5: 解公式 ────────────────────────────────────────────
        solution_result = self._run_solution(truth_table_result)

        analysis_results = {
            "calibration": calibration_result,
            "necessity_analysis": necessity_result,
            "sufficiency_analysis": sufficiency_result,
            "truth_table": truth_table_result,
            "solutions": solution_result,
        }

        result = {
            "status": "success",
            "skill": "qca-analysis-expert",
            "timestamp": datetime.now().isoformat(),
            "mode": "llm_coordinated",
            "message": (
                "⚠️ 定性分析决策（锚点选择、必要/充分性判断、解类型选择）"
                "由 LLM 基于理论原则完成。本工具管理数据结构和工作流。"
            ),
            "workflow": self._workflow_status(stage),
            "analysis_results": analysis_results,
            "data": data,
        }

        self._save_session(result)
        return result

    def _run_calibration(self, data: Dict[str, Any]) -> Dict:
        cases = data.get("cases", [])
        if not cases:
            return {
                "status": "completed",
                "phase": "calibration",
                "cases": [],
                "message": "无案例数据，无法进行校准",
            }

        calibrator = DataCalibrator()
        calibrated = calibrator.calibrate(cases)

        conditions = data.get("conditions", [])
        outcome = data.get("outcome", "")
        if not conditions and cases:
            keys = list(cases[0].keys()) if isinstance(cases[0], dict) else []
            outcome = keys[-1] if keys else ""
            conditions = keys[:-1] if len(keys) > 1 else []

        return {
            "status": "completed",
            "phase": "calibration",
            "cases": calibrated.get("calibrated_data", cases),
            "num_cases": calibrated.get("num_cases", len(cases)),
            "conditions": conditions,
            "outcome": outcome,
            "calibration_method": "direct",
        }

    def _run_necessity(self, calibration: Dict) -> Dict:
        cases = calibration.get("cases", [])
        outcome = calibration.get("outcome", "")
        if not cases or not outcome:
            return {"status": "no_data", "phase": "necessity", "conditions": []}

        conditions = calibration.get("conditions", [])
        if not conditions and cases:
            keys = [k for k in cases[0].keys()] if isinstance(cases[0], dict) else []
            outcome = keys[-1] if keys else ""
            conditions = keys[:-1] if len(keys) > 1 else []

        necessity_results = []
        for cond in conditions:
            consistency = self._calc_necessity_consistency(cases, cond, outcome)
            coverage = self._calc_necessity_coverage(cases, cond, outcome)
            necessity_results.append({
                "condition": cond,
                "consistency": consistency,
                "coverage": coverage,
                "is_necessary": consistency >= 0.9,
                "note": "由 LLM 根据 consistency >= 0.9 判断是否为必要条件",
            })

        return {
            "status": "completed",
            "phase": "necessity",
            "conditions": necessity_results,
        }

    def _run_sufficiency(self, calibration: Dict) -> Dict:
        cases = calibration.get("cases", [])
        outcome = calibration.get("outcome", "")
        if not cases or not outcome:
            return {"status": "no_data", "phase": "sufficiency", "paths": []}

        conditions = calibration.get("conditions", [])
        if not conditions and cases:
            keys = [k for k in cases[0].keys()] if isinstance(cases[0], dict) else []
            outcome = keys[-1] if keys else ""
            conditions = keys[:-1] if len(keys) > 1 else []

        sufficiency_results = []
        for cond in conditions:
            consistency = self._calc_sufficiency_consistency(cases, cond, outcome)
            coverage = self._calc_sufficiency_coverage(cases, cond, outcome)
            sufficiency_results.append({
                "condition": cond,
                "consistency": consistency,
                "coverage": coverage,
                "is_sufficient": consistency >= 0.8,
                "note": "由 LLM 根据 consistency >= 0.8 判断是否为充分条件",
            })

        return {
            "status": "completed",
            "phase": "sufficiency",
            "paths": sufficiency_results,
        }

    def _run_truth_table(self, calibration: Dict) -> Dict:
        cases = calibration.get("cases", [])
        conditions = calibration.get("conditions", [])
        outcome = calibration.get("outcome", "")

        if not cases or not conditions or not outcome:
            return {"status": "no_data", "phase": "truth_table", "configurations": []}

        builder = TruthTableBuilder()
        result = builder.build(cases, conditions, outcome)
        return {
            "status": "completed",
            "phase": "truth_table",
            "truth_table": result.get("truth_table", []),
            "num_configurations": result.get("num_configurations", 0),
            "conditions": conditions,
            "outcome": outcome,
        }

    def _run_solution(self, truth_table: Dict) -> Dict:
        table = truth_table.get("truth_table", [])
        if not table:
            return {
                "status": "no_data",
                "phase": "solution",
                "complex": {"summary": "无真值表数据"},
                "intermediate": {"summary": "无真值表数据"},
                "parsimonious": {"summary": "无真值表数据"},
            }

        calculator = SolutionCalculator()
        result = calculator.calculate(table, solution_type="all")
        return {
            "status": "completed",
            "phase": "solution",
            "complex": result.get("complex", {}),
            "intermediate": result.get("intermediate", {}),
            "parsimonious": result.get("parsimonious", {}),
            "note": "解类型选择由 LLM 根据研究问题决定（通常报告中间解）",
        }

    def _calc_necessity_consistency(
        self, cases: List[Dict], cond: str, outcome: str
    ) -> float:
        """OUTCOME ⊆ CONDITION"""
        if not cases:
            return 0.0
        numerator = sum(min(c.get(cond, 0), c.get(outcome, 0)) for c in cases)
        denominator = sum(c.get(outcome, 0) for c in cases)
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 4)

    def _calc_necessity_coverage(
        self, cases: List[Dict], cond: str, outcome: str
    ) -> float:
        """OUTCOME ∩ CONDITION / CONDITION"""
        if not cases:
            return 0.0
        numerator = sum(min(c.get(cond, 0), c.get(outcome, 0)) for c in cases)
        denominator = sum(c.get(cond, 0) for c in cases)
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 4)

    def _calc_sufficiency_consistency(
        self, cases: List[Dict], cond: str, outcome: str
    ) -> float:
        """CONDITION ⊆ OUTCOME"""
        if not cases:
            return 0.0
        numerator = sum(min(c.get(cond, 0), c.get(outcome, 0)) for c in cases)
        denominator = sum(c.get(cond, 0) for c in cases)
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 4)

    def _calc_sufficiency_coverage(
        self, cases: List[Dict], cond: str, outcome: str
    ) -> float:
        """CONDITION ∩ OUTCOME / OUTCOME"""
        if not cases:
            return 0.0
        numerator = sum(min(c.get(cond, 0), c.get(outcome, 0)) for c in cases)
        denominator = sum(c.get(outcome, 0) for c in cases)
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 4)

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
            "calibration": (
                "QCA 校准方法论指导（Ragin 2008 模糊集）:\n"
                "1. 直接校准法：三个锚点（完全隶属=1.0，交叉点=0.5，完全不隶属=0.0）\n"
                "2. 校准决策必须由 LLM 结合研究背景做出\n"
                "3. 0-1 数据直接通过；字符串需 LLM 做语义映射"
            ),
            "necessity": (
                "QCA 必要性分析指导:\n"
                "1. 一致性(consistency) >= 0.9 通常视为必要条件\n"
                "2. 覆盖度(coverage) 衡量必要条件的普遍性\n"
                "3. 多个必要条件为 AND 关系\n"
                "4. LLM 需结合研究问题判断一致性阈值"
            ),
            "sufficiency": (
                "QCA 充分性分析指导:\n"
                "1. 一致性(consistency) >= 0.8 通常视为充分条件\n"
                "2. PRI > 0.5 可区分一致性和矛盾组\n"
                "3. 多个充分条件为 OR 关系\n"
                "4. LLM 需判断条件组合路径"
            ),
            "truth_table": (
                "QCA 真值表构建指导:\n"
                "1. 每行 = 一种条件组合，n = 该组合案例数\n"
                "2. 一致性 > 阈值（如 0.75）= 该组合为充分解\n"
                "3. LLM 需决定阈值并解释不符合的案例"
            ),
            "solution": (
                "QCA 解公式选择指导:\n"
                "1. 复杂解：最保守，使用所有观察到的逻辑余项\n"
                "2. 中间解（最常用）：使用符合理论预期的部分逻辑余项\n"
                "3. 简约解：最简洁，可能过度简化\n"
                "4. 通常报告中间解，说明使用的逻辑余项假设"
            ),
        }
        return guides.get(
            stage,
            "请参考 SKILL.md 中的 QCA 方法论指导，由 LLM 做定性判断。",
        )


# ─── CSV case parser ──────────────────────────────────────────────────────────

def parse_csv_case(text: str) -> Dict[str, Any]:
    """解析 CSV 格式的 QCA 案例数据。

    格式：
        case,COND1,COND2,COND3,OUTCOME
        Taiwan,0.92,0.55,0.88,0.95
    第一列=案例名，最后一列=结果，中间=条件变量。
    """
    if not text or not text.strip():
        return {"cases": [], "conditions": [], "outcome": ""}

    reader = csv.DictReader(io.StringIO(text.strip()))
    rows = list(reader)

    if not rows:
        return {"cases": [], "conditions": [], "outcome": ""}

    fields = list(rows[0].keys())
    case_field = fields[0]
    outcome_field = fields[-1]
    condition_fields = fields[1:-1]

    cases = []
    for row in rows:
        case_entry = {case_field: row[case_field]}
        for cond in condition_fields:
            try:
                case_entry[cond] = float(row[cond])
            except (ValueError, KeyError):
                case_entry[cond] = row.get(cond, "")
        try:
            case_entry[outcome_field] = float(row[outcome_field])
        except (ValueError, KeyError):
            case_entry[outcome_field] = row.get(outcome_field, "")

        cases.append(case_entry)

    return {
        "cases": cases,
        "conditions": condition_fields,
        "outcome": outcome_field,
    }


# ─── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="qca-analysis-expert 分析协调器"
    )
    parser.add_argument(
        "--stage",
        default="solution",
        choices=SkillAnalyzer.WORKFLOW_STAGES,
        help="当前分析阶段",
    )
    parser.add_argument(
        "--data",
        default="{}",
        help="输入数据(JSON)，包含 cases/conditions/outcome",
    )
    parser.add_argument(
        "--case",
        default=None,
        help="CSV 格式案例数据（优先级高于 --data）",
    )
    parser.add_argument(
        "--dir",
        default="./session",
        help="工作目录",
    )
    args = parser.parse_args()

    analyzer = SkillAnalyzer(working_dir=args.dir)

    if args.case:
        parsed = parse_csv_case(args.case)
    else:
        try:
            parsed = json.loads(args.data)
        except json.JSONDecodeError:
            parsed = {}

    result = analyzer.analyze(parsed, stage=args.stage)
    print(json.dumps(result, ensure_ascii=False, indent=2))
