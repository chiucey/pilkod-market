#!/usr/bin/env python3
"""
SKILL进化追踪器
追踪复合Skill的执行效果，触发进化机制
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class EvolutionTracker:
    """SKILL进化追踪器"""

    # 进化触发阈值
    QUALITY_THRESHOLD = 0.85
    EFFICIENCY_THRESHOLD = 1.5
    SATISFACTION_THRESHOLD = 4.0
    PATTERN_THRESHOLD = 3

    def __init__(self, evolution_dir: str = "/workspace/temp-skills/skill-evolution-system/evolution"):
        self.evolution_dir = Path(evolution_dir)
        self.evolution_dir.mkdir(parents=True, exist_ok=True)
        self.evolution_records = {}

    def record_execution(self, skill_name: str, execution_data: Dict) -> bool:
        """
        记录一次执行
        返回是否触发了进化
        """
        if skill_name not in self.evolution_records:
            self.evolution_records[skill_name] = {
                "executions": [],
                "evolution_count": 0,
                "current_version": "1.0.0",
                "quality_scores": [],
                "efficiency_scores": [],
                "satisfaction_scores": []
            }

        record = self.evolution_records[skill_name]

        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "duration": execution_data.get("duration", 0),
            "success": execution_data.get("success", True),
            "quality_score": execution_data.get("quality_score", 0),
            "efficiency_score": execution_data.get("efficiency_score", 0),
            "satisfaction_score": execution_data.get("satisfaction_score", 0),
            "feedback": execution_data.get("feedback", ""),
            "corrections": execution_data.get("corrections", 0)
        }

        record["executions"].append(execution_record)
        record["quality_scores"].append(execution_record["quality_score"])
        record["efficiency_scores"].append(execution_record["efficiency_score"])
        record["satisfaction_scores"].append(execution_record["satisfaction_score"])

        # 检查是否需要进化
        should_evolve = self._check_evolution_needed(skill_name)

        if should_evolve:
            self._trigger_evolution(skill_name)

        self._save_record(skill_name)

        return should_evolve

    def _check_evolution_needed(self, skill_name: str) -> bool:
        """检查是否需要进化"""
        record = self.evolution_records[skill_name]
        recent = record["executions"][-5:] if len(record["executions"]) >= 5 else record["executions"]

        if not recent:
            return False

        # 质量驱动
        avg_quality = sum(e["quality_score"] for e in recent) / len(recent)
        if avg_quality < self.QUALITY_THRESHOLD:
            record["trigger_reason"] = "quality"
            return True

        # 效率驱动
        avg_duration = sum(e["duration"] for e in recent) / len(recent)
        expected_duration = record.get("expected_duration", avg_duration * 2)
        if avg_duration > expected_duration * self.EFFICIENCY_THRESHOLD:
            record["trigger_reason"] = "efficiency"
            return True

        # 满意度驱动
        avg_satisfaction = sum(e["satisfaction_score"] for e in recent) / len(recent)
        if avg_satisfaction < self.SATISFACTION_THRESHOLD:
            record["trigger_reason"] = "satisfaction"
            return True

        # 模式驱动 - 连续相似任务
        similar_count = self._count_similar_patterns(record["executions"])
        if similar_count >= self.PATTERN_THRESHOLD:
            record["trigger_reason"] = "pattern"
            return True

        return False

    def _count_similar_patterns(self, executions: List[Dict]) -> int:
        """计算连续相似任务数"""
        if len(executions) < self.PATTERN_THRESHOLD:
            return 0

        # 简化的相似性检查
        recent = executions[-self.PATTERN_THRESHOLD:]
        similar_count = 1

        for i in range(1, len(recent)):
            # 如果质量分数接近，认为是相似任务
            if abs(recent[i]["quality_score"] - recent[i-1]["quality_score"]) < 0.1:
                similar_count += 1
            else:
                similar_count = 1

        return similar_count

    def _trigger_evolution(self, skill_name: str):
        """触发进化"""
        record = self.evolution_records[skill_name]
        record["evolution_count"] += 1

        # 生成进化建议
        evolution_suggestion = self._generate_evolution_suggestion(skill_name)

        # 保存进化记录
        evolution_record = {
            "timestamp": datetime.now().isoformat(),
            "version": record["current_version"],
            "new_version": self._bump_version(record["current_version"]),
            "trigger_reason": record.get("trigger_reason", "unknown"),
            "suggestion": evolution_suggestion,
            "execution_stats": self._get_stats(record)
        }

        self._save_evolution_record(skill_name, evolution_record)

        # 更新版本
        record["current_version"] = evolution_record["new_version"]

        print(f"🔄 {skill_name} 已触发进化: {evolution_record['trigger_reason']}")
        print(f"   {record['current_version']} → {evolution_record['new_version']}")
        print(f"   建议: {evolution_suggestion}")

    def _generate_evolution_suggestion(self, skill_name: str) -> str:
        """生成进化建议"""
        record = self.evolution_records[skill_name]
        reason = record.get("trigger_reason", "unknown")

        suggestions = {
            "quality": "建议增加验证步骤或引入额外的审查层",
            "efficiency": "建议优化流程路径或引入缓存机制",
            "satisfaction": "建议改进输出格式或增加用户自定义选项",
            "pattern": "建议提取通用模式并固化为新的子Skill"
        }

        return suggestions.get(reason, "建议进行常规优化")

    def _bump_version(self, current: str) -> str:
        """版本号递增"""
        parts = current.split(".")
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
        else:
            parts.append("1")
        return ".".join(parts)

    def _get_stats(self, record: Dict) -> Dict:
        """获取统计数据"""
        recent = record["executions"][-10:] if len(record["executions"]) >= 10 else record["executions"]

        return {
            "total_executions": len(record["executions"]),
            "avg_quality": sum(e["quality_score"] for e in recent) / len(recent) if recent else 0,
            "avg_duration": sum(e["duration"] for e in recent) / len(recent) if recent else 0,
            "success_rate": sum(1 for e in recent if e["success"]) / len(recent) if recent else 0
        }

    def _save_record(self, skill_name: str):
        """保存执行记录"""
        filepath = self.evolution_dir / f"{skill_name}_record.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.evolution_records[skill_name], f, ensure_ascii=False, indent=2)

    def _save_evolution_record(self, skill_name: str, record: Dict):
        """保存进化记录"""
        evol_file = self.evolution_dir / f"{skill_name}_evolutions.json"

        evolutions = []
        if evol_file.exists():
            with open(evol_file, 'r', encoding='utf-8') as f:
                evolutions = json.load(f)

        evolutions.append(record)

        with open(evol_file, 'w', encoding='utf-8') as f:
            json.dump(evolutions, f, ensure_ascii=False, indent=2)

    def get_evolution_status(self, skill_name: str) -> Optional[Dict]:
        """获取进化状态"""
        filepath = self.evolution_dir / f"{skill_name}_record.json"

        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_evolution_report(self) -> Dict:
        """生成进化报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_skills_tracked": len(self.evolution_records),
            "skills": []
        }

        for skill_name, record in self.evolution_records.items():
            report["skills"].append({
                "name": skill_name,
                "current_version": record["current_version"],
                "evolution_count": record["evolution_count"],
                "total_executions": len(record["executions"]),
                "avg_quality": sum(record["quality_scores"]) / len(record["quality_scores"]) if record["quality_scores"] else 0,
                "avg_satisfaction": sum(record["satisfaction_scores"]) / len(record["satisfaction_scores"]) if record["satisfaction_scores"] else 0
            })

        return report


