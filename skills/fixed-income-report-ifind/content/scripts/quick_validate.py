#!/usr/bin/env python3
"""
快速验证Skill结构和Frontmatter
"""
import os
import sys
import json
import re

def validate_skill(skill_path):
    """验证Skill目录结构和frontmatter"""
    errors = []
    warnings = []

    # 检查目录存在
    if not os.path.exists(skill_path):
        return False, [f"路径不存在: {skill_path}"]

    skill_name = os.path.basename(skill_path.rstrip('/'))

    # 1. 检查 SKILL.md 存在
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("缺少 SKILL.md 文件")
        return False, errors

    # 2. 读取并检查 frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 frontmatter 格式
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 --- 开头（frontmatter格式）")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 frontmatter")
    else:
        fm_text = frontmatter_match.group(1)
        fm = {}
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                fm[key.strip()] = value.strip()

        # 检查必需字段
        if 'name' not in fm:
            errors.append("frontmatter 缺少 'name' 字段")
        if 'description' not in fm:
            errors.append("frontmatter 缺少 'description' 字段")

        # 检查 name 格式（连字符）
        if 'name' in fm and not re.match(r'^[a-z0-9-]+$', fm['name']):
            errors.append(f"name 必须使用连字符格式: {fm['name']}")

        # 检查 name 与目录名匹配
        if 'name' in fm and fm['name'] != skill_name:
            warnings.append(f"name '{fm['name']}' 与目录名 '{skill_name}' 不匹配")

    # 3. 检查 _meta.json
    meta_json = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_json):
        errors.append("缺少 _meta.json 文件")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 4. 检查可选目录
    for subdir in ['scripts', 'references', 'assets']:
        subdir_path = os.path.join(skill_path, subdir)
        if os.path.exists(subdir_path) and not os.listdir(subdir_path):
            warnings.append(f"'{subdir}' 目录存在但为空")

    return len(errors) == 0, errors + warnings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    success, messages = validate_skill(skill_path)

    print(f"\n{'='*50}")
    print(f"验证结果: {'✓ 通过' if success else '✗ 失败'}")
    print(f"{'='*50}")

    for msg in messages:
        print(f"  - {msg}")

    sys.exit(0 if success else 1)