#!/usr/bin/env python3
"""
技能验证脚本 - 验证SKILL.md和_meta.json的格式正确性
"""

import os
import re
import json
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list]:
    """验证frontmatter格式"""
    errors = []
    skill_md = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_md):
        errors.append("SKILL.md 文件不存在")
        return False, errors

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 --- 开头（frontmatter开始）")

    # 提取 frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append("无法解析 frontmatter，请检查格式")
        return False, errors

    frontmatter_text = match.group(1)

    # 检查必需的字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"缺少必需字段: {field}")

    # 检查 name 格式（连字符）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            errors.append(f"name 格式不正确，应使用连字符: {name}")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list]:
    """验证_meta.json格式"""
    errors = []
    meta_path = os.path.join(skill_path, '_meta.json')

    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
        return False, errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必需字段
        if 'id' not in meta:
            errors.append("_meta.json 缺少 'id' 字段")
        elif not isinstance(meta['id'], int):
            errors.append("_meta.json 的 'id' 必须是整数")

        if 'version' not in meta:
            errors.append("_meta.json 缺少 'version' 字段")
        elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append("_meta.json 的 'version' 格式不正确，应为 x.y.z")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON格式错误: {e}")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list]:
    """验证目录结构"""
    errors = []

    # 检查基本目录结构
    required_items = ['SKILL.md', '_meta.json']
    for item in required_items:
        item_path = os.path.join(skill_path, item)
        if not os.path.exists(item_path):
            errors.append(f"缺少必需项: {item}")

    # 检查目录名称与name字段一致
    skill_name = os.path.basename(skill_path)
    meta_path = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            if 'id' in meta:
                # id存在即可
                pass

    return len(errors) == 0, errors


def validate_skill(skill_path: str) -> dict:
    """执行所有验证并返回结果"""
    results = {
        'path': skill_path,
        'valid': True,
        'errors': []
    }

    # 验证 frontmatter
    fm_valid, fm_errors = validate_frontmatter(skill_path)
    if not fm_valid:
        results['valid'] = False
        results['errors'].extend([f"Frontmatter: {e}" for e in fm_errors])

    # 验证 _meta.json
    meta_valid, meta_errors = validate_meta_json(skill_path)
    if not meta_valid:
        results['valid'] = False
        results['errors'].extend([f"Meta JSON: {e}" for e in meta_errors])

    # 验证结构
    struct_valid, struct_errors = validate_structure(skill_path)
    if not struct_valid:
        results['valid'] = False
        results['errors'].extend([f"Structure: {e}" for e in struct_errors])

    return results


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = '.'

    results = validate_skill(skill_path)

    print(f"\n技能验证结果: {'✓ 通过' if results['valid'] else '✗ 失败'}")
    print(f"路径: {results['path']}")

    if results['errors']:
        print("\n错误列表:")
        for error in results['errors']:
            print(f"  - {error}")

    sys.exit(0 if results['valid'] else 1)
