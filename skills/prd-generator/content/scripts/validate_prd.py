#!/usr/bin/env python3
"""
PRD 生成器技能 - 质量验证脚本
PRD Generator Skill - Quality Validation Script

用于验证生成的 PRD 是否满足质量门槛要求
"""

import re
import sys
from pathlib import Path


class PRDValidator:
    """PRD 内容验证器"""

    def __init__(self, prd_content):
        self.content = prd_content
        self.errors = []
        self.warnings = []

    def check_document_info(self):
        """检查文档信息部分"""
        required_fields = ['版本', '作者', '日期', '状态']
        missing = []
        for field in required_fields:
            if field not in self.content:
                missing.append(field)

        if missing:
            self.errors.append(f"文档信息缺少: {', '.join(missing)}")

    def check_background(self):
        """检查背景与问题陈述"""
        required_sections = ['背景', '问题', '目标', '非目标']
        missing = []
        for section in required_sections:
            if section not in self.content:
                missing.append(section)

        if missing:
            self.errors.append(f"背景章节缺少: {', '.join(missing)}")

        # 检查北极星指标
        if '北极星指标' not in self.content:
            self.warnings.append("缺少北极星指标定义")

    def check_user_stories(self):
        """检查用户故事"""
        # 统计场景数量
        scenarios = re.findall(r'场景\d+[:：]', self.content)
        if len(scenarios) < 2:
            self.warnings.append(f"用户场景较少（{len(scenarios)}个），建议至少2-3个核心场景")

    def check_scope(self):
        """检查范围定义"""
        required = ['Must-have', 'MVP', 'Out of scope']
        missing = []
        for req in required:
            if req not in self.content:
                missing.append(req)

        if missing:
            self.errors.append(f"范围定义缺少: {', '.join(missing)}")

    def check_acceptance_criteria(self):
        """检查验收标准"""
        ac_patterns = [
            r'AC-\d+',
            r'验收标准',
            r'当.*则.*'
        ]

        found = False
        for pattern in ac_patterns:
            if re.search(pattern, self.content):
                found = True
                break

        if not found:
            self.errors.append("缺少验收标准（AC）定义")

        # 统计 AC 数量
        ac_count = len(re.findall(r'AC-\d+', self.content))
        if ac_count < 6:
            self.warnings.append(f"验收标准较少（{ac_count}条），建议至少6条")

    def check_risks(self):
        """检查风险与依赖"""
        required = ['依赖', '风险']
        missing = []
        for req in required:
            if req not in self.content:
                missing.append(req)

        if missing:
            self.warnings.append(f"建议添加: {', '.join(missing)}")

    def check_open_questions(self):
        """检查开放问题"""
        if '开放问题' not in self.content:
            self.warnings.append("建议添加开放问题章节")

    def validate(self):
        """执行所有验证"""
        self.check_document_info()
        self.check_background()
        self.check_user_stories()
        self.check_scope()
        self.check_acceptance_criteria()
        self.check_risks()
        self.check_open_questions()

        return len(self.errors) == 0

    def report(self):
        """生成验证报告"""
        report = []

        if self.errors:
            report.append("❌ 验证失败:")
            for err in self.errors:
                report.append(f"   - {err}")

        if self.warnings:
            report.append("⚠️  建议改进:")
            for warn in self.warnings:
                report.append(f"   - {warn}")

        if not self.errors and not self.warnings:
            report.append("✅ PRD 质量检查通过!")

        return '\n'.join(report)


def main():
    if len(sys.argv) < 2:
        print("用法: python validate_prd.py <prd_file.md>")
        print("示例: python validate_prd.py output.prd.md")
        sys.exit(1)

    prd_file = Path(sys.argv[1])
    if not prd_file.exists():
        print(f"❌ 文件不存在: {prd_file}")
        sys.exit(1)

    with open(prd_file, 'r', encoding='utf-8') as f:
        content = f.read()

    validator = PRDValidator(content)
    validator.validate()

    print("📋 PRD 质量检查报告")
    print("-" * 40)
    print(validator.report())


if __name__ == "__main__":
    main()
