#!/usr/bin/env python3
"""
Email Assistant Skill Validator
验证邮件助手技能的结构和内容完整性
"""

import os
import sys
import json
import re

def validate_frontmatter(skill_path):
    """验证 SKILL.md frontmatter 格式"""
    skill_file = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_file):
        return False, "SKILL.md 文件不存在"

    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter (---) 开头"

    # 解析 frontmatter
    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        return False, "YAML frontmatter 未正确闭合"

    frontmatter_text = content[3:frontmatter_end].strip()

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = rf'^{field}:\s*.+$'
        if not re.search(pattern, frontmatter_text, re.MULTILINE):
            return False, f"Frontmatter 缺少必需字段: {field}"

    # 验证 name 格式（连字符、小写）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            return False, "name 字段必须为小写字母、数字和连字符"

    return True, "Frontmatter 验证通过"

def validate_meta_json(skill_path):
    """验证 _meta.json 格式"""
    meta_file = os.path.join(skill_path, '_meta.json')

    if not os.path.exists(meta_file):
        return False, "_meta.json 文件不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                return False, f"_meta.json 缺少必需字段: {field}"

        if not isinstance(meta['id'], int):
            return False, "_meta.json 中 id 必须是整数"

        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            return False, "_meta.json 中 version 必须符合语义化版本格式 (x.y.z)"

        return True, "_meta.json 验证通过"

    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 解析错误: {e}"

def validate_file_structure(skill_path):
    """验证文件结构"""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_path, file)
        if not os.path.exists(file_path):
            return False, f"缺少必需文件: {file}"

    return True, "文件结构验证通过"

def main():
    if len(sys.argv) < 2:
        skill_path = '/workspace/temp-skills/email-assistant'
    else:
        skill_path = sys.argv[1]

    print(f"验证技能: {skill_path}")
    print("=" * 50)

    all_passed = True

    # 验证文件结构
    passed, message = validate_file_structure(skill_path)
    status = "✓" if passed else "✗"
    print(f"[{status}] 文件结构: {message}")
    if not passed: all_passed = False

    # 验证 frontmatter
    passed, message = validate_frontmatter(skill_path)
    status = "✓" if passed else "✗"
    print(f"[{status}] Frontmatter: {message}")
    if not passed: all_passed = False

    # 验证 meta.json
    passed, message = validate_meta_json(skill_path)
    status = "✓" if passed else "✗"
    print(f"[{status}] _meta.json: {message}")
    if not passed: all_passed = False

    print("=" * 50)
    if all_passed:
        print("✅ 所有验证通过!")
        sys.exit(0)
    else:
        print("❌ 验证失败，请修复上述问题")
        sys.exit(1)

if __name__ == '__main__':
    main()