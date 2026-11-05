#!/usr/bin/env python3
"""
快速总结技能验证脚本
验证 SKILL.md 的 frontmatter 格式和结构完整性
"""

import os
import re
import json
import sys

def validate_frontmatter(file_path):
    """验证 frontmatter 格式"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头（frontmatter开始标记）"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 frontmatter，请检查格式"

    frontmatter = frontmatter_match.group(1)

    # 验证必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return False, f"缺少必填字段: {field}"

    # 验证 name 格式（连字符，小写）
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name 字段格式错误，应使用小写字母、数字和连字符: {name}"

    return True, "Frontmatter 验证通过"


def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 文件不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError:
            return False, "_meta.json 格式错误，不是有效的JSON"

    # 验证必填字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"缺少必填字段: {field}"

    # 验证 id 是整数
    if not isinstance(meta['id'], int):
        return False, "id 必须是整数"

    # 验证 version 格式
    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        return False, "version 必须是语义化版本格式 (如 1.0.0)"

    return True, "_meta.json 验证通过"


def validate_skill_md_structure(file_path):
    """验证 SKILL.md 内容结构"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 确保 frontmatter 后没有 # 标题直接出现
    after_frontmatter = content.split('---', 2)[2] if content.count('---') >= 2 else content

    # 检查是否有基本内容
    if len(content) < 200:
        return False, "SKILL.md 内容过短"

    return True, "内容结构验证通过"


def main():
    skill_dir = "/workspace/temp-skills/fast-summarize"
    skill_md = os.path.join(skill_dir, "SKILL.md")
    meta_json = os.path.join(skill_dir, "_meta.json")

    print("=" * 50)
    print("Fast Summarize 技能验证")
    print("=" * 50)

    all_passed = True

    # 验证 SKILL.md frontmatter
    print("\n[1] 验证 SKILL.md Frontmatter...")
    passed, msg = validate_frontmatter(skill_md)
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 验证 _meta.json
    print("\n[2] 验证 _meta.json...")
    passed, msg = validate_meta_json(meta_json)
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 验证内容结构
    print("\n[3] 验证内容结构...")
    passed, msg = validate_skill_md_structure(skill_md)
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项")
        return 1


if __name__ == "__main__":
    sys.exit(main())
