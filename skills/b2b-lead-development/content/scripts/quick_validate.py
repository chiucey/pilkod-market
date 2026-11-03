#!/usr/bin/env python3
"""
B2B Lead Development Skill - Quick Validation Script
验证技能包结构和Frontmatter格式
"""

import os
import sys
import json
import re
from pathlib import Path

class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> bool:
        """执行所有验证"""
        print(f"\n{'='*60}")
        print(f"验证技能: {self.skill_path.name}")
        print(f"{'='*60}\n")

        # 1. 目录结构验证
        self.check_directory_structure()

        # 2. Frontmatter验证
        self.check_frontmatter()

        # 3. _meta.json验证
        self.check_meta_json()

        # 4. 文件内容检查
        self.check_file_contents()

        # 输出结果
        self.print_results()

        return len(self.errors) == 0

    def check_directory_structure(self):
        """检查目录结构"""
        required_dirs = ['scripts', 'references', 'assets']
        required_files = ['SKILL.md', '_meta.json']

        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if dir_path.exists():
                self.passed.append(f"✓ 目录存在: {dir_name}")
            else:
                self.warnings.append(f"⚠ 目录不存在: {dir_name}")

        for file_name in required_files:
            file_path = self.skill_path / file_name
            if file_path.exists():
                self.passed.append(f"✓ 文件存在: {file_name}")
            else:
                self.errors.append(f"✗ 文件缺失: {file_name}")

    def check_frontmatter(self):
        """检查Frontmatter格式"""
        skill_md = self.skill_path / 'SKILL.md'

        if not skill_md.exists():
            self.errors.append("✗ SKILL.md不存在，无法验证frontmatter")
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查是否以---开头
        if not content.strip().startswith('---'):
            self.errors.append("✗ SKILL.md必须以YAML frontmatter开头（---）")
            return

        # 提取frontmatter
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            self.errors.append("✗ 缺少frontmatter结束标记（---）")
            return

        frontmatter_text = '\n'.join(lines[1:frontmatter_end])

        # 解析frontmatter
        try:
            import yaml
            frontmatter = yaml.safe_load(frontmatter_text)
        except Exception as e:
            self.errors.append(f"✗ YAML解析错误: {e}")
            return

        # 检查必需字段
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(f"✗ Frontmatter缺少必需字段: {field}")
            else:
                self.passed.append(f"✓ Frontmatter字段: {field}")

        # 检查name格式
        if 'name' in frontmatter:
            name = frontmatter['name']
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"✗ name必须使用小写字母、数字、连字符: {name}")
            if len(name) > 64:
                self.errors.append(f"✗ name长度不能超过64字符: {len(name)}")
            if name != self.skill_path.name:
                self.errors.append(f"✗ name必须与文件夹名称匹配: {name} != {self.skill_path.name}")

        # 检查description格式
        if 'description' in frontmatter:
            desc = frontmatter['description']
            if len(desc) < 20:
                self.warnings.append(f"⚠ description可能太短，建议至少20字符")
            if 'Use when' not in desc and '当用户' not in desc:
                self.warnings.append(f"⚠ description建议包含触发短语（Use when...）")

    def check_meta_json(self):
        """检查_meta.json"""
        meta_path = self.skill_path / '_meta.json'

        if not meta_path.exists():
            self.errors.append("✗ _meta.json不存在")
            return

        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
        except Exception as e:
            self.errors.append(f"✗ _meta.json解析错误: {e}")
            return

        # 检查必需字段
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                self.errors.append(f"✗ _meta.json缺少必需字段: {field}")
            else:
                self.passed.append(f"✓ _meta.json字段: {field}")

        # 检查version格式
        if 'version' in meta:
            version = meta['version']
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                self.errors.append(f"✗ version格式错误，应为x.y.z: {version}")

    def check_file_contents(self):
        """检查文件内容"""
        skill_md = self.skill_path / 'SKILL.md'

        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')

            # 检查是否有markdown标题在frontmatter之前
            lines = content.split('\n')
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    break

            if frontmatter_end > 0:
                before_frontmatter = '\n'.join(lines[:frontmatter_end])
                if re.search(r'^#\s+\S+', before_frontmatter, re.MULTILINE):
                    self.errors.append("✗ Markdown标题不能出现在frontmatter之前")
                else:
                    self.passed.append("✓ Frontmatter格式正确")

            # 检查文件大小
            if len(content) < 1000:
                self.warnings.append("⚠ SKILL.md内容可能太少")

            # 检查基本结构
            if '#' not in content:
                self.warnings.append("⚠ SKILL.md缺少Markdown标题")

    def print_results(self):
        """打印验证结果"""
        print("\n" + "="*60)
        print("验证结果")
        print("="*60 + "\n")

        if self.passed:
            print("✓ 通过检查:")
            for item in self.passed:
                print(f"  {item}")

        if self.warnings:
            print("\n⚠ 警告:")
            for item in self.warnings:
                print(f"  {item}")

        if self.errors:
            print("\n✗ 错误:")
            for item in self.errors:
                print(f"  {item}")

        print("\n" + "="*60)
        if len(self.errors) == 0:
            print("✓ 验证通过!")
        else:
            print(f"✗ 验证失败 ({len(self.errors)} 个错误)")
        print("="*60 + "\n")


def main():
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    validator = SkillValidator(skill_path)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
