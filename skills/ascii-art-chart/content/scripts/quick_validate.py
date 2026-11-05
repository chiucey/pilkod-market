#!/usr/bin/env python3
"""
ASCII Art Chart Skill Validator
验证技能结构和内容的完整性
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
        self.check_references()

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

        # 检查是否以 --- 开头
        if not content.startswith('---'):
            self.errors.append("SKILL.md must start with YAML frontmatter (---)")
            return

        # 提取 frontmatter
        lines = content.split('\n')
        if len(lines) < 3:
            self.errors.append("Frontmatter is too short")
            return

        # 解析 frontmatter
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

            # 检查必需字段
            if 'name:' not in frontmatter_text:
                self.errors.append("Missing required field: name")

            if 'description:' not in frontmatter_text:
                self.errors.append("Missing required field: description")

            # 检查 name 格式
            name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()
                if not re.match(r'^[a-z0-9-]+$', name):
                    self.errors.append(f"Invalid name format: '{name}'. Use lowercase with hyphens only.")

                # 检查与文件夹名称匹配
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

            # 检查 version 格式
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

    def check_references(self):
        """检查参考文档链接"""
        skill_md = self.skill_path / 'SKILL.md'

        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查是否有 orphaned 链接
        references_dir = self.skill_path / 'references'
        if references_dir.exists():
            ref_files = {f.stem for f in references_dir.iterdir() if f.is_file()}

            # 检查是否有 markdown 链接指向不存在的文件
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            for match in re.finditer(link_pattern, content):
                link = match.group(2)
                if link.startswith('references/'):
                    ref_file = link.split('/')[-1].split('#')[0]
                    if ref_file and not (references_dir / ref_file).exists():
                        self.warnings.append(f"Link points to non-existent reference: {link}")


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
