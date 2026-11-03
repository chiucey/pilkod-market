#!/usr/bin/env python3
"""
A股分析预测系统 - 技能验证脚本
验证 SKILL.md 和 _meta.json 的格式和内容正确性
"""

import json
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md frontmatter 格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开头（---）"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 YAML frontmatter"

    frontmatter_text = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            return False, f"缺少必需字段: {field}"

    # 提取 name 值
    name_match = re.search(r'^name:\s*(.+?)\s*$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        # 检查 name 格式（连字符）
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name_value):
            return False, f"name 格式错误，应使用连字符格式: {name_value}"

    return True, "Frontmatter 验证通过"

def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 格式错误: {e}"

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"缺少必需字段: {field}"

    # 验证 id 是数字
    if not isinstance(meta['id'], int):
        return False, f"id 必须是整数: {meta['id']}"

    # 验证 version 格式
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"version 格式错误，应为 semver 格式: {version}"

    return True, "_meta.json 验证通过"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    skill_path = Path(skill_dir)

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = skill_path / file
        if not file_path.exists():
            return False, f"缺少必需文件: {file}"

    return True, "目录结构验证通过"

def validate_name_consistency(skill_dir, skill_md_path):
    """验证名称一致性"""
    # 从目录名获取
    dir_name = Path(skill_dir).name

    # 从 _meta.json 获取
    meta_path = Path(skill_dir) / '_meta.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 从 SKILL.md frontmatter 获取
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    frontmatter_text = frontmatter_match.group(1)
    name_match = re.search(r'^name:\s*(.+?)\s*$', frontmatter_text, re.MULTILINE)
    frontmatter_name = name_match.group(1).strip() if name_match else None

    # 检查一致性
    names = [dir_name, frontmatter_name]
    if len(set(names)) > 1:
        return False, f"名称不一致: 目录名={dir_name}, frontmatter={frontmatter_name}"

    return True, "名称一致性验证通过"

def main():
    skill_dir = "/workspace/temp-skills/a-share-analysis-system"
    skill_md_path = f"{skill_dir}/SKILL.md"
    meta_path = f"{skill_dir}/_meta.json"

    all_passed = True

    # 验证目录结构
    result, msg = validate_directory_structure(skill_dir)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    # 验证 meta.json
    result, msg = validate_meta_json(meta_path)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    # 验证 frontmatter
    result, msg = validate_frontmatter(skill_md_path)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    # 验证名称一致性
    result, msg = validate_name_consistency(skill_dir, skill_md_path)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    if all_passed:
        print("\n✓ 所有验证通过！")
        return 0
    else:
        print("\n✗ 验证失败，请修复以上问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
