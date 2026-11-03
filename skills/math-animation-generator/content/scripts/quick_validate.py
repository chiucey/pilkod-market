#!/usr/bin/env python3
"""
数学动画生成器 - 快速验证脚本
验证技能结构和frontmatter是否符合规范
"""

import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
META_JSON = SKILL_DIR / "_meta.json"

def validate_frontmatter():
    """验证SKILL.md的frontmatter格式"""
    if not SKILL_MD.exists():
        return False, "SKILL.md 文件不存在"

    with open(SKILL_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头"

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析frontmatter"

    frontmatter = frontmatter_match.group(1)

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return False, f"frontmatter 缺少必填字段: {field}"

    # 验证name格式（连字符）
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name必须使用连字符格式（小写字母、数字、连字符）: {name}"

    # 检查description包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            return False, "description 过短，应包含详细的触发短语"

    return True, "Frontmatter验证通过"

def validate_meta_json():
    """验证_meta.json的格式"""
    if not META_JSON.exists():
        return False, "_meta.json 文件不存在"

    import json

    try:
        with open(META_JSON, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON格式错误: {e}"

    # 检查必填字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json 缺少必填字段: {field}"

    # 验证id是整数
    if not isinstance(meta['id'], int):
        return False, "_meta.json 中 id 必须是整数"

    # 验证version格式
    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        return False, "_meta.json 中 version 必须符合语义化版本格式 (如 1.0.0)"

    return True, "_meta.json验证通过"

def validate_directory_structure():
    """验证目录结构"""
    required_dirs = []
    optional_dirs = ['scripts', 'references', 'assets']

    all_valid = True
    messages = []

    for dir_name in required_dirs:
        dir_path = SKILL_DIR / dir_name
        if not dir_path.exists():
            all_valid = False
            messages.append(f"缺少必需目录: {dir_name}")

    for dir_name in optional_dirs:
        dir_path = SKILL_DIR / dir_name
        if dir_path.exists():
            messages.append(f"✓ 找到可选目录: {dir_name}")

    if all_valid:
        messages.insert(0, "✓ 目录结构验证通过")
    else:
        messages.insert(0, "✗ 目录结构验证失败")

    return all_valid, "\n".join(messages)

def main():
    """运行所有验证"""
    print("=" * 50)
    print("数学动画生成器 - 技能验证")
    print("=" * 50)
    print()

    all_passed = True

    # 1. 验证frontmatter
    print("[1/3] 验证Frontmatter...")
    passed, msg = validate_frontmatter()
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed
    print()

    # 2. 验证_meta.json
    print("[2/3] 验证_meta.json...")
    passed, msg = validate_meta_json()
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed
    print()

    # 3. 验证目录结构
    print("[3/3] 验证目录结构...")
    passed, msg = validate_directory_structure()
    for line in msg.split('\n'):
        print(f"    {line}")
    all_passed = all_passed and passed
    print()

    # 总结
    print("=" * 50)
    if all_passed:
        print("✓ 所有验证通过！技能结构符合规范。")
        return 0
    else:
        print("✗ 验证失败，请修复上述问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
