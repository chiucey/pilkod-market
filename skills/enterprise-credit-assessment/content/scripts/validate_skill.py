#!/usr/bin/env python3
"""
企业资信评估技能验证脚本
验证 SKILL.md 结构和 frontmatter 格式
"""

import os
import re
import json
import sys

def validate_frontmatter(skill_path):
    """验证 frontmatter 格式"""
    skill_md_path = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md_path):
        return False, "SKILL.md 文件不存在"

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开始（---），而不是以 # 标题开头"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 YAML frontmatter，请检查格式"

    frontmatter_content = frontmatter_match.group(1)

    # 验证必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_content, re.MULTILINE):
            return False, f"frontmatter 缺少必需字段: {field}"

    # 验证 name 格式（连字符格式）
    name_match = re.search(r'^name:\s*(.+)', frontmatter_content, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name_value):
            return False, f"name 字段必须使用连字符格式（小写字母和数字）: {name_value}"

    # 验证 description 包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_content, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            return False, "description 太短，应包含详细的触发短语和功能描述"

    return True, "frontmatter 验证通过"

def validate_meta_json(skill_path):
    """验证 _meta.json 文件"""
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "_meta.json 文件不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 验证必需字段
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                return False, f"_meta.json 缺少必需字段: {field}"

        # 验证 version 格式
        version = meta.get('version', '')
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            return False, f"version 格式不正确，应为语义化版本（如 1.0.0）: {version}"

        return True, "_meta.json 验证通过"

    except json.JSONDecodeError as e:
        return False, f"_meta.json 格式错误: {e}"

def validate_directory_structure(skill_path):
    """验证目录结构"""
    # 目录名应与 skill name 一致
    dir_name = os.path.basename(skill_path)
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', dir_name):
        return False, f"目录名应使用连字符格式（小写字母和数字）: {dir_name}"

    return True, "目录结构验证通过"

def validate_paths_english_only(skill_path):
    """验证所有路径和文件名仅包含英文字符"""
    errors = []

    for root, dirs, files in os.walk(skill_path):
        for d in dirs:
            if not re.match(r'^[a-zA-Z0-9_\-]+$', d):
                errors.append(f"目录名包含非英文字符: {os.path.join(root, d)}")

        for f in files:
            if not re.match(r'^[a-zA-Z0-9_\-.]+$', f):
                errors.append(f"文件名包含非英文字符: {os.path.join(root, f)}")

    if errors:
        return False, "\n".join(errors)

    return True, "路径和名称验证通过（仅包含英文）"

def main():
    skill_path = "/workspace/temp-skills/enterprise-credit-assessment"

    print("=" * 50)
    print("企业资信评估技能 - 验证检查")
    print("=" * 50)

    all_passed = True

    # 1. 验证 frontmatter
    print("\n[1] 验证 frontmatter 格式...")
    passed, msg = validate_frontmatter(skill_path)
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 2. 验证 _meta.json
    print("\n[2] 验证 _meta.json...")
    passed, msg = validate_meta_json(skill_path)
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 3. 验证目录结构
    print("\n[3] 验证目录结构...")
    passed, msg = validate_directory_structure(skill_path)
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 4. 验证路径英文
    print("\n[4] 验证路径和名称（仅英文）...")
    passed, msg = validate_paths_english_only(skill_path)
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项，请修复后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
