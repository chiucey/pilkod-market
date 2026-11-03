#!/usr/bin/env python3
"""
国家标准下载器技能 - 快速验证脚本
验证 SKILL.md frontmatter 格式和文件结构
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md frontmatter 格式"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查文件开头是否为 frontmatter
    if not content.startswith('---'):
        errors.append("❌ SKILL.md 必须以 YAML frontmatter (---) 开头")
        return errors, False

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("❌ 无法解析 YAML frontmatter")
        return errors, False

    frontmatter_text = frontmatter_match.group(1)

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"❌ frontmatter 缺少必填字段: {field}")

    # 检查 name 字段格式（连字符）
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            errors.append(f"❌ name 必须使用连字符格式（小写字母、数字、连字符）: 当前值='{name_value}'")
        if ' ' in name_value:
            errors.append(f"❌ name 不能包含空格: 当前值='{name_value}'")

    # 检查 description 是否包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            errors.append(f"⚠️ description 过短（建议至少20字符）: 当前={len(desc_value)}字符")
        if '当用户' not in desc_value and 'Use when' not in desc_value:
            errors.append("⚠️ description 建议包含触发短语（如'当用户...'或'Use when...'）")

    return errors, len(errors) == 0

def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("❌ 缺少 _meta.json 文件")
        return errors, False

    import json
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"❌ _meta.json 格式错误: {e}")
        return errors, False

    # 检查必填字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"❌ _meta.json 缺少必填字段: {field}")
        elif field == 'id':
            if not isinstance(meta[field], int):
                errors.append(f"❌ _meta.json id 必须是整数: 当前={type(meta[field])}")
        elif field == 'version':
            if not re.match(r'^\d+\.\d+\.\d+$', meta[field]):
                errors.append(f"❌ _meta.json version 必须是语义化版本格式（如1.0.0）: 当前={meta[field]}")

    return errors, len(errors) == 0

def validate_structure(skill_dir):
    """验证目录结构"""
    errors = []

    # 检查必填目录/文件
    required = {
        'SKILL.md': 'file',
        '_meta.json': 'file',
    }

    for item, item_type in required.items():
        path = os.path.join(skill_dir, item)
        if not os.path.exists(path):
            errors.append(f"❌ 缺少{item_type}: {item}")
        elif item_type == 'file':
            if os.path.getsize(path) == 0:
                errors.append(f"❌ 文件为空: {item}")

    # 检查可选目录
    optional = ['references', 'scripts', 'assets']
    for dir_name in optional:
        path = os.path.join(skill_dir, dir_name)
        if os.path.exists(path):
            if not os.path.isdir(path):
                errors.append(f"❌ 期望是目录但是文件: {dir_name}")

    return errors, len(errors) == 0

def main():
    skill_dir = '/workspace/temp-skills/national-standard-downloader'

    print("=" * 50)
    print("国家标准下载器技能 - 验证检查")
    print("=" * 50)

    all_errors = []
    all_passed = True

    # 1. 验证目录结构
    print("\n[1/3] 检查目录结构...")
    structure_errors, structure_ok = validate_structure(skill_dir)
    all_errors.extend(structure_errors)
    if structure_ok:
        print("✅ 目录结构验证通过")
    else:
        print("❌ 目录结构验证失败")
        for err in structure_errors:
            print(f"  {err}")
        all_passed = False

    # 2. 验证 frontmatter
    print("\n[2/3] 检查 frontmatter 格式...")
    frontmatter_errors, frontmatter_ok = validate_frontmatter(
        os.path.join(skill_dir, 'SKILL.md')
    )
    all_errors.extend(frontmatter_errors)
    if frontmatter_ok:
        print("✅ Frontmatter 格式验证通过")
    else:
        print("❌ Frontmatter 格式验证失败")
        for err in frontmatter_errors:
            print(f"  {err}")
        all_passed = False

    # 3. 验证 _meta.json
    print("\n[3/3] 检查 _meta.json...")
    meta_errors, meta_ok = validate_meta_json(
        os.path.join(skill_dir, '_meta.json')
    )
    all_errors.extend(meta_errors)
    if meta_ok:
        print("✅ _meta.json 格式验证通过")
    else:
        print("❌ _meta.json 格式验证失败")
        for err in meta_errors:
            print(f"  {err}")
        all_passed = False

    # 总结
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有验证检查通过！")
        return 0
    else:
        print(f"❌ 发现 {len(all_errors)} 个问题，请修复后重新验证")
        return 1

if __name__ == '__main__':
    sys.exit(main())
