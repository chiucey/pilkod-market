#!/usr/bin/env python3
"""
快速验证技能结构和文件完整性
"""

import os
import json
import re
import sys

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md 的 frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开头 (---)"

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0].strip() != '---':
        return False, "SKILL.md frontmatter 格式不正确"

    # 找到 frontmatter 结束
    frontmatter_end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end is None:
        return False, "SKILL.md frontmatter 未正确关闭"

    # 解析 frontmatter
    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            return False, f"缺少必需字段: {field}"

    # 提取 name 字段
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        folder_name = os.path.basename(os.path.dirname(skill_md_path))
        if name != folder_name:
            return False, f"name 字段 '{name}' 与文件夹名称 '{folder_name}' 不匹配"

    # 检查 markdown 标题不在 frontmatter 之前
    for i, line in enumerate(lines[:frontmatter_end]):
        if line.strip().startswith('#'):
            return False, f"markdown 标题不应出现在 frontmatter 中 (行 {i+1})"

    return True, "✓ Frontmatter 验证通过"

def validate_meta_json(meta_path):
    """验证 _meta.json"""
    if not os.path.exists(meta_path):
        return False, "缺少 _meta.json 文件"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 格式错误: {e}"

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"缺少必需字段: {field}"

    if not isinstance(meta['id'], (int, str)):
        return False, f"_meta.json id 必须是数字或字符串"

    if not re.match(r'^\d+\.\d+\.\d+$', str(meta['version'])):
        return False, f"_meta.json version 必须符合语义化版本格式 (如 1.0.0)"

    return True, "✓ _meta.json 验证通过"

def validate_skill_structure(skill_dir):
    """验证整体目录结构"""
    required = ['SKILL.md', '_meta.json']
    for item in required:
        path = os.path.join(skill_dir, item)
        if not os.path.exists(path):
            return False, f"缺少必需文件: {item}"

    # 检查可选目录
    optional_dirs = ['references', 'scripts', 'assets']
    existing = [d for d in optional_dirs if os.path.isdir(os.path.join(skill_dir, d))]

    return True, f"✓ 目录结构验证通过 (包含: {', '.join(existing) if existing else '无额外目录'})"

def main():
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(skill_dir)  # 回到技能根目录

    print(f"验证技能: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # 验证 frontmatter
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md):
        passed, msg = validate_frontmatter(skill_md)
        print(msg)
        if not passed:
            all_passed = False
    else:
        print("✗ 缺少 SKILL.md")
        all_passed = False

    # 验证 meta.json
    meta_json = os.path.join(skill_dir, '_meta.json')
    passed, msg = validate_meta_json(meta_json)
    print(msg)
    if not passed:
        all_passed = False

    # 验证目录结构
    passed, msg = validate_skill_structure(skill_dir)
    print(msg)
    if not passed:
        all_passed = False

    print("-" * 50)
    if all_passed:
        print("✅ 所有验证通过！")
        return 0
    else:
        print("❌ 验证失败，请修复以上问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
