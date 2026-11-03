#!/usr/bin/env python3
"""
置信度追踪器 - 简历优化技能核心模块

用于追踪和管理用户在简历优化访谈过程中的置信度状态。
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DimensionConfidence:
    """单个维度的置信度状态"""
    name: str
    current: float
    target: float
    weight: float
    status: str  # "pending", "in_progress", "met", "exceeded"
    last_updated: str
    evidence: List[str]  # 支撑置信度的事实依据


class ConfidenceTracker:
    """置信度追踪器"""

    # 维度配置
    DIMENSIONS = {
        "job_target": {
            "name": "求职目标",
            "weight": 0.30,
            "target": 0.95,
            "questions": [
                "目标岗位是什么？",
                "期望薪资范围？",
                "工作地点偏好？",
                "行业选择倾向？",
                "职级定位？",
                "时间规划？"
            ]
        },
        "industry_positioning": {
            "name": "行业定位",
            "weight": 0.20,
            "target": 0.95,
            "questions": [
                "最希望深耕哪个行业？",
                "在该行业的经验？",
                "转型原因？",
                "人脉资源？"
            ]
        },
        "core_competencies": {
            "name": "核心竞争力",
            "weight": 0.20,
            "target": 0.90,
            "questions": [
                "3个核心竞争力关键词？",
                "专业技能体现？",
                "可迁移能力？",
                "差异化优势？",
                "稀缺性技能？"
            ]
        },
        "work_highlights": {
            "name": "工作经历亮点",
            "weight": 0.20,
            "target": 0.90,
            "questions": [
                "STAR法则挖掘",
                "量化数据收集",
                "成就提炼"
            ]
        },
        "skill_match": {
            "name": "技能匹配度",
            "weight": 0.10,
            "target": 0.90,
            "questions": [
                "技能熟练度评估",
                "工具清单收集",
                "证书资质",
                "学习计划"
            ]
        }
    }

    def __init__(self):
        self.dimensions: Dict[str, DimensionConfidence] = {}
        self.session_start = datetime.now().isoformat()
        self._init_dimensions()

    def _init_dimensions(self):
        """初始化所有维度"""
        for dim_id, config in self.DIMENSIONS.items():
            self.dimensions[dim_id] = DimensionConfidence(
                name=config["name"],
                current=0.0,
                target=config["target"],
                weight=config["weight"],
                status="pending",
                last_updated=self.session_start,
                evidence=[]
            )

    def update_dimension(
        self,
        dimension_id: str,
        new_confidence: float,
        evidence: str,
        source: str = "user_input"
    ) -> bool:
        """
        更新单个维度的置信度

        Args:
            dimension_id: 维度ID
            new_confidence: 新的置信度值 (0-100，百分比格式)
            evidence: 支撑这一置信度的事实依据
            source: 置信度来源

        Returns:
            更新是否成功
        """
        if dimension_id not in self.dimensions:
            return False

        dim = self.dimensions[dimension_id]
        # 将百分比转换为小数格式存储（0-1）
        dim.current = max(0, min(100, new_confidence)) / 100.0
        dim.last_updated = datetime.now().isoformat()
        dim.evidence.append(f"[{source}] {evidence}")

        # 更新状态 (target已经是小数格式0-1)
        if dim.current >= dim.target:
            dim.status = "met" if dim.current < dim.target + 0.05 else "exceeded"
        elif dim.current > 0:
            dim.status = "in_progress"

        return True

    def calculate_overall_confidence(self) -> float:
        """
        计算综合置信度

        综合置信度 = Σ(维度置信度 × 维度权重) / Σ维度权重
        """
        total_weight = 0
        weighted_sum = 0

        for dim in self.dimensions.values():
            weighted_sum += dim.current * dim.weight
            total_weight += dim.weight

        if total_weight == 0:
            return 0

        return round(weighted_sum / total_weight, 1)

    def get_status(self) -> Dict:
        """
        获取当前置信度状态

        Returns:
            包含各维度状态和综合置信度的字典
        """
        overall = self.calculate_overall_confidence()

        # 判断是否达标
        if overall >= 95:
            status = "ready"  # 可以生成方案
        elif overall >= 85:
            status = "almost"  # 接近达标，需要补充
        else:
            status = "insufficient"  # 置信度不足

        # 找出需要补充的维度
        gaps = []
        for dim_id, dim in self.dimensions.items():
            if dim.current < dim.target:
                gaps.append({
                    "dimension_id": dim_id,
                    "name": dim.name,
                    "current": dim.current,
                    "target": dim.target,
                    "gap": dim.target - dim.current,
                    "suggested_questions": self.DIMENSIONS[dim_id]["questions"]
                })

        # 按gap大小排序
        gaps.sort(key=lambda x: x["gap"], reverse=True)

        return {
            "overall_confidence": overall,
            "status": status,
            "dimensions": {
                dim_id: {
                    "name": dim.name,
                    "current": dim.current,
                    "target": dim.target,
                    "weight": dim.weight,
                    "status": dim.status,
                    "progress": f"{dim.current}/{dim.target}"
                }
                for dim_id, dim in self.dimensions.items()
            },
            "gaps": gaps,
            "can_generate_plan": overall >= 95
        }

    def generate_progress_visualization(self) -> str:
        """
        生成置信度进度可视化字符串
        """
        status = self.get_status()

        lines = [
            "【置信度评估面板】\n",
            f"┌{'─'*17}┬{'─'*11}┬{'─'*11}┐",
            f"│{'维度':^15} │ {'当前':^9} │ {'目标':^9} │",
            f"├{'─'*17}┼{'─'*11}┼{'─'*11}┤"
        ]

        for dim_id, dim in status["dimensions"].items():
            # 生成进度条 (current和target都是小数格式0-1)
            filled = int(dim["current"] * 10)
            empty = 10 - filled
            progress_bar = "▓" * filled + "░" * empty

            # 状态符号
            status_icon = "✅" if dim["status"] in ["met", "exceeded"] else "▓"

            # 显示为百分比格式
            current_pct = dim["current"] * 100
            target_pct = dim["target"] * 100

            lines.append(
                f"│ {dim['name']:^13} │ {current_pct:>6.1f}%  {status_icon} │ {target_pct:>6.1f}%   │"
            )
            lines.append(
                f"│{'':^17} │ {progress_bar} │{'':^11} │"
            )

        # 综合置信度行
        lines.append(f"├{'─'*17}┼{'─'*11}┼{'─'*11}┤")
        overall = status["overall_confidence"] * 100  # 转换为百分比
        filled = int(overall / 10)
        empty = 10 - filled
        progress_bar = "▓" * filled + "░" * empty

        lines.append(
            f"│ {'综合置信度':^13} │ {overall:>6.1f}%   │ {95.0:>6.1f}%   │"
        )
        lines.append(f"│{'':^17} │ {progress_bar} │{'':^11} │")
        lines.append(f"└{'─'*17}┴{'─'*11}┴{'─'*11}┘")

        # 状态说明
        if status["status"] == "ready":
            lines.append("\n✅ 综合置信度已达95%，可以生成简历优化方案！")
        elif status["status"] == "almost":
            lines.append(f"\n⚠️ 综合置信度{overall}%，距离95%目标还差{95-overall}个百分点")
            lines.append("建议：补充以下维度的信息：")
            for gap in status["gaps"][:2]:  # 只显示前两个
                lines.append(f"  - {gap['name']}（当前{gap['current']}%，目标{gap['target']}%）")
        else:
            lines.append(f"\n❌ 综合置信度{overall}%，需要进一步收集信息")

        return "\n".join(lines)

    def export_state(self, filepath: str):
        """导出当前状态到JSON文件"""
        state = self.get_status()
        state["dimensions_detail"] = {
            dim_id: {
                "evidence": dim.evidence,
                "last_updated": dim.last_updated
            }
            for dim_id, dim in self.dimensions.items()
        }
        state["session_start"] = self.session_start

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def import_state(self, filepath: str) -> bool:
        """从JSON文件导入状态"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)

            # 恢复维度状态
            for dim_id, dim_state in state.get("dimensions_detail", {}).items():
                if dim_id in self.dimensions:
                    self.dimensions[dim_id].evidence = dim_state.get("evidence", [])
                    self.dimensions[dim_id].last_updated = dim_state.get("last_updated", "")

            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False


def demo():
    """演示置信度追踪器的使用"""
    tracker = ConfidenceTracker()

    # 模拟用户回答
    tracker.update_dimension(
        "job_target",
        95.0,
        "目标岗位：高级产品经理，期望薪资30-40K，北京，互联网行业"
    )

    tracker.update_dimension(
        "industry_positioning",
        95.0,
        "深耕互联网行业，有5年经验，有一定行业人脉"
    )

    tracker.update_dimension(
        "core_competencies",
        88.0,
        "核心竞争力：用户增长、数据驱动、产品思维"
    )

    tracker.update_dimension(
        "work_highlights",
        85.0,
        "主导过千万级项目，有量化成果"
    )

    tracker.update_dimension(
        "skill_match",
        90.0,
        "技能匹配度达到90%"
    )

    # 打印状态
    print(tracker.generate_progress_visualization())

    # 检查是否可以生成方案
    status = tracker.get_status()
    print(f"\n是否可以生成方案: {status['can_generate_plan']}")

    # 导出状态
    tracker.export_state("/tmp/confidence_state.json")
    print("\n状态已导出到 /tmp/confidence_state.json")


if __name__ == "__main__":
    demo()
