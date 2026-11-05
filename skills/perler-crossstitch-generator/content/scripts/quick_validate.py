#!/usr/bin/env python3
"""
拼豆十字绣图纸生成器 - 技能验证脚本
验证 SKILL.md 结构和 frontmatter
"""

import os
import re
import json
from pathlib import Path

class SkillValidator:
    def __init__(self, skill_dir):
        self.skill_dir = Path(skill_dir)
        self.errors = []
        self.warnings = []

    def validate(self):
        """执行所有验证"""
        print(f"验证技能目录: {self.skill_dir}")
        print("=" * 50)

        self.validate_structure()
        self.validate_frontmatter()
        self.validate_meta()
        self.validate_naming()

        self.print_results()
        return len(self.errors) == 0

    def validate_structure(self):
        """验证目录结构"""
        required_files = ['SKILL.md', '_meta.json']
        for f in required_files:
            path = self.skill_dir / f
            if not path.exists():
                self.errors.append(f"缺少必需文件: {f}")
            else:
                print(f"✓ 找到文件: {f}")

        # 检查目录结构
        for subdir in ['scripts', 'assets', 'references']:
            path = self.skill_dir / subdir
            if path.exists():
                print(f"✓ 目录存在: {subdir}/")

    def validate_frontmatter(self):
        """验证 SKILL.md frontmatter"""
        skill_md = self.skill_dir / 'SKILL.md'
        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查 frontmatter 格式
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 YAML frontmatter 开始 (---)")
            return

        # 提取 frontmatter
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            self.errors.append("未找到 frontmatter 结束标记 (---)")
            return

        frontmatter_text = '\n'.join(lines[1:frontmatter_end])

        # 验证必需字段
        if 'name:' not in frontmatter_text:
            self.errors.append("frontmatter 缺少 'name' 字段")
        else:
            print("✓ frontmatter 包含 'name' 字段")

        if 'description:' not in frontmatter_text:
            self.errors.append("frontmatter 缺少 'description' 字段")
        else:
            print("✓ frontmatter 包含 'description' 字段")

        # 验证触发短语
        if 'Use when' not in frontmatter_text and '当用户' not in frontmatter_text:
            self.warnings.append("description 建议包含触发短语 (Use when... / 当用户...)")

    def validate_meta(self):
        """验证 _meta.json"""
        meta_file = self.skill_dir / '_meta.json'
        if not meta_file.exists():
            self.errors.append("_meta.json 文件不存在")
            return

        try:
            meta = json.loads(meta_file.read_text(encoding='utf-8'))

            if 'id' not in meta:
                self.errors.append("_meta.json 缺少 'id' 字段")
            else:
                print(f"✓ _meta.json id: {meta['id']}")

            if 'version' not in meta:
                self.errors.append("_meta.json 缺少 'version' 字段")
            else:
                print(f"✓ _meta.json version: {meta['version']}")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 格式错误: {e}")

    def validate_naming(self):
        """验证命名规范"""
        # 检查 SKILL.md 中的 name 字段
        skill_md = self.skill_dir / 'SKILL.md'
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')

            # 检查是否有中文字符在不应该出现的地方
            if re.search(r'^name:\s*[\u4e00-\u9fff]', content, re.MULTILINE):
                self.warnings.append("frontmatter 'name' 字段建议使用英文 (连字符格式)")

            # 检查路径名称
            if re.search(r'[\u4e00-\u9fff]', str(self.skill_dir)):
                self.warnings.append("目录路径包含中文字符，建议使用英文")

    def print_results(self):
        """打印验证结果"""
        print("\n" + "=" * 50)

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}):")
            for e in self.errors:
                print(f"  - {e}")

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  - {w}")

        if not self.errors and not self.warnings:
            print("\n✅ 所有验证通过!")

        print()


def main():
    import sys

    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    validator = SkillValidator(skill_dir)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
