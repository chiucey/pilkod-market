#!/usr/bin/env python3
"""
技能验证脚本 - 验证SKILL.md和_meta.json的结构正确性
"""

import os
import json
import re
import sys
from pathlib import Path


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """
        执行完整验证

        Returns:
            是否通过验证
        """
        print(f"🔍 验证技能: {self.skill_path}")
        print("=" * 50)

        # 1. 检查目录结构
        self._check_directory_structure()

        # 2. 验证 SKILL.md
        self._validate_skill_md()

        # 3. 验证 _meta.json
        self._validate_meta_json()

        # 打印结果
        self._print_results()

        return len(self.errors) == 0

    def _check_directory_structure(self):
        """检查目录结构"""
        print("\n📁 检查目录结构...")

        if not self.skill_path.exists():
            self.errors.append(f"技能目录不存在: {self.skill_path}")
            return

        # 必须存在的文件
        required_files = ["SKILL.md", "_meta.json"]
        for file in required_files:
            file_path = self.skill_path / file
            if file_path.exists():
                print(f"  ✅ {file}")
            else:
                self.errors.append(f"缺少必需文件: {file}")

    def _validate_skill_md(self):
        """验证 SKILL.md"""
        print("\n📄 验证 SKILL.md...")

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')

        # 检查 frontmatter 是否在第一行
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 frontmatter (---) 开头")
        else:
            print("  ✅ Frontmatter 在文件开头")

        # 解析 frontmatter
        frontmatter = self._parse_frontmatter(content)
        if not frontmatter:
            self.errors.append("无法解析 frontmatter")
            return

        # 检查必需字段
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in frontmatter:
                self.errors.append(f"Frontmatter 缺少必需字段: {field}")
            else:
                print(f"  ✅ {field}: {frontmatter[field][:50]}...")

        # 检查 name 格式
        if "name" in frontmatter:
            name = frontmatter["name"]
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"name 格式不正确，应使用连字符格式: {name}")

        # 检查 description 触发短语
        if "description" in frontmatter:
            desc = frontmatter["description"]
            if not any(phrase in desc.lower() for phrase in ["当用户", "when", "use when"]):
                self.warnings.append("description 建议包含触发短语 (如 '当用户要求...' 或 'Use when...')")

    def _validate_meta_json(self):
        """验证 _meta.json"""
        print("\n⚙️ 验证 _meta.json...")

        meta_json = self.skill_path / "_meta.json"
        if not meta_json.exists():
            return

        try:
            data = json.loads(meta_json.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 解析失败: {e}")
            return

        # 检查必需字段
        required_fields = ["id", "version"]
        for field in required_fields:
            if field not in data:
                self.errors.append(f"_meta.json 缺少必需字段: {field}")
            else:
                print(f"  ✅ {field}: {data[field]}")

        # 检查 version 格式
        if "version" in data:
            version = data["version"]
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                self.warnings.append(f"version 格式建议使用语义化版本 (如 1.0.0): {version}")

    def _parse_frontmatter(self, content: str) -> dict:
        """解析 YAML frontmatter"""
        if not content.startswith('---'):
            return {}

        lines = content.split('\n')
        frontmatter = {}
        in_frontmatter = False
        frontmatter_lines = []

        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break

            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def _print_results(self):
        """打印验证结果"""
        print("\n" + "=" * 50)

        if self.errors:
            print(f"❌ 验证失败，发现 {len(self.errors)} 个错误:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("✅ 所有验证通过!")


def main():
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        # 默认验证当前目录
        skill_path = os.path.dirname(os.path.abspath(__file__))
        # 回到技能根目录
        skill_path = os.path.dirname(os.path.dirname(skill_path))

    validator = SkillValidator(skill_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()