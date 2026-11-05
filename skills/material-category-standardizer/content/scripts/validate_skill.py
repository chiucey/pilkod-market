#!/usr/bin/env python3
"""
材料类别标准化技能验证脚本
验证 SKILL.md 结构和 _meta.json 格式
"""

import json
import os
import sys
from pathlib import Path

def validate_frontmatter():
    """验证 SKILL.md frontmatter"""
    skill_file = Path(__file__).parent.parent / "SKILL.md"
    if not skill_file.exists():
        return False, "SKILL.md 文件不存在"

    content = skill_file.read_text(encoding='utf-8')

    # 检查第一行是否是 ---
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        return False, "SKILL.md 必须以 --- 开头作为 frontmatter 分隔符"

    # 检查 frontmatter 结束
    try:
        end_idx = content.index('---', 3)
        frontmatter_text = content[3:end_idx].strip()
    except ValueError:
        return False, "SKILL.md frontmatter 未正确关闭"

    # 解析 frontmatter
    try:
        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
    except Exception as e:
        return False, f"frontmatter 解析错误: {e}"

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            return False, f"缺少必需字段: {field}"

    # 验证 name 格式（连字符格式）
    name = frontmatter['name']
    if not name.replace('-', '').isalnum() or not name.replace('-', '').islower():
        return False, f"name 字段格式错误，应使用连字符格式: {name}"

    # 检查 description 是否包含触发短语
    desc = frontmatter['description']
    trigger_phrases = ['标准化', '材料类别', '映射', '清洗', '规范']
    has_trigger = any(phrase in desc for phrase in trigger_phrases)
    if not has_trigger:
        return False, "description 应包含触发短语，如'标准化材料类别'"

    return True, "frontmatter 验证通过"

def validate_meta():
    """验证 _meta.json 格式"""
    meta_file = Path(__file__).parent.parent / "_meta.json"
    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 格式错误: {e}"

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"缺少必需字段: {field}"

    # 验证 id 是整数
    if not isinstance(meta['id'], int):
        return False, f"id 必须是整数: {meta['id']}"

    # 验证 version 格式
    version = meta['version']
    if not isinstance(version, str) or len(version.split('.')) != 3:
        return False, f"version 应为语义化版本格式 (x.y.z): {version}"

    return True, "_meta.json 验证通过"

def validate_categories():
    """验证材料类别映射表"""
    categories_file = Path(__file__).parent.parent / "references" / "material_categories.json"
    if not categories_file.exists():
        return False, "material_categories.json 不存在"

    try:
        data = json.loads(categories_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, f"material_categories.json JSON 格式错误: {e}"

    # 检查顶层结构
    if 'categories' not in data:
        return False, "缺少 categories 数组"

    # 检查每个类别
    for i, cat in enumerate(data['categories']):
        required_fields = ['code', 'name', 'parent', 'keywords']
        for field in required_fields:
            if field not in cat:
                return False, f"类别 {i} 缺少字段: {field}"

    return True, f"material_categories.json 验证通过 (共 {len(data['categories'])} 个类别)"

def main():
    """运行所有验证"""
    print("=" * 50)
    print("材料类别标准化技能 - 质量验证")
    print("=" * 50)

    checks = [
        ("Frontmatter 验证", validate_frontmatter),
        ("_meta.json 验证", validate_meta),
        ("材料类别映射表验证", validate_categories),
    ]

    all_passed = True
    for name, func in checks:
        print(f"\n检查: {name}")
        passed, message = func()
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {status}: {message}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("所有验证通过！技能结构符合规范。")
        return 0
    else:
        print("验证失败，请修复上述问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
