#!/usr/bin/env python3
"""
C/C++ Developer Skill - Quick Validation Script
快速验证技能结构和内容的正确性
"""

import os
import sys
import json
import re
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def validate_skill(skill_path: str) -> bool:
    """验证技能的结构和内容"""
    skill_dir = Path(skill_path)
    results = []

    print(f"\n{'='*60}")
    print(f"验证技能: {skill_dir.name}")
    print('='*60)

    # 1. 检查 SKILL.md 是否存在
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print_error(f"SKILL.md 不存在于 {skill_path}")
        return False
    print_success(f"SKILL.md 存在")

    # 2. 读取并验证 frontmatter
    content = skill_md.read_text(encoding='utf-8')

    # 检查 frontmatter 位置（必须在第一行）
    lines = content.split('\n')
    if lines[0].strip() != '---':
        print_error("SKILL.md 必须以 frontmatter '---' 开头")
        return False
    print_success("Frontmatter 格式正确")

    # 提取 frontmatter
    try:
        end_idx = content.index('---', 3)  # 找到第二个 ---
        frontmatter_text = content[3:end_idx].strip()

        # 解析 YAML frontmatter
        name = None
        description = None

        for line in frontmatter_text.split('\n'):
            if line.startswith('name:'):
                name = line.split(':', 1)[1].strip()
            elif line.startswith('description:'):
                description = line.split(':', 1)[1].strip()

        if not name:
            print_error("Frontmatter 缺少 'name' 字段")
            return False
        print_success(f"名称验证通过: {name}")

        if not description:
            print_error("Frontmatter 缺少 'description' 字段")
            return False
        print_success("描述字段存在")

        # 检查描述是否包含触发短语
        if '当' not in description and 'when' not in description.lower():
            print_warning("建议在描述中添加触发短语（如'当用户请求...'）")

    except ValueError:
        print_error("Frontmatter 格式错误：未找到结束标记 '---'")
        return False

    # 3. 检查 _meta.json
    meta_file = skill_dir / "_meta.json"
    if not meta_file.exists():
        print_error("_meta.json 不存在")
        return False
    print_success("_meta.json 存在")

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        if 'id' not in meta:
            print_error("_meta.json 缺少 'id' 字段")
            return False
        if 'version' not in meta:
            print_error("_meta.json 缺少 'version' 字段")
            return False
        print_success(f"元数据验证通过: id={meta['id']}, version={meta['version']}")
    except json.JSONDecodeError as e:
        print_error(f"_meta.json JSON 格式错误: {e}")
        return False

    # 4. 检查目录结构
    expected_dirs = ['references', 'scripts']
    for dir_name in expected_dirs:
        dir_path = skill_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print_success(f"目录 {dir_name}/ 存在")
        else:
            print_warning(f"建议添加 {dir_name}/ 目录")

    # 5. 检查文件命名（确保英文）
    non_english_files = []
    for file_path in skill_dir.rglob('*'):
        if file_path.is_file():
            # 检查文件名是否包含非 ASCII 字符
            if not all(ord(c) < 128 for c in file_path.name):
                non_english_files.append(file_path.relative_to(skill_dir))

    if non_english_files:
        print_error(f"发现非英文文件名: {non_english_files}")
        return False
    print_success("所有文件名均为英文")

    # 6. 验证 SKILL.md 内容完整性
    required_sections = ['触发场景', '工作流程', '核心能力', '代码质量标准']
    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        print_warning(f"建议添加以下章节: {', '.join(missing_sections)}")
    else:
        print_success("核心章节完整")

    print(f"\n{'='*60}")
    print("验证完成")
    print('='*60)

    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
