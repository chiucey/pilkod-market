#!/usr/bin/env python3
"""
LaTeX to Word 技能验证脚本
验证技能结构和内容是否符合规范
"""

import json
import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 frontmatter 格式和内容"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 frontmatter --- 开头"

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "缺少 frontmatter 结束标记 ---"

    # 解析 frontmatter
    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            return False, f"缺少必填字段: {field}"

    # 验证 name 格式
    name = frontmatter.get('name', '')
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"name 字段必须使用连字符格式（小写字母、数字、连字符），当前: {name}"

    if len(name) > 64:
        return False, f"name 字段长度不能超过 64 字符，当前: {len(name)}"

    # 验证 description 包含触发短语
    description = frontmatter.get('description', '')
    trigger_keywords = ['.tex', '.docx', 'LaTeX', 'Word', '转换']
    has_trigger = any(keyword in description for keyword in trigger_keywords)
    if not has_trigger:
        return False, "description 应包含触发关键词（如 .tex, .docx, LaTeX, Word, 转换）"

    return True, "Frontmatter 验证通过"

def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    if not os.path.exists(meta_path):
        return False, "缺少 _meta.json 文件"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 检查必填字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json 缺少必填字段: {field}"

    # 验证 id 是整数
    if not isinstance(meta['id'], int):
        return False, f"_meta.json 的 id 必须是整数，当前: {type(meta['id'])}"

    # 验证 version 格式
    version = meta.get('version', '')
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"_meta.json 的 version 必须符合语义化版本格式（如 1.0.0），当前: {version}"

    return True, "_meta.json 验证通过"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            return False, f"缺少必填文件: {file}"

    return True, "目录结构验证通过"

def main():
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    if skill_dir.endswith('/scripts'):
        skill_dir = os.path.dirname(skill_dir)

    print(f"验证技能: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # 验证目录结构
    passed, msg = validate_directory_structure(skill_dir)
    print(f"📁 目录结构: {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 验证 frontmatter
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    passed, msg = validate_frontmatter(skill_md_path)
    print(f"📝 Frontmatter: {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 验证 _meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    passed, msg = validate_meta_json(meta_path)
    print(f"⚙️  _meta.json: {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✅ 所有验证通过！")
        return 0
    else:
        print("❌ 验证失败，请修复以上问题")
        return 1

if __name__ == '__main__':
    sys.exit(main())
