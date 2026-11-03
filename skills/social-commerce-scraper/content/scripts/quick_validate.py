#!/usr/bin/env python3
"""
社交电商热销商品抓取技能 - 快速验证脚本
验证SKILL.md的frontmatter格式和目录结构
"""

import os
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def log_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def log_info(msg):
    print(f"{YELLOW}ℹ {msg}{RESET}")

def validate_frontmatter():
    """验证SKILL.md的frontmatter格式"""
    skill_md = SKILL_DIR / "SKILL.md"

    if not skill_md.exists():
        log_error("SKILL.md 文件不存在")
        return False

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在最前面
    if not content.startswith('---'):
        log_error("SKILL.md 必须以 --- 开头（frontmatter）")
        return False

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        log_error("无法解析frontmatter块")
        return False

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    missing_fields = []

    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            missing_fields.append(field)

    if missing_fields:
        log_error(f"frontmatter缺少必需字段: {', '.join(missing_fields)}")
        return False

    # 验证name格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            log_error(f"name '{name}' 格式不正确，应使用小写字母、数字、连字符")
            return False
        if name != SKILL_DIR.name:
            log_error(f"name '{name}' 应与目录名 '{SKILL_DIR.name}' 一致")
            return False

    log_success("frontmatter格式验证通过")
    return True

def validate_meta_json():
    """验证_meta.json文件"""
    meta_file = SKILL_DIR / "_meta.json"

    if not meta_file.exists():
        log_error("_meta.json 文件不存在")
        return False

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError:
        log_error("_meta.json 格式不正确（JSON解析失败）")
        return False

    required_fields = ['id', 'version']
    missing_fields = []

    for field in required_fields:
        if field not in meta:
            missing_fields.append(field)

    if missing_fields:
        log_error(f"_meta.json缺少必需字段: {', '.join(missing_fields)}")
        return False

    # 验证version格式
    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        log_error(f"version '{meta['version']}' 格式不正确，应为 x.y.z")
        return False

    log_success("_meta.json验证通过")
    return True

def validate_directory_structure():
    """验证目录结构"""
    required_dirs = []
    optional_dirs = ['scripts', 'references', 'assets']

    for dir_name in required_dirs:
        dir_path = SKILL_DIR / dir_name
        if not dir_path.exists():
            log_error(f"必需目录 '{dir_name}' 不存在")
            return False

    log_success("目录结构验证通过")
    return True

def validate_references():
    """验证references目录中的平台指南"""
    ref_dir = SKILL_DIR / "references"
    expected_files = ['xiaohongshu.md', 'douyin.md', 'bilibili.md']

    if not ref_dir.exists():
        log_info("references目录不存在，跳过验证")
        return True

    for filename in expected_files:
        file_path = ref_dir / filename
        if not file_path.exists():
            log_info(f"缺少参考文档: {filename}")

    log_success("references目录验证通过")
    return True

def main():
    print("=" * 50)
    print("社交电商热销商品抓取技能 - 验证")
    print("=" * 50)
    print()

    results = []

    print("[1] 验证frontmatter格式...")
    results.append(validate_frontmatter())
    print()

    print("[2] 验证_meta.json...")
    results.append(validate_meta_json())
    print()

    print("[3] 验证目录结构...")
    results.append(validate_directory_structure())
    print()

    print("[4] 验证references...")
    results.append(validate_references())
    print()

    print("=" * 50)
    if all(results):
        log_success("所有验证通过！")
        return 0
    else:
        log_error("部分验证失败，请修复后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
