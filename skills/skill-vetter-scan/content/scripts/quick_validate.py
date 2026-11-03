#!/usr/bin/env python3
"""
技能验证器 (Quick Validator)
验证技能目录结构是否符合规范
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class SkillValidator:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors = []
        self.warnings = []
        self.passed = []

    def validate_all(self) -> bool:
        """执行所有验证"""
        print(f"🔍 验证技能: {self.skill_path}\n")

        self.check_directory_structure()
        self.check_skill_md()
        self.check_meta_json()
        self.validate_naming()
        self.validate_frontmatter()

        return len(self.errors) == 0

    def check_directory_structure(self):
        """检查目录结构"""
        if not self.skill_path.exists():
            self.errors.append(f"❌ 技能目录不存在: {self.skill_path}")
            return

        if not self.skill_path.is_dir():
            self.errors.append(f"❌ 路径不是目录: {self.skill_path}")
            return

        self.passed.append("✅ 目录结构正确")

    def check_skill_md(self):
        """检查SKILL.md文件"""
        skill_md = self.skill_path / "SKILL.md"

        if not skill_md.exists():
            self.errors.append("❌ SKILL.md 文件不存在")
            return

        if not skill_md.is_file():
            self.errors.append("❌ SKILL.md 不是文件")
            return

        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查frontmatter
        if not content.startswith('---'):
            self.errors.append("❌ SKILL.md 必须以 frontmatter (---) 开头")

        # 检查frontmatter完整性
        if content.startswith('---'):
            frontmatter_end = content.find('---', 3)
            if frontmatter_end == -1:
                self.errors.append("❌ Frontmatter 未正确关闭")
            else:
                self.passed.append("✅ Frontmatter 格式正确")

        # 检查是否在frontmatter前有markdown标题
        lines = content.split('\n')
        frontmatter_end_line = 0
        in_frontmatter = False
        for i, line in enumerate(lines[:10]):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    frontmatter_end_line = i
                    break
            if not in_frontmatter and line.startswith('#'):
                self.errors.append(f"❌ SKILL.md 在 frontmatter 之前有标题 (第{i+1}行)")
                break
        else:
            # 如果循环正常结束（没找到第二个---），frontmatter还没结束
            if in_frontmatter:
                pass  # frontmatter还没正确结束，这个在其他检查中处理

        self.passed.append("✅ SKILL.md 存在且格式正确")

    def check_meta_json(self):
        """检查_meta.json文件"""
        meta_json = self.skill_path / "_meta.json"

        if not meta_json.exists():
            self.warnings.append("⚠️ _meta.json 文件不存在")
            return

        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            # 检查必需字段
            if 'id' not in meta:
                self.errors.append("❌ _meta.json 缺少 'id' 字段")

            if 'version' not in meta:
                self.errors.append("❌ _meta.json 缺少 'version' 字段")

            # 验证id是数字
            if 'id' in meta:
                try:
                    int(meta['id'])
                    self.passed.append("✅ _meta.json id 格式正确")
                except ValueError:
                    self.errors.append("❌ _meta.json id 必须是数字")

            # 验证version格式
            if 'version' in meta:
                if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                    self.warnings.append("⚠️ version 建议使用语义化版本格式 (x.y.z)")

        except json.JSONDecodeError as e:
            self.errors.append(f"❌ _meta.json 格式错误: {e}")

    def validate_naming(self):
        """验证命名规范"""
        # 文件夹名称应为连字符格式
        folder_name = self.skill_path.name
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', folder_name):
            self.warnings.append(f"⚠️ 文件夹名称 '{folder_name}' 建议使用连字符格式 (kebab-case)")

        # 检查SKILL.md中的name字段
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取frontmatter
            if content.startswith('---'):
                end = content.find('---', 3)
                if end != -1:
                    frontmatter = content[3:end]
                    if 'name:' in frontmatter:
                        name_match = re.search(r'name:\s*([^\n]+)', frontmatter)
                        if name_match:
                            skill_name = name_match.group(1).strip()
                            if skill_name != folder_name:
                                self.warnings.append(f"⚠️ SKILL.md 中的 name ('{skill_name}') 与文件夹名称 ('{folder_name}') 不一致")

    def validate_frontmatter(self):
        """验证frontmatter内容"""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            return

        end = content.find('---', 3)
        if end == -1:
            return

        frontmatter = content[3:end]

        # 检查必需字段
        if 'name:' not in frontmatter:
            self.errors.append("❌ Frontmatter 缺少 'name' 字段")

        if 'description:' not in frontmatter:
            self.errors.append("❌ Frontmatter 缺少 'description' 字段")

        # 验证description长度
        desc_match = re.search(r'description:\s*([^\n]+(?:\n[^\n]+)*)', frontmatter)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 10:
                self.warnings.append("⚠️ description 过短，建议至少10个字符")

        # 检查description中是否有触发短语
        trigger_phrases = [
            '当用户要求', '当用户请求', 'Use when',
            '用于', '适用于', '处理'
        ]
        if not any(phrase in frontmatter for phrase in trigger_phrases):
            self.warnings.append("⚠️ description 建议包含触发短语 (如 '当用户要求...' 或 'Use when...')")

    def print_results(self):
        """打印验证结果"""
        print("="*60)

        if self.passed:
            print("\n✅ 通过的检查:")
            for item in self.passed:
                print(f"  {item}")

        if self.warnings:
            print("\n⚠️  警告:")
            for item in self.warnings:
                print(f"  {item}")

        if self.errors:
            print("\n❌ 错误:")
            for item in self.errors:
                print(f"  {item}")

        print("\n" + "="*60)

        if len(self.errors) == 0:
            print("✅ 验证通过！")
            return True
        else:
            print(f"❌ 验证失败 ({len(self.errors)} 个错误)")
            return False


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 验证当前技能目录
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    validator = SkillValidator(skill_path)
    success = validator.validate_all()
    validator.print_results()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
