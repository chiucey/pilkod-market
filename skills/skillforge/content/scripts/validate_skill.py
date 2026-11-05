#!/usr/bin/env python3
"""
SkillForge - Skill 质量验证脚本

验证 SKILL.md 的格式、内容和最佳实践。
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any


class SkillValidator:
    """Skill 质量验证器"""

    # 10 维度评分配置
    DIMENSIONS = {
        "format": {"weight": 0.15, "name": "格式规范"},
        "trigger": {"weight": 0.15, "name": "触发质量"},
        "boundary": {"weight": 0.15, "name": "边界定义"},
        "instruction": {"weight": 0.15, "name": "指令质量"},
        "example": {"weight": 0.10, "name": "示例质量"},
        "tool": {"weight": 0.10, "name": "工具定义"},
        "doc": {"weight": 0.05, "name": "文档完善"},
        "error_handling": {"weight": 0.05, "name": "错误处理"},
        "maintainability": {"weight": 0.05, "name": "可维护性"},
        "security": {"weight": 0.05, "name": "安全性"},
    }

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_md_path = self.skill_path / "SKILL.md"
        self.meta_path = self.skill_path / "_meta.json"
        self.issues: List[Dict[str, Any]] = []
        self.scores: Dict[str, int] = {}

    def validate(self) -> Tuple[bool, float, Dict[str, int]]:
        """
        执行完整验证流程。
        返回: (是否通过, 加权评分, 各维度评分)
        """
        # 1. 检查文件存在性
        if not self.skill_md_path.exists():
            self.add_issue("critical", "SKILL.md 文件不存在")
            return False, 0, {}

        # 2. 读取并解析 SKILL.md
        content = self.skill_md_path.read_text(encoding="utf-8")
        frontmatter, body = self.parse_frontmatter(content)

        # 3. 验证 Frontmatter
        self.validate_frontmatter(frontmatter)

        # 4. 验证内容质量
        self.validate_content_quality(body)

        # 5. 验证结构
        self.validate_structure(body)

        # 6. 计算评分
        self.calculate_scores()

        # 7. 返回结果
        weighted_score = sum(
            self.scores.get(dim, 0) * info["weight"]
            for dim, info in self.DIMENSIONS.items()
        )

        passed = weighted_score >= 80 and not self.has_critical_issues()

        return passed, weighted_score, self.scores

    def parse_frontmatter(self, content: str) -> Tuple[Dict[str, str], str]:
        """解析 YAML frontmatter"""
        if not content.startswith("---"):
            self.add_issue("high", "Frontmatter 必须从第一行开始")
            return {}, content

        parts = content.split("---", 2)
        if len(parts) < 3:
            self.add_issue("high", "Frontmatter 格式错误")
            return {}, content

        import yaml
        try:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
            return frontmatter, body
        except yaml.YAMLError as e:
            self.add_issue("critical", f"YAML 解析错误: {e}")
            return {}, content

    def validate_frontmatter(self, frontmatter: Dict[str, str]) -> None:
        """验证 Frontmatter"""
        # 检查必需字段
        if "name" not in frontmatter:
            self.add_issue("critical", "Frontmatter 缺少 'name' 字段")

        if "description" not in frontmatter:
            self.add_issue("critical", "Frontmatter 缺少 'description' 字段")
        else:
            desc = frontmatter["description"]
            # 检查是否包含触发短语
            trigger_phrases = ["use when", "use this", "当用户要求", "触发", "use for"]
            has_trigger = any(phrase.lower() in desc.lower() for phrase in trigger_phrases)
            if not has_trigger:
                self.add_issue("medium", "description 建议包含触发短语 (e.g., 'Use when...')")

    def validate_content_quality(self, body: str) -> None:
        """验证内容质量"""
        lines = body.split("\n")

        # 检查空文档
        if not body.strip():
            self.add_issue("critical", "SKILL.md 内容为空")
            return

        # 检查是否过于简短
        if len(lines) < 20:
            self.add_issue("medium", f"SKILL.md 内容过短 ({len(lines)} 行)，建议至少 50 行")

        # 检查是否过于冗长
        if len(lines) > 500:
            self.add_issue("medium", f"SKILL.md 内容过长 ({len(lines)} 行)，建议精简到 450 行以内")

    def validate_structure(self, body: str) -> None:
        """验证文档结构"""
        # 检查是否包含必要部分
        required_sections = ["#", "##"]
        found_sections = []

        for line in body.split("\n")[:50]:  # 检查前50行
            for section in required_sections:
                if line.strip().startswith(section):
                    found_sections.append(line.strip())

        if not found_sections:
            self.add_issue("low", "建议添加标题结构以提高可读性")

    def calculate_scores(self) -> None:
        """计算各维度评分"""
        # 基于问题自动计算评分
        issue_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in self.issues:
            severity = issue.get("severity", "low")
            issue_counts[severity] += 1

        # 格式规范评分
        format_score = 10
        if issue_counts["critical"] > 0:
            format_score = 2
        elif issue_counts["high"] > 0:
            format_score = 5
        elif issue_counts["medium"] > 0:
            format_score = 7
        self.scores["format"] = format_score

        # 触发质量评分
        trigger_score = 8  # 假设基础良好
        if any("description" in i.get("message", "").lower() for i in self.issues):
            trigger_score = 6
        self.scores["trigger"] = trigger_score

        # 其他维度基于整体健康度
        base_score = 8
        if issue_counts["high"] > 0:
            base_score = 6
        if issue_counts["critical"] > 0:
            base_score = 3

        for dim in ["boundary", "instruction", "example", "tool", "doc",
                    "error_handling", "maintainability", "security"]:
            self.scores[dim] = base_score

    def add_issue(self, severity: str, message: str) -> None:
        """添加问题"""
        self.issues.append({
            "severity": severity,
            "message": message,
            "dimension": self.classify_issue(message)
        })

    def classify_issue(self, message: str) -> str:
        """将问题归类到维度"""
        message_lower = message.lower()
        if "frontmatter" in message_lower or "yaml" in message_lower:
            return "format"
        if "description" in message_lower or "trigger" in message_lower:
            return "trigger"
        if "boundary" in message_lower:
            return "boundary"
        if "instruction" in message_lower or "content" in message_lower:
            return "instruction"
        return "general"

    def has_critical_issues(self) -> bool:
        """检查是否有严重问题"""
        return any(issue.get("severity") == "critical" for issue in self.issues)

    def get_report(self) -> str:
        """生成验证报告"""
        report = ["=" * 60]
        report.append("SkillForge 验证报告")
        report.append("=" * 60)

        report.append(f"\n文件: {self.skill_path}")

        if self.issues:
            report.append("\n发现问题:")
            for i, issue in enumerate(self.issues, 1):
                severity_emoji = {
                    "critical": "[X]",
                    "high": "[!]",
                    "medium": "[~]",
                    "low": "[*]"
                }.get(issue["severity"], "[?]")
                report.append(f"  {i}. {severity_emoji} [{issue['severity'].upper()}] {issue['message']}")

        report.append("\n维度评分:")
        for dim, info in self.DIMENSIONS.items():
            score = self.scores.get(dim, 0)
            bar = "=" * score + "-" * (10 - score)
            report.append(f"  {info['name']:<8} [{bar}] {score}/10 ({info['weight']*100:.0f}%)")

        weighted_score = sum(
            self.scores.get(dim, 0) * info["weight"]
            for dim, info in self.DIMENSIONS.items()
        )
        report.append(f"\n加权总分: {weighted_score:.1f}/100")

        passed = weighted_score >= 80 and not self.has_critical_issues()
        status = "通过" if passed else "未通过"
        report.append(f"验证状态: {status}")

        return "\n".join(report)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python validate_skill.py <skill-directory>")
        sys.exit(1)

    skill_path = sys.argv[1]
    validator = SkillValidator(skill_path)
    passed, score, scores = validator.validate()

    print(validator.get_report())

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
