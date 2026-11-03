#!/usr/bin/env python3
"""
循证建设工程商事调解技能验证脚本
验证技能结构、frontmatter规范性和内容完整性
"""

import os
import re
import json
from pathlib import Path

# 技能根目录
SKILL_ROOT = Path(__file__).parent.parent
SKILL_NAME = "chn-construction-commercial-mediation"

class SkillValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self):
        """执行所有验证"""
        print("=" * 60)
        print("循证建设工程商事调解技能 - 验证开始")
        print("=" * 60)

        self.check_directory_structure()
        self.check_meta_json()
        self.check_skill_md()
        self.check_references()

        self.print_summary()
        return len(self.errors) == 0

    def check_directory_structure(self):
        """检查目录结构"""
        print("\n[1] 检查目录结构...")

        required_dirs = ["references", "scripts"]
        for dir_name in required_dirs:
            dir_path = SKILL_ROOT / dir_name
            if dir_path.exists():
                self.passed.append(f"目录存在: {dir_name}")
            else:
                self.errors.append(f"缺少目录: {dir_name}")

    def check_meta_json(self):
        """检查_meta.json"""
        print("\n[2] 检查_meta.json...")

        meta_path = SKILL_ROOT / "_meta.json"
        if not meta_path.exists():
            self.errors.append("_meta.json 不存在")
            return

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            required_fields = ["id", "version", "name", "description"]
            for field in required_fields:
                if field in meta:
                    self.passed.append(f"_meta.json 包含字段: {field}")
                else:
                    self.errors.append(f"_meta.json 缺少字段: {field}")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON格式错误: {e}")

    def check_skill_md(self):
        """检查SKILL.md"""
        print("\n[3] 检查SKILL.md...")

        skill_path = SKILL_ROOT / "SKILL.md"
        if not skill_path.exists():
            self.errors.append("SKILL.md 不存在")
            return

        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查frontmatter格式
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 --- 开头（frontmatter）")
        else:
            self.passed.append("SKILL.md frontmatter 格式正确")

        # 提取frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            fm_content = frontmatter_match.group(1)

            # 检查必需字段
            if 'name:' in fm_content:
                self.passed.append("frontmatter 包含 name 字段")
            else:
                self.errors.append("frontmatter 缺少 name 字段")

            if 'description:' in fm_content:
                self.passed.append("frontmatter 包含 description 字段")
            else:
                self.errors.append("frontmatter 缺少 description 字段")
        else:
            self.errors.append("无法解析 frontmatter")

        # 检查核心模块
        core_modules = [
            ("DEM", "争议证据图谱"),
            ("CMCR", "类案知识库"),
            ("MDEA", "多专业协同评估"),
            ("EIMP", "循证调解策略"),
            ("MOKMS", "效果评价与知识管理")
        ]

        for abbr, name in core_modules:
            if abbr in content or name in content:
                self.passed.append(f"包含核心模块: {name} ({abbr})")
            else:
                self.warnings.append(f"可能缺少模块: {name} ({abbr})")

        # 检查GRADE证据分级
        grade_levels = ["A级", "B级", "C级", "D级"]
        for level in grade_levels:
            if level in content:
                self.passed.append(f"包含证据等级: {level}")

        # 检查质量底线
        quality_lines = ["不可编造类案数据", "不可超出证据等级做结论", "未调成案例必须做失败分析"]
        for line in quality_lines:
            if line in content:
                self.passed.append(f"包含质量底线: {line[:10]}...")

    def check_references(self):
        """检查references目录"""
        print("\n[4] 检查references目录...")

        refs_dir = SKILL_ROOT / "references"
        if not refs_dir.exists():
            self.errors.append("references 目录不存在")
            return

        required_refs = [
            "legal-reference.md",
            "case-search-guide.md",
            "mediator-guide.md",
            "agent-guide.md",
            "applicant-guide.md"
        ]

        for ref_file in required_refs:
            ref_path = refs_dir / ref_file
            if ref_path.exists():
                self.passed.append(f"参考文档存在: {ref_file}")
            else:
                self.warnings.append(f"建议添加参考文档: {ref_file}")

    def print_summary(self):
        """打印验证摘要"""
        print("\n" + "=" * 60)
        print("验证结果摘要")
        print("=" * 60)

        print(f"\n✅ 通过项: {len(self.passed)}")
        for item in self.passed[:10]:
            print(f"   • {item}")
        if len(self.passed) > 10:
            print(f"   ... 还有 {len(self.passed) - 10} 项")

        if self.warnings:
            print(f"\n⚠️ 警告项: {len(self.warnings)}")
            for item in self.warnings:
                print(f"   • {item}")

        if self.errors:
            print(f"\n❌ 错误项: {len(self.errors)}")
            for item in self.errors:
                print(f"   • {item}")
        else:
            print("\n✅ 所有验证通过!")

        print("\n" + "=" * 60)

if __name__ == "__main__":
    validator = SkillValidator()
    success = validator.validate_all()
    exit(0 if success else 1)
