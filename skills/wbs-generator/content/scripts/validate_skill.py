#!/usr/bin/env python3
"""
WBS Generator Skill Validator
验证WBS技能的结构和内容是否符合规范
"""

import os
import sys
import re
import json
from pathlib import Path

class SkillValidator:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []

    def validate(self):
        """执行所有验证检查"""
        print(f"验证技能: {self.skill_path.name}")
        print("=" * 50)

        self.check_directory_structure()
        self.check_skill_md()
        self.check_meta_json()
        self.check_references()

        self.print_results()
        return len(self.errors) == 0

    def check_directory_structure(self):
        """检查目录结构"""
        required_dirs = ['references', 'scripts']
        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                self.warnings.append(f"建议目录不存在: {dir_name}")
            elif not dir_path.is_dir():
                self.errors.append(f"{dir_name} 不是目录")

    def check_skill_md(self):
        """检查SKILL.md文件"""
        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            self.errors.append("SKILL.md 文件不存在")
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查frontmatter
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以frontmatter (---) 开头")
            return

        # 提取frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            self.errors.append("无法解析frontmatter")
            return

        try:
            frontmatter = self._parse_frontmatter(match.group(1))
        except Exception as e:
            self.errors.append(f"Frontmatter解析错误: {e}")
            return

        # 检查必需字段
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(f"Frontmatter缺少必需字段: {field}")

        # 检查name格式
        if 'name' in frontmatter:
            name = frontmatter['name']
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"name字段格式错误，应为小写字母、数字和连字符: {name}")

        # 检查description不为空
        if 'description' in frontmatter:
            if len(frontmatter['description'].strip()) < 10:
                self.warnings.append("description字段过短，建议至少10个字符")

    def check_meta_json(self):
        """检查_meta.json文件"""
        meta_json = self.skill_path / "_meta.json"

        if not meta_json.exists():
            self.errors.append("_meta.json 文件不存在")
            return

        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON格式错误: {e}")
            return

        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                self.errors.append(f"_meta.json缺少必需字段: {field}")

        # 检查version格式
        if 'version' in meta:
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                self.warnings.append("version字段建议使用语义化版本格式 (x.y.z)")

    def check_references(self):
        """检查references目录"""
        ref_dir = self.skill_path / "references"
        if ref_dir.exists():
            ref_files = list(ref_dir.glob("*.md"))
            if len(ref_files) == 0:
                self.warnings.append("references目录为空，建议添加参考文档")

    def _parse_frontmatter(self, text):
        """解析YAML格式的frontmatter"""
        result = {}
        for line in text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip().strip('"').strip("'")
        return result

    def print_results(self):
        """打印验证结果"""
        if self.errors:
            print("\n❌ 错误:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️ 警告:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ 验证通过!")
        elif not self.errors:
            print("\n✅ 验证通过 (有警告)")
        else:
            print("\n❌ 验证失败")

def main():
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    validator = SkillValidator(skill_path)
    success = validator.validate()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
