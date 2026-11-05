#!/usr/bin/env python3
"""
股票热点概念技能验证脚本
验证技能文件的结构、frontmatter和内容质量
"""

import os
import re
import json
from pathlib import Path

class SkillValidator:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """执行所有验证检查"""
        print(f"正在验证技能: {self.skill_path.name}")
        print("=" * 50)

        # 1. 检查目录结构
        self.check_structure()

        # 2. 验证SKILL.md
        self.validate_skill_md()

        # 3. 验证_meta.json
        self.validate_meta_json()

        # 4. 输出结果
        self.print_results()

        return len(self.errors) == 0

    def check_structure(self):
        """检查目录结构"""
        required_files = ['SKILL.md', '_meta.json']
        for file in required_files:
            file_path = self.skill_path / file
            if not file_path.exists():
                self.errors.append(f"缺少必需文件: {file}")
            else:
                print(f"✓ 找到文件: {file}")

    def validate_skill_md(self):
        """验证SKILL.md文件"""
        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查frontmatter格式
        if not content.startswith('---'):
            self.errors.append("SKILL.md必须以frontmatter YAML块开始")
            return

        # 提取frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            self.errors.append("无法解析frontmatter块")
            return

        frontmatter = frontmatter_match.group(1)

        # 验证必需字段
        required_fields = ['name', 'description']
        for field in required_fields:
            if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
                self.errors.append(f"frontmatter缺少必需字段: {field}")
            else:
                print(f"✓ frontmatter包含字段: {field}")

        # 检查description长度
        desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                self.warnings.append("description字段可能过短，建议至少20字符")
            else:
                print(f"✓ description长度: {len(desc)}字符")

        # 检查name格式
        name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                self.warnings.append("name建议使用小写字母、数字和连字符")
            elif name != self.skill_path.name:
                self.warnings.append(f"name('{name}')应与目录名('{self.skill_path.name}')匹配")
            else:
                print(f"✓ name格式正确: {name}")

    def validate_meta_json(self):
        """验证_meta.json文件"""
        meta_json = self.skill_path / '_meta.json'
        if not meta_json.exists():
            return

        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            # 验证必需字段
            required_fields = ['id', 'version']
            for field in required_fields:
                if field not in meta:
                    self.errors.append(f"_meta.json缺少必需字段: {field}")
                else:
                    print(f"✓ _meta.json包含字段: {field}")

            # 验证version格式
            if 'version' in meta:
                version = meta['version']
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    self.warnings.append("version应使用语义化版本格式(x.y.z)")
                else:
                    print(f"✓ version格式正确: {version}")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json JSON格式错误: {e}")

    def print_results(self):
        """输出验证结果"""
        print("\n" + "=" * 50)
        if self.errors:
            print(f"❌ 验证失败，发现 {len(self.errors)} 个错误:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"⚠️  发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("✅ 所有验证通过!")

        print("=" * 50)


def main():
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = os.path.dirname(os.path.abspath(__file__))
        # 回到技能根目录
        skill_path = os.path.dirname(skill_path)

    validator = SkillValidator(skill_path)
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
