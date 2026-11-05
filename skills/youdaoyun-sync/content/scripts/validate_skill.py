#!/usr/bin/env python3
"""
有道云笔记同步技能验证器
检查 SKILL.md 和元数据的有效性
"""

import json
import os
import re
import sys
from pathlib import Path


class SkillValidator:
    """技能验证器"""

    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir)
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """执行所有验证"""
        print("=" * 50)
        print("有道云笔记同步技能验证")
        print("=" * 50)

        checks = [
            ("目录结构", self.check_directory_structure),
            ("SKILL.md 存在", self.check_skill_md_exists),
            ("Frontmatter 格式", self.check_frontmatter),
            ("_meta.json 格式", self.check_meta_json),
            ("脚本存在", self.check_scripts_exist),
            ("命名规范", self.check_naming),
        ]

        all_passed = True
        for name, check_func in checks:
            print(f"\n检查: {name}...", end=" ")
            try:
                result = check_func()
                if result:
                    print("✅ 通过")
                else:
                    print("❌ 失败")
                    all_passed = False
            except Exception as e:
                print(f"❌ 错误: {e}")
                all_passed = False

        # 报告问题
        if self.warnings:
            print("\n⚠️ 警告:")
            for w in self.warnings:
                print(f"  - {w}")

        if self.errors:
            print("\n❌ 错误:")
            for e in self.errors:
                print(f"  - {e}")

        print("\n" + "=" * 50)
        if all_passed:
            print("✅ 所有验证通过!")
        else:
            print("❌ 验证失败，请修复上述问题")

        return all_passed

    def check_directory_structure(self) -> bool:
        """检查目录结构"""
        required_dirs = ["scripts"]
        for d in required_dirs:
            path = self.skill_dir / d
            if not path.exists():
                self.errors.append(f"缺少目录: {d}")
                return False
        return True

    def check_skill_md_exists(self) -> bool:
        """检查 SKILL.md 是否存在"""
        path = self.skill_dir / "SKILL.md"
        if not path.exists():
            self.errors.append("SKILL.md 文件不存在")
            return False
        return True

    def check_frontmatter(self) -> bool:
        """检查 frontmatter 格式"""
        path = self.skill_dir / "SKILL.md"
        content = path.read_text(encoding='utf-8')

        # 检查是否以 --- 开头
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 --- 开头")
            return False

        # 提取 frontmatter
        lines = content.split('\n')
        end_index = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_index = i
                break

        if end_index == -1:
            self.errors.append("SKILL.md frontmatter 未正确闭合")
            return False

        frontmatter_text = '\n'.join(lines[1:end_index])

        # 检查必需字段
        required_fields = ['name', 'description']
        for field in required_fields:
            if not re.search(f'^{field}:', frontmatter_text, re.MULTILINE):
                self.errors.append(f"Frontmatter 缺少必需字段: {field}")

        # 检查 name 格式
        name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                self.errors.append(f"name 格式错误 (应使用小写字母、数字、连字符): {name}")
                return False
            if name != self.skill_dir.name:
                self.warnings.append(f"name ({name}) 与目录名 ({self.skill_dir.name}) 不一致")

        return len(self.errors) == 0

    def check_meta_json(self) -> bool:
        """检查 _meta.json 格式"""
        path = self.skill_dir / "_meta.json"
        if not path.exists():
            self.errors.append("_meta.json 文件不存在")
            return False

        try:
            with open(path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 格式错误: {e}")
            return False

        # 检查必需字段
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                self.errors.append(f"_meta.json 缺少必需字段: {field}")

        # 检查版本格式
        if 'version' in meta:
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                self.errors.append(f"version 格式错误 (应为语义化版本如 1.0.0): {meta['version']}")

        return len(self.errors) == 0

    def check_scripts_exist(self) -> bool:
        """检查脚本是否存在"""
        scripts_dir = self.skill_dir / "scripts"
        required_scripts = ["sync_files.py"]

        for script in required_scripts:
            path = scripts_dir / script
            if not path.exists():
                self.errors.append(f"缺少脚本: {script}")
                return False

        return True

    def check_naming(self) -> bool:
        """检查命名规范"""
        # 检查文件夹名称
        folder_name = self.skill_dir.name
        if not re.match(r'^[a-z0-9-]+$', folder_name):
            self.errors.append(f"文件夹名称格式错误: {folder_name}")
            return False

        # 检查所有文件名是否为英文
        for file_path in self.skill_dir.rglob('*'):
            if file_path.is_file():
                file_name = file_path.name
                # 检查是否有非 ASCII 字符
                if not file_name.isascii():
                    self.warnings.append(f"文件名包含非 ASCII 字符: {file_name}")

        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="验证有道云同步技能")
    parser.add_argument("--path", default=".", help="技能目录路径")
    args = parser.parse_args()

    validator = SkillValidator(args.path)
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
