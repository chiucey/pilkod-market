#!/usr/bin/env python3
"""
Quick Validation Script for Agent Skill Optimizer
Validates frontmatter, structure, and quality constraints
"""

import os
import re
import json
import sys
from pathlib import Path

class SkillValidator:
    """验证技能质量门槛"""

    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []

    def validate(self):
        """执行完整验证"""
        print(f"🔍 Validating skill at: {self.skill_path}")
        print("=" * 60)

        # 1. Frontmatter + 结构验证
        self.validate_frontmatter()
        self.validate_meta()
        self.validate_structure()

        # 2. 输出结果
        self.print_results()

        return len(self.errors) == 0

    def validate_frontmatter(self):
        """验证 Frontmatter 格式"""
        print("\n📋 Frontmatter 验证...")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查是否以 --- 开头
        if not content.strip().startswith('---'):
            self.errors.append("❌ SKILL.md 必须以 frontmatter --- 开头，而非 # 标题")
            return

        # 提取 frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            self.errors.append("❌ 无法解析 frontmatter")
            return

        frontmatter = frontmatter_match.group(1)

        # 必填字段检查
        if 'name:' not in frontmatter:
            self.errors.append("❌ Frontmatter 缺少 name 字段")

        if 'description:' not in frontmatter:
            self.errors.append("❌ Frontmatter 缺少 description 字段")

        # description 必须包含触发短语
        desc_match = re.search(r'description:\s*(.+)', frontmatter)
        if desc_match:
            desc = desc_match.group(1)
            if not any(trigger in desc for trigger in ['使用', '当用户', '用于', '触发']):
                self.warnings.append("⚠️ description 建议包含触发短语（使用/当用户/用于/触发）")

        print("✅ Frontmatter 格式正确")

    def validate_meta(self):
        """验证 _meta.json"""
        print("\n📦 _meta.json 验证...")

        meta_path = self.skill_path / "_meta.json"
        if not meta_path.exists():
            self.errors.append("❌ _meta.json 文件不存在")
            return

        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))

            if 'id' not in meta:
                self.errors.append("❌ _meta.json 缺少 id 字段")

            if 'version' not in meta:
                self.errors.append("❌ _meta.json 缺少 version 字段")

            # 版本格式检查（语义化版本）
            if 'version' in meta:
                version = meta['version']
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    self.warnings.append(f"⚠️ version '{version}' 建议使用语义化格式（如 1.0.0）")

            print("✅ _meta.json 结构正确")

        except json.JSONDecodeError as e:
            self.errors.append(f"❌ _meta.json 格式错误: {e}")

    def validate_structure(self):
        """验证目录结构"""
        print("\n📁 目录结构验证...")

        expected_dirs = ['scripts', 'references', 'assets']
        existing_dirs = [d for d in expected_dirs if (self.skill_path / d).is_dir()]

        if existing_dirs:
            print(f"  现有目录: {', '.join(existing_dirs)}")

        # 检查文件路径是否安全（防止符号链接逃逸）
        for item in self.skill_path.rglob('*'):
            if item.is_symlink():
                self.errors.append(f"❌ 发现符号链接（可能不安全）: {item}")

        print("✅ 目录结构验证通过")

    def print_results(self):
        """打印验证结果"""
        print("\n" + "=" * 60)
        print("📊 验证结果汇总")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ 所有验证通过！")
        elif not self.errors:
            print("\n✅ 验证通过（有警告）")
        else:
            print("\n❌ 验证失败，请修复上述错误")


def main():
    if len(sys.argv) < 2:
        skill_path = "/workspace/temp-skills/agent-skill-optimizer"
    else:
        skill_path = sys.argv[1]

    validator = SkillValidator(skill_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
