#!/usr/bin/env python3
"""
auto-driving-test-qa 技能验证脚本
验证 SKILL.md 和 _meta.json 的结构和内容是否符合规范
"""

import json
import os
import re
import sys
from pathlib import Path

# ANSI 颜色码
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")


def print_info(msg):
    print(f"{BOLD}ℹ {msg}{RESET}")


def get_folder_name(path):
    """获取文件夹名称"""
    return Path(path).absolute().name


class SkillValidator:
    def __init__(self, skill_dir: str):
        self.skill_dir = Path(skill_dir).absolute()
        self.errors = []
        self.warnings = []

    def validate_all(self) -> bool:
        """执行所有验证检查"""
        folder_name = self.skill_dir.name
        print_info(f"开始验证技能: {folder_name}")
        print("=" * 50)

        checks = [
            ("目录结构检查", self.check_directory_structure),
            ("Frontmatter检查", self.check_frontmatter),
            ("_meta.json检查", self.check_meta_json),
            ("SKILL.md内容检查", self.check_skill_content),
            ("命名规范检查", self.check_naming_conventions),
        ]

        all_passed = True
        for name, check_func in checks:
            print(f"\n[B] {name}...[/B]")
            if not check_func():
                all_passed = False

        self.print_summary(all_passed)
        return all_passed

    def check_directory_structure(self) -> bool:
        """检查目录结构"""
        required_files = ['SKILL.md', '_meta.json']
        missing = []

        for f in required_files:
            if not (self.skill_dir / f).exists():
                missing.append(f)

        if missing:
            for f in missing:
                print_error(f"缺少必需文件: {f}")
            return False

        print_success("目录结构完整")
        return True

    def check_frontmatter(self) -> bool:
        """检查SKILL.md的frontmatter"""
        skill_file = self.skill_dir / 'SKILL.md'
        content = skill_file.read_text(encoding='utf-8')

        # 检查frontmatter是否在第一行
        if not content.strip().startswith('---'):
            print_error("SKILL.md 必须以 frontmatter (---) 开始，第一行不能是 markdown 标题")
            return False

        # 提取frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            print_error("无法解析 frontmatter，格式应为 --- ... ---")
            return False

        frontmatter_text = fm_match.group(1)

        # 检查必需字段
        required_fields = ['name', 'description']
        missing = []
        for field in required_fields:
            if not re.search(rf'^{field}:\s*.+', frontmatter_text, re.MULTILINE):
                missing.append(field)

        if missing:
            for f in missing:
                print_error(f"frontmatter缺少必需字段: {f}")
            return False

        # 检查name字段格式
        name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
        folder_name = self.skill_dir.name
        if name_match:
            name_value = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name_value):
                print_error(f"name字段必须使用连字符格式(小写+中划线)，当前值: {name_value}")
                return False
            if name_value != folder_name:
                print_warning(f"name字段({name_value})与文件夹名称({folder_name})不一致")

        print_success("Frontmatter格式正确")
        return True

    def check_meta_json(self) -> bool:
        """检查_meta.json文件"""
        meta_file = self.skill_dir / '_meta.json'

        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            print_error(f"_meta.json 解析失败: {e}")
            return False

        # 检查必需字段
        required_fields = ['id', 'version']
        missing = []
        for field in required_fields:
            if field not in meta:
                missing.append(field)

        if missing:
            for f in missing:
                print_error(f"_meta.json缺少必需字段: {f}")
            return False

        # 验证id是整数
        if not isinstance(meta['id'], int):
            print_error("_meta.json的id必须是整数")
            return False

        # 验证version格式
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            print_error(f"version必须遵循语义化版本格式(x.y.z)，当前值: {version}")
            return False

        print_success("_meta.json格式正确")
        return True

    def check_skill_content(self) -> bool:
        """检查SKILL.md内容完整性"""
        skill_file = self.skill_dir / 'SKILL.md'
        content = skill_file.read_text(encoding='utf-8')

        # 移除frontmatter后检查内容
        fm_end = content.find('---', 3) + 3
        body = content[fm_end:].strip()

        if len(body) < 500:
            print_warning("SKILL.md内容较少，可能不够详细")

        # 检查关键章节
        essential_sections = [
            '角色定义',  # 或 role/角色
            '专业领域',  # 或能力/核心能力
        ]

        found_sections = []
        for section in essential_sections:
            if section in body:
                found_sections.append(section)

        if not found_sections:
            print_warning("未找到明确的角色/能力定义章节")

        # 检查是否包含示例
        if '示例' in body or 'Example' in body.lower():
            print_success("包含示例内容")
        else:
            print_warning("建议添加问答示例以提升实用性")

        print_success("SKILL.md内容结构完整")
        return True

    def check_naming_conventions(self) -> bool:
        """检查命名规范"""
        folder_name = self.skill_dir.name
        if not re.match(r'^[a-z0-9-]+$', folder_name):
            print_error(f"文件夹名称必须使用连字符格式(小写+中划线)，当前: {folder_name}")
            return False

        print_success("命名规范检查通过")
        return True

    def print_summary(self, all_passed: bool):
        """打印验证总结"""
        print("\n" + "=" * 50)
        if all_passed:
            print_success("所有验证检查通过!")
        else:
            print_error("验证失败，请修复上述错误")
        print("=" * 50)


def main():
    if len(sys.argv) < 2:
        skill_dir = Path(__file__).parent.parent
    else:
        skill_dir = Path(sys.argv[1])

    if not skill_dir.exists():
        print_error(f"技能目录不存在: {skill_dir}")
        sys.exit(1)

    validator = SkillValidator(skill_dir)
    passed = validator.validate_all()

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()