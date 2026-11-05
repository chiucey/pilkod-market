#!/usr/bin/env python3
"""
投资认知条目验证脚本
验证认知条目是否符合标准格式和内容要求
"""

import re
import sys
from typing import Dict, List, Tuple, Any

class CognitionValidator:
    """认知条目验证器"""

    # 必需的元数据字段
    REQUIRED_META_FIELDS = [
        "录入时间",
        "分类来源",
        "综合评分",
        "时效标记"
    ]

    # 必需的量化评分字段
    REQUIRED_SCORING_FIELDS = [
        "逻辑完整性",
        "数据支撑",
        "时效适用",
        "可执行性"
    ]

    # 时效标记可选值
    VALID_TIME_TAGS = [
        "短期有效",
        "中期有效",
        "长期有效",
        "永久有效"
    ]

    # 分类来源可选值
    VALID_CATEGORIES = [
        "技术面",
        "情绪面",
        "基本面",
        "政策面",
        "散户心理",
        "主力意图",
        "关注票池",
        "近期盘面"
    ]

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.score = 0

    def validate(self, content: str) -> Tuple[bool, Dict[str, Any]]:
        """
        验证认知条目内容
        返回: (是否通过, {详细结果字典})
        """
        self.errors = []
        self.warnings = []
        self.score = 0

        # 1. 检查标题
        self._validate_title(content)

        # 2. 检查必需元数据
        self._validate_meta_fields(content)

        # 3. 检查量化评分
        self._validate_scoring(content)

        # 4. 检查核心内容
        self._validate_core_content(content)

        # 5. 检查原始输入
        self._validate_original_input(content)

        # 6. 检查适用条件
        self._validate_conditions(content)

        # 计算总分
        self._calculate_score()

        passed = len(self.errors) == 0

        result = {
            "passed": passed,
            "score": self.score,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": self._generate_summary()
        }

        return passed, result

    def _validate_title(self, content: str):
        """验证标题"""
        title_pattern = r'^##\s+(.+)$'
        match = re.search(title_pattern, content, re.MULTILINE)

        if not match:
            self.errors.append("缺少认知标题（应使用 ## 标题格式）")
            return

        title = match.group(1).strip()
        if len(title) > 30:
            self.warnings.append(f"标题过长（{len(title)}字符），建议不超过30字符")
        if len(title) < 5:
            self.warnings.append("标题过短，可能不够明确")

    def _validate_meta_fields(self, content: str):
        """验证元数据字段"""
        for field in self.REQUIRED_META_FIELDS:
            if f"**{field}**" not in content:
                self.errors.append(f"缺少必需字段：{field}")

        # 验证时效标记
        time_tag_match = re.search(r'\*\*时效标记\*\*：(.+)', content)
        if time_tag_match:
            time_tag = time_tag_match.group(1).strip()
            valid = any(tag in time_tag for tag in self.VALID_TIME_TAGS)
            if not valid:
                self.errors.append(
                    f"时效标记值无效：{time_tag}，应包含 {', '.join(self.VALID_TIME_TAGS)} 之一"
                )

        # 验证分类来源
        category_match = re.search(r'\*\*分类来源\*\*：(.+)', content)
        if category_match:
            category = category_match.group(1).strip()
            valid = any(cat in category for cat in self.VALID_CATEGORIES)
            if not valid:
                self.warnings.append(
                    f"分类来源可能无效：{category}，建议使用 {', '.join(self.VALID_CATEGORIES)}"
                )

    def _validate_scoring(self, content: str):
        """验证量化评分"""
        # 检查综合评分
        total_score_match = re.search(r'\*\*综合评分\*\*：(\d+)', content)
        if total_score_match:
            score = int(total_score_match.group(1))
            if score < 0 or score > 100:
                self.errors.append(f"综合评分超出范围：{score}（应为0-100）")
        else:
            self.errors.append("缺少综合评分")

        # 检查各维度评分
        for field in self.REQUIRED_SCORING_FIELDS:
            pattern = rf'- {field}：(\d+)/25'
            match = re.search(pattern, content)
            if not match:
                self.warnings.append(f"缺少评分字段：{field}")
                continue

            score = int(match.group(1))
            if score < 0 or score > 25:
                self.warnings.append(f"{field}评分超出范围：{score}（应为0-25）")

        # 验证综合评分是否等于各项之和
        if total_score_match:
            calculated_score = 0
            for field in self.REQUIRED_SCORING_FIELDS:
                pattern = rf'- {field}：(\d+)/25'
                match = re.search(pattern, content)
                if match:
                    calculated_score += int(match.group(1))

            actual_score = int(total_score_match.group(1))
            if abs(calculated_score - actual_score) > 5:
                self.warnings.append(
                    f"综合评分({actual_score})与各项之和({calculated_score})不一致"
                )

    def _validate_core_content(self, content: str):
        """验证核心内容"""
        if "### 核心内容" not in content:
            self.errors.append("缺少核心内容章节（### 核心内容）")
            return

        # 检查核心内容是否为空
        core_match = re.search(
            r'### 核心内容\s*\n(.+?)(?=\n###|\n---|\Z)',
            content,
            re.DOTALL
        )
        if core_match:
            core_content = core_match.group(1).strip()
            if len(core_content) < 20:
                self.warnings.append("核心内容过于简短，可能描述不够清晰")
            if len(core_content) > 500:
                self.warnings.append("核心内容过长，建议精简到3-5句话")
        else:
            self.errors.append("核心内容为空")

    def _validate_original_input(self, content: str):
        """验证原始输入"""
        if "### 原始输入" not in content:
            self.warnings.append("缺少原始输入章节，建议保留原始输入以备追溯")
            return

        original_match = re.search(
            r'>\s*(.+?)(?:\n|$)',
            content
        )
        if not original_match:
            self.warnings.append("原始输入格式可能不正确（应为 > 引用格式）")

    def _validate_conditions(self, content: str):
        """验证适用条件"""
        if "### 适用条件" not in content:
            self.warnings.append("缺少适用条件章节，建议明确使用场景")
            return

        # 检查是否有列表项
        conditions_section = re.search(
            r'### 适用条件\s*\n((?:\d+\..+\n?)+)',
            content
        )
        if not conditions_section:
            self.warnings.append("适用条件应使用编号列表格式")

    def _calculate_score(self):
        """计算验证得分"""
        base_score = 100

        # 每项错误扣分
        self.score = base_score - len(self.errors) * 10 - len(self.warnings) * 2

        # 确保分数在0-100范围内
        self.score = max(0, min(100, self.score))

    def _generate_summary(self) -> str:
        """生成验证摘要"""
        lines = []
        lines.append(f"验证得分: {self.score}/100")

        if self.errors:
            lines.append(f"\n错误 ({len(self.errors)}项):")
            for error in self.errors:
                lines.append(f"  • {error}")

        if self.warnings:
            lines.append(f"\n警告 ({len(self.warnings)}项):")
            for warning in self.warnings:
                lines.append(f"  • {warning}")

        if not self.errors and not self.warnings:
            lines.append("\n✓ 认知条目格式完全符合规范")

        return "\n".join(lines)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python validate_cognition.py <文件路径>")
        print("   或: python validate_cognition.py --stdin")
        sys.exit(1)

    if sys.argv[1] == "--stdin":
        # 从标准输入读取
        content = sys.stdin.read()
    else:
        # 从文件读取
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"错误: 文件不存在 {file_path}")
            sys.exit(1)

    validator = CognitionValidator()
    passed, result = validator.validate(content)

    print("=" * 50)
    print("认知条目验证结果")
    print("=" * 50)
    print()
    print(result["summary"])
    print()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
