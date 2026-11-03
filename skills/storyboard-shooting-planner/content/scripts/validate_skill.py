#!/usr/bin/env python3
"""
分镜拍摄规划技能验证脚本
验证 SKILL.md 的 frontmatter 和结构是否符合规范
"""

import os
import sys
import json
import re

def validate_frontmatter(skill_path):
    """验证 frontmatter 格式"""
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        return False, "SKILL.md 文件不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头（frontmatter 开始）"

    # 检查 frontmatter 结束
    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        return False, "frontmatter 缺少结束标记 ---"

    frontmatter_text = content[3:frontmatter_end].strip()

    # 检查必需字段
    if 'name:' not in frontmatter_text:
        return False, "frontmatter 缺少 name 字段"

    if 'description:' not in frontmatter_text:
        return False, "frontmatter 缺少 description 字段"

    # 提取 name 值
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        # 检查 name 格式（连字符格式）
        if ' ' in name_value:
            return False, f"name 字段应使用连字符格式，当前值包含空格: {name_value}"

    # 检查 frontmatter 之后是否有内容
    rest_content = content[frontmatter_end+3:].strip()
    if not rest_content:
        return False, "frontmatter 之后缺少技能内容"

    return True, "Frontmatter 验证通过"

def validate_meta(skill_path):
    """验证 _meta.json 格式"""
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "_meta.json 文件不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError:
        return False, "_meta.json 格式无效（非 JSON）"

    # 检查必需字段
    if 'id' not in meta:
        return False, "_meta.json 缺少 id 字段"

    if 'version' not in meta:
        return False, "_meta.json 缺少 version 字段"

    # 验证 id 是整数
    if not isinstance(meta['id'], int):
        return False, "_meta.json 的 id 必须是整数"

    return True, "_meta.json 验证通过"

def validate_structure(skill_path):
    """验证目录结构"""
    required_files = ["SKILL.md", "_meta.json"]

    for filename in required_files:
        filepath = os.path.join(skill_path, filename)
        if not os.path.exists(filepath):
            return False, f"缺少必需文件: {filename}"

    return True, "目录结构验证通过"

def main():
    skill_path = os.path.dirname(os.path.abspath(__file__))
    # 返回到技能根目录
    skill_path = os.path.dirname(skill_path)

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 验证结构
    passed, msg = validate_structure(skill_path)
    print(f"{'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 验证 frontmatter
    passed, msg = validate_frontmatter(skill_path)
    print(f"{'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 验证 _meta.json
    passed, msg = validate_meta(skill_path)
    print(f"{'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 存在验证失败项")
        return 1

if __name__ == "__main__":
    sys.exit(main())
