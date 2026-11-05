#!/usr/bin/env python3
"""
Blood Glucose Monitor Skill Validator
验证技能结构的完整性
"""

import os
import re
import json
from pathlib import Path
from typing import List, Tuple


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """执行所有验证"""
        self.errors.clear()
        self.warnings.clear()

        self.check_structure()
        self.check_frontmatter()
        self.check_meta()
        self.check_naming()

        return len(self.errors) == 0, self.errors, self.warnings

    def check_structure(self):
        """检查目录结构"""
        required_files = ['SKILL.md', '_meta.json']

        for file in required_files:
            file_path = self.skill_path / file
            if not file_path.exists():
                self.errors.append(f"Missing required file: {file}")

    def check_frontmatter(self):
        """检查 frontmatter 格式"""
        skill_md = self.skill_path / 'SKILL.md'

        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        if not content.startswith('---'):
            self.errors.append("SKILL.md must start with YAML frontmatter (---)")
            return

        lines = content.split('\n')
        if len(lines) < 3:
            self.errors.append("Frontmatter is too short")
            return

        try:
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

            frontmatter_text = '\n'.join(frontmatter_lines)

            if 'name:' not in frontmatter_text:
                self.errors.append("Missing required field: name")

            if 'description:' not in frontmatter_text:
                self.errors.append("Missing required field: description")

            name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                if not re.match(r'^[a-z0-9-]+$', name):
                    self.errors.append(f"Invalid name format: '{name}'. Use lowercase with hyphens only.")

                folder_name = self.skill_path.name
                if name != folder_name:
                    self.errors.append(f"Name mismatch: frontmatter has '{name}', folder is '{folder_name}'")

        except Exception as e:
            self.errors.append(f"Failed to parse frontmatter: {str(e)}")

    def check_meta(self):
        """检查 _meta.json"""
        meta_file = self.skill_path / '_meta.json'

        if not meta_file.exists():
            return

        try:
            meta = json.loads(meta_file.read_text(encoding='utf-8'))

            required_fields = ['id', 'version']
            for field in required_fields:
                if field not in meta:
                    self.errors.append(f"Missing required field in _meta.json: {field}")

            if 'version' in meta:
                version = meta['version']
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    self.warnings.append(f"Version format may not follow semver: {version}")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in _meta.json: {str(e)}")

    def check_naming(self):
        """检查命名规范"""
        folder_name = self.skill_path.name

        if not re.match(r'^[a-z0-9-]+$', folder_name):
            self.errors.append(f"Folder name contains invalid characters: {folder_name}")
            self.errors.append("Use only lowercase letters, numbers, and hyphens")

        if len(folder_name) > 64:
            self.errors.append(f"Folder name too long: {len(folder_name)} characters (max 64)")


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    validator = SkillValidator(skill_path)

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    is_valid, errors, warnings = validator.validate_all()

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠ {w}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  ✗ {e}")

    if is_valid and not errors:
        print("\n✓ All validations passed!")
        sys.exit(0)
    else:
        print("\n✗ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
