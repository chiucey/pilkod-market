#!/usr/bin/env python3
"""
A股主力博弈分析系统 - 技能验证脚本
验证 SKILL.md 和 _meta.json 的格式规范
"""

import json
import os
import re
import sys
from pathlib import Path


class SkillValidator:
    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir)
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """执行所有验证检查"""
        self._check_files_exist()
        if not self.errors:
            self._validate_frontmatter()
            self._validate_meta_json()
            self._validate_naming()
        return len(self.errors) == 0

    def _check_files_exist(self):
        """检查必需文件是否存在"""
        skill_md = self.skill_dir / "SKILL.md"
        meta_json = self.skill_dir / "_meta.json"

        if not skill_md.exists():
            self.errors.append(f"Missing required file: SKILL.md")
        if not meta_json.exists():
            self.errors.append(f"Missing required file: _meta.json")

    def _validate_frontmatter(self):
        """验证 SKILL.md 的 frontmatter 格式"""
        skill_md = self.skill_dir / "SKILL.md"
        content = skill_md.read_text(encoding='utf-8')

        # 检查第一行必须是 ---
        lines = content.split('\n')
        if not lines or lines[0].strip() != '---':
            self.errors.append("SKILL.md must start with '---' (frontmatter delimiter)")
            return

        # 查找 frontmatter 结束标记
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx == -1:
            self.errors.append("SKILL.md missing closing '---' for frontmatter")
            return

        # 提取 frontmatter 内容
        frontmatter_lines = lines[1:end_idx]
        frontmatter_text = '\n'.join(frontmatter_lines)

        # 解析 YAML 格式的 frontmatter
        try:
            frontmatter = {}
            for line in frontmatter_lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

            # 检查必需字段
            if 'name' not in frontmatter:
                self.errors.append("Frontmatter missing required field: 'name'")

            if 'description' not in frontmatter:
                self.errors.append("Frontmatter missing required field: 'description'")

            # 检查 description 是否包含触发短语
            description = frontmatter.get('description', '')
            if 'Trigger' not in description and '触发' not in description:
                self.warnings.append("Frontmatter description should include trigger keywords (e.g., 'Trigger keywords: ...')")

        except Exception as e:
            self.errors.append(f"Failed to parse frontmatter: {e}")

    def _validate_meta_json(self):
        """验证 _meta.json 格式"""
        meta_json = self.skill_dir / "_meta.json"

        try:
            data = json.loads(meta_json.read_text(encoding='utf-8'))

            # 检查必需字段
            if 'id' not in data:
                self.errors.append("_meta.json missing required field: 'id'")
            elif not isinstance(data['id'], (int, str)):
                self.errors.append("_meta.json 'id' must be integer or string")

            if 'version' not in data:
                self.errors.append("_meta.json missing required field: 'version'")
            elif not re.match(r'^\d+\.\d+\.\d+$', str(data['version'])):
                self.warnings.append("_meta.json 'version' should follow semantic versioning (e.g., '1.0.0')")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in _meta.json: {e}")

    def _validate_naming(self):
        """验证命名规范"""
        # 检查文件夹名称是否为英文连字符格式
        folder_name = self.skill_dir.name
        if not re.match(r'^[a-z0-9-]+$', folder_name):
            self.errors.append(f"Folder name '{folder_name}' must be lowercase with hyphens only (e.g., 'my-skill')")

        # 检查 SKILL.md frontmatter 中的 name 是否匹配
        skill_md = self.skill_dir / "SKILL.md"
        content = skill_md.read_text(encoding='utf-8')

        # 提取 frontmatter
        lines = content.split('\n')
        frontmatter_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            if in_frontmatter:
                frontmatter_lines.append(line)

        for line in frontmatter_lines:
            if line.startswith('name:'):
                name = line.split(':', 1)[1].strip()
                # name 应该是连字符格式
                if not re.match(r'^[a-z0-9-]+$', name):
                    self.warnings.append(f"Frontmatter 'name' should use hyphen-case format (e.g., 'my-skill')")

    def print_report(self):
        """打印验证报告"""
        print("=" * 60)
        print("SKILL VALIDATION REPORT")
        print("=" * 60)
        print(f"Skill directory: {self.skill_dir}")
        print()

        if self.warnings:
            print("⚠️  WARNINGS:")
            for w in self.warnings:
                print(f"  - {w}")
            print()

        if self.errors:
            print("❌ ERRORS:")
            for e in self.errors:
                print(f"  - {e}")
            print()
            print("❌ Validation FAILED")
        else:
            print("✅ Validation PASSED")

        print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill-directory>")
        sys.exit(1)

    skill_dir = sys.argv[1]
    validator = SkillValidator(skill_dir)

    if validator.validate_all():
        validator.print_report()
        sys.exit(0)
    else:
        validator.print_report()
        sys.exit(1)


if __name__ == "__main__":
    main()