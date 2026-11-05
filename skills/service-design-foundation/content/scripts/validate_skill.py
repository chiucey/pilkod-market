#!/usr/bin/env python3
"""
服务设计基础技能验证脚本
验证 SKILL.md 和 _meta.json 的完整性和正确性
"""

import os
import re
import json
import sys
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f" {msg}")
    print(f"{'='*60}{Colors.END}\n")

def validate_frontmatter(skill_path):
    """验证 SKILL.md frontmatter"""
    results = {"passed": [], "failed": []}

    # 检查文件是否存在
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        print_error(f"SKILL.md 不存在: {skill_file}")
        return False

    content = skill_file.read_text(encoding='utf-8')

    # 检查1: frontmatter 是否在第一行
    if not content.strip().startswith('---'):
        print_error("Frontmatter 必须从文件第一行开始")
        results["failed"].append("frontmatter_position")
    else:
        print_success("Frontmatter 位于文件开头")
        results["passed"].append("frontmatter_position")

    # 提取 frontmatter
    try:
        frontmatter_end = content.index('---', 3)  # 找第二个 ---
        frontmatter_text = content[3:frontmatter_end].strip()
    except ValueError:
        print_error("Frontmatter 格式错误：缺少结束标记 ---")
        return False

    # 检查2: 必须包含 name 字段
    if not re.search(r'^name:\s*.+$', frontmatter_text, re.MULTILINE):
        print_error("Frontmatter 必须包含 'name' 字段")
        results["failed"].append("name_field")
    else:
        print_success("包含 'name' 字段")
        results["passed"].append("name_field")

    # 检查3: 必须包含 description 字段
    if not re.search(r'^description:\s*.+$', frontmatter_text, re.MULTILINE):
        print_error("Frontmatter 必须包含 'description' 字段")
        results["failed"].append("description_field")
    else:
        print_success("包含 'description' 字段")
        results["passed"].append("description_field")

    # 检查4: name 格式（连字符）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if ' ' in name:
            print_error(f"name 应使用连字符格式，当前: '{name}'")
            results["failed"].append("name_format")
        else:
            print_success(f"name 格式正确: '{name}'")
            results["passed"].append("name_format")

    # 检查5: description 应包含触发短语
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        trigger_phrases = ['当用户', '使用时', '适用于', '触发']
        if any(phrase in desc for phrase in trigger_phrases):
            print_success("description 包含触发短语")
            results["passed"].append("trigger_phrase")
        else:
            print_error("description 应包含触发短语（如：'当用户...'）")
            results["failed"].append("trigger_phrase")

    # 检查6: frontmatter 之后不能直接是标题
    main_content_start = frontmatter_end + 3
    remaining = content[main_content_start:].strip()
    if remaining.startswith('# '):
        print_success("主内容以标题开始")
        results["passed"].append("content_starts_with_title")
    else:
        print_info("主内容可能不以标题开始")

    return len(results["failed"]) == 0

def validate_meta(skill_path):
    """验证 _meta.json"""
    results = {"passed": [], "failed": []}

    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        print_error(f"_meta.json 不存在: {meta_file}")
        return False

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print_error(f"_meta.json JSON 格式错误: {e}")
        return False

    # 检查1: 必须包含 id
    if "id" not in meta:
        print_error("_meta.json 必须包含 'id' 字段")
        results["failed"].append("id_field")
    else:
        print_success("包含 'id' 字段")
        results["passed"].append("id_field")

    # 检查2: 必须包含 version
    if "version" not in meta:
        print_error("_meta.json 必须包含 'version' 字段")
        results["failed"].append("version_field")
    else:
        print_success("包含 'version' 字段")
        results["passed"].append("version_field")

    # 检查3: version 格式（语义化版本）
    if "version" in meta:
        version = meta["version"]
        if re.match(r'^\d+\.\d+\.\d+$', version):
            print_success(f"version 格式正确: {version}")
            results["passed"].append("version_format")
        else:
            print_error(f"version 应使用语义化格式 (x.y.z)，当前: {version}")
            results["failed"].append("version_format")

    return len(results["failed"]) == 0

def validate_structure(skill_path):
    """验证目录结构"""
    results = {"passed": [], "failed": []}

    skill_name = skill_path.name

    # 检查目录名称
    if ' ' in skill_name:
        print_error(f"目录名称应使用连字符: '{skill_name}'")
        results["failed"].append("dir_name_format")
    else:
        print_success(f"目录名称格式正确: '{skill_name}'")
        results["passed"].append("dir_name_format")

    # 检查 SKILL.md 存在
    if (skill_path / "SKILL.md").exists():
        print_success("SKILL.md 存在")
        results["passed"].append("skill_file")
    else:
        print_error("SKILL.md 不存在")
        results["failed"].append("skill_file")

    # 检查 _meta.json 存在
    if (skill_path / "_meta.json").exists():
        print_success("_meta.json 存在")
        results["passed"].append("meta_file")
    else:
        print_error("_meta.json 不存在")
        results["failed"].append("meta_file")

    # 检查可选目录
    for optional_dir in ["scripts", "references", "assets"]:
        if (skill_path / optional_dir).exists():
            print_info(f"可选目录 '{optional_dir}' 存在")

    return len(results["failed"]) == 0

def validate_content(skill_path):
    """验证 SKILL.md 内容完整性"""
    results = {"passed": [], "failed": [], "warnings": []}

    skill_file = skill_path / "SKILL.md"
    content = skill_file.read_text(encoding='utf-8')

    # 必须包含的核心章节
    required_sections = [
        ("双钻石", "双钻石模型"),
        ("服务蓝图", "服务蓝图"),
        ("用户旅程", "用户旅程图"),
        ("设计原则", "设计原则"),
    ]

    for section_name, display_name in required_sections:
        if section_name in content:
            print_success(f"包含章节: {display_name}")
            results["passed"].append(f"section_{section_name}")
        else:
            print_error(f"缺少核心章节: {display_name}")
            results["failed"].append(f"section_{section_name}")

    # 建议包含的内容
    recommended = [
        ("工具", "设计工具"),
        ("检查清单", "检查清单"),
        ("术语", "术语表"),
        ("交付物", "交付物"),
    ]

    for keyword, display_name in recommended:
        if keyword in content:
            print_success(f"包含内容: {display_name}")
        else:
            print_info(f"建议添加: {display_name}")
            results["warnings"].append(f"recommend_{keyword}")

    return len(results["failed"]) == 0

def main():
    skill_path = Path(__file__).parent.parent

    print_header("服务设计基础技能 - 验证报告")
    print_info(f"技能路径: {skill_path}")

    all_passed = True

    print_header("1. 结构验证")
    if not validate_structure(skill_path):
        all_passed = False

    print_header("2. Frontmatter 验证")
    if not validate_frontmatter(skill_path):
        all_passed = False

    print_header("3. _meta.json 验证")
    if not validate_meta(skill_path):
        all_passed = False

    print_header("4. 内容完整性验证")
    if not validate_content(skill_path):
        all_passed = False

    print_header("验证结果")
    if all_passed:
        print_success("所有验证通过！技能结构完整。")
        return 0
    else:
        print_error("部分验证未通过，请修复后重新验证。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