def main():
    """主函数 - 测试进化追踪"""
    print("📊 SKILL进化追踪器")
    print("=" * 50)

    tracker = EvolutionTracker()

    # 模拟执行记录
    test_executions = [
        {
            "duration": 30,
            "success": True,
            "quality_score": 0.75,
            "efficiency_score": 0.8,
            "satisfaction_score": 3.5,
            "corrections": 2
        },
        {
            "duration": 35,
            "success": True,
            "quality_score": 0.72,
            "efficiency_score": 0.78,
            "satisfaction_score": 3.6,
            "corrections": 2
        },
        {
            "duration": 32,
            "success": True,
            "quality_score": 0.73,
            "efficiency_score": 0.79,
            "satisfaction_score": 3.4,
            "corrections": 2
        }
    ]

    skill_name = "auto-intelligence"

    print(f"\n🔍 追踪 Skill: {skill_name}")

    for i, exec_data in enumerate(test_executions, 1):
        print(f"\n--- 执行 #{i} ---")
        triggered = tracker.record_execution(skill_name, exec_data)
        if triggered:
            print(f"✅ 触发了进化!")

    # 获取状态
    status = tracker.get_evolution_status(skill_name)
    if status:
        print(f"\n📊 当前状态:")
        print(f"   版本: {status['current_version']}")
        print(f"   进化次数: {status['evolution_count']}")
        print(f"   总执行: {len(status['executions'])}")

    # 生成报告
    report = tracker.generate_evolution_report()
    print(f"\n📋 进化报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return report


if __name__ == "__main__":
    main()
