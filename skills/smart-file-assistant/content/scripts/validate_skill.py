#!/usr/bin/env python3
"""
技能验证脚本 - 验证 SKILL.md 和目录结构是否符合规范
"""

import os
import sys
import json
import re
from pathlib import Path

class SkillValidator:
    def __init__(self, skill_path):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []

    def validate(self):
        """执行所有验证检查"""
        print(f"🔍 开始验证技能: {self.skill_path.name}")
        print("-" * 50)

        checks = [
            ("目录结构检查", self.check_directory_structure),
            ("SKILL.md 存在性", self.check_skill_md_exists),
            ("Frontmatter 检查", self.check_frontmatter),
            ("_meta.json 检查", self.check_meta_json),
            ("命名规范检查", self.check_naming_conventions),
            ("内容完整性检查", self.check_content_completeness),
        ]

        all_passed = True
        for name, check_func in checks:
            print(f"\n📋 {name}...")
            try:
                passed = check_func()
                if passed:
                    print(f"   ✅ 通过")
                else:
                    print(f"   ❌ 失败")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ 错误: {e}")
                self.errors.append(f"{name}: {e}")
                all_passed = False

        self.print_summary()
        return all_passed

    def check_directory_structure(self):
        """检查目录结构"""
        required_dirs = ['references']
        optional_dirs = ['scripts', 'assets']

        for dir_name in required_dirs:
            dir_path = self.skill_path / dir_name
            if not dir_path.exists():
                self.errors.append(f"缺少必需目录: {dir_name}")
                return False
        return True

    def check_skill_md_exists(self):
        """检查 SKILL.md 是否存在"""
        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            self.errors.append("缺少 SKILL.md 文件")
            return False
        return True

    def check_frontmatter(self):
        """检查 frontmatter 格式"""
        skill_md = self.skill_path / 'SKILL.md'
        content = skill_md.read_text(encoding='utf-8')

        # 检查 frontmatter 是否在第一行
        if not content.startswith('---'):
            self.errors.append("SKILL.md 必须以 --- 开头（frontmatter）")
            return False

        # 提取 frontmatter
        lines = content.split('\n')
        if len(lines) < 3:
            self.errors.append("Frontmatter 格式不完整")
            return False

        # 找到 frontmatter 结束标记
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx == -1:
            self.errors.append("Frontmatter 缺少结束标记 ---")
            return False

        frontmatter_text = '\n'.join(lines[1:end_idx])

        # 检查必需字段
        if 'name:' not in frontmatter_text:
            self.errors.append("Frontmatter 缺少 name 字段")
            return False

        if 'description:' not in frontmatter_text:
            self.errors.append("Frontmatter 缺少 description 字段")
            return False

        # 检查 name 格式（连字符）
        name_match = re.search(r'name:\s*([^\n]+)', frontmatter_text)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                self.warnings.append(f"name 应使用连字符格式: {name}")

        # 检查 description 是否包含触发短语
        desc_match = re.search(r'description:\s*>?\s*(.+?)(?=\n---|\n\w+:|$)', frontmatter_text, re.DOTALL)
        if desc_match:
            desc = desc_match.group(1)
            if 'when' not in desc.lower() and 'ask' not in desc.lower():
                self.warnings.append("description 建议包含触发短语（如 'Use when...'）")

        return True

    def check_meta_json(self):
        """检查 _meta.json 文件"""
        meta_file = self.skill_path / '_meta.json'
        if not meta_file.exists():
            self.errors.append("缺少 _meta.json 文件")
            return False

        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            # 检查必需字段
            required_fields = ['id', 'version']
            for field in required_fields:
                if field not in meta:
                    self.errors.append(f"_meta.json 缺少字段: {field}")
                    return False

            # 检查 version 格式
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                self.warnings.append(f"version 格式应为 x.y.z，当前: {meta['version']}")

        except json.JSONDecodeError as e:
            self.errors.append(f"_meta.json 格式错误: {e}")
            return False

        return True

    def check_naming_conventions(self):
        """检查命名规范"""
        # 文件夹名称应为小写+连字符
        folder_name = self.skill_path.name
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', folder_name):
            self.errors.append(f"文件夹名称应使用连字符格式: {folder_name}")
            return False

        return True

    def check_content_completeness(self):
        """检查内容完整性"""
        skill_md = self.skill_path / 'SKILL.md'
        content = skill_md.read_text(encoding='utf-8')

        # 检查是否有实际内容（不只是 frontmatter）
        lines = content.split('\n')
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        content_after_frontmatter = '\n'.join(lines[end_idx+1:]).strip()
        if len(content_after_frontmatter) < 100:
            self.warnings.append("SKILL.md 内容较少，可能不够完整")

        return True

    def print_summary(self):
        """打印验证摘要"""
        print("\n" + "=" * 50)
        print("📊 验证结果摘要")
        print("=" * 50)

        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")

        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ 所有检查通过！")
        elif not self.errors:
            print("\n✅ 核心检查通过，有轻微警告。")
        else:
            print("\n❌ 存在错误，需要修复后重新验证。")


def main():
    if len(sys.argv) < 2:
        print("用法: python validate_skill.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    validator = SkillValidator(skill_path)
    passed = validator.validate()

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
