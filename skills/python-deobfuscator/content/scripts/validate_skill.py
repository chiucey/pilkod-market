#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Deobfuscator Skill 验证脚本
验证技能结构和内容是否符合规范
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed = 0
        self.failed = 0

    def log_pass(self, message: str):
        """记录通过的检查"""
        self.passed += 1
        print(f"    [PASS] {message}")

    def log_fail(self, message: str):
        """记录失败的检查"""
        self.failed += 1
        self.errors.append(message)
        print(f"    [FAIL] {message}")

    def log_warn(self, message: str):
        """记录警告"""
        self.warnings.append(message)
        print(f"    [WARN] {message}")

    def validate(self) -> bool:
        """执行所有验证"""
        print("=" * 60)
        print("SKILL VALIDATION")
        print("=" * 60)
        print(f"\nSkill Path: {self.skill_path}\n")

        # 1. 目录结构检查
        self.validate_structure()

        # 2. SKILL.md 检查
        self.validate_skill_md()

        # 3. _meta.json 检查
        self.validate_meta_json()

        # 4. 脚本检查
        self.validate_scripts()

        # 5. 参考文档检查
        self.validate_references()

        # 输出结果
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Warnings: {len(self.warnings)}")

        if self.errors:
            print("\nErrors:")
            for err in self.errors:
                print(f"  - {err}")

        if self.warnings:
            print("\nWarnings:")
            for warn in self.warnings:
                print(f"  - {warn}")

        return self.failed == 0

    def validate_structure(self):
        """验证目录结构"""
        print("\n[1] Directory Structure")

        required_items = [
            'SKILL.md',
            '_meta.json',
            'scripts',
        ]

        for item in required_items:
            path = self.skill_path / item
            if path.exists():
                self.log_pass(f"{item} exists")
            else:
                self.log_fail(f"{item} missing")

    def validate_skill_md(self):
        """验证SKILL.md"""
        print("\n[2] SKILL.md Validation")

        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            self.log_fail("SKILL.md not found")
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查frontmatter
        if not content.startswith('---'):
            self.log_fail("SKILL.md must start with YAML frontmatter (---)")
            return
        else:
            self.log_pass("Has YAML frontmatter")

        # 提取frontmatter
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            self.log_fail("YAML frontmatter not properly closed")
            return

        frontmatter = content[3:frontmatter_end].strip()

        # 检查必填字段
        if 'name:' in frontmatter:
            self.log_pass("Has 'name' field")
        else:
            self.log_fail("Missing 'name' field in frontmatter")

        if 'description:' in frontmatter:
            self.log_pass("Has 'description' field")
            # 检查触发短语
            if 'Use when' in frontmatter or '当用户要求' in frontmatter:
                self.log_pass("Has trigger phrase")
            else:
                self.log_warn("Description should include trigger phrases")
        else:
            self.log_fail("Missing 'description' field in frontmatter")

        # 检查名称格式
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if '-' in name:
                self.log_pass(f"Name uses hyphen-case: {name}")
            else:
                self.log_warn(f"Name should use hyphen-case: {name}")

    def validate_meta_json(self):
        """验证_meta.json"""
        print("\n[3] _meta.json Validation")

        meta_json = self.skill_path / '_meta.json'
        if not meta_json.exists():
            self.log_fail("_meta.json not found")
            return

        try:
            data = json.loads(meta_json.read_text(encoding='utf-8'))

            # 检查必填字段
            if 'id' in data:
                self.log_pass("Has 'id' field")
            else:
                self.log_fail("Missing 'id' field")

            if 'version' in data:
                self.log_pass("Has 'version' field")
                # 检查版本格式
                if re.match(r'^\d+\.\d+\.\d+$', data['version']):
                    self.log_pass("Version format is semantic")
                else:
                    self.log_warn("Version should follow semantic versioning (x.y.z)")
            else:
                self.log_fail("Missing 'version' field")

        except json.JSONDecodeError as e:
            self.log_fail(f"Invalid JSON: {e}")

    def validate_scripts(self):
        """验证脚本文件"""
        print("\n[4] Scripts Validation")

        scripts_dir = self.skill_path / 'scripts'
        if not scripts_dir.exists():
            self.log_fail("scripts/ directory not found")
            return

        py_files = list(scripts_dir.glob('*.py'))
        if py_files:
            self.log_pass(f"Found {len(py_files)} Python script(s)")
            for py_file in py_files:
                # 检查是否为有效Python文件
                try:
                    content = py_file.read_text(encoding='utf-8')
                    if content.startswith('#!/usr/bin/env python') or \
                       content.startswith('# -*- coding:'):
                        self.log_pass(f"{py_file.name} has valid header")
                    else:
                        self.log_warn(f"{py_file.name} missing standard header")
                except Exception as e:
                    self.log_fail(f"Cannot read {py_file.name}: {e}")
        else:
            self.log_warn("No Python scripts found")

    def validate_references(self):
        """验证参考文档"""
        print("\n[5] References Validation")

        refs_dir = self.skill_path / 'references'
        if not refs_dir.exists():
            self.log_warn("references/ directory not found (optional)")
            return

        md_files = list(refs_dir.glob('*.md'))
        if md_files:
            self.log_pass(f"Found {len(md_files)} reference document(s)")
            for md_file in md_files:
                self.log_pass(f"  - {md_file.name}")
        else:
            self.log_warn("No reference documents found")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    validator = SkillValidator(skill_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
