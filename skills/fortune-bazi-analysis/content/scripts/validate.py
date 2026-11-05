#!/usr/bin/env python3
"""
SKILL.md 验证脚本
检查 frontmatter 格式、必填字段和结构完整性
"""

import os
import re
import sys
import json

def validate_skill(skill_path):
    """验证技能文件结构和 frontmatter"""
    errors = []
    warnings = []

    skill_md = os.path.join(skill_path, "SKILL.md")
    meta_json = os.path.join(skill_path, "_meta.json")

    # 检查必需文件
    if not os.path.exists(skill_md):
        errors.append("缺少 SKILL.md 文件")
        return errors, warnings

    if not os.path.exists(meta_json):
        errors.append("缺少 _meta.json 文件")
        return errors, warnings

    # 读取并验证 SKILL.md frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 frontmatter 格式
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter 开头（---）")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 YAML frontmatter")
    else:
        frontmatter_text = frontmatter_match.group(1)

        # 检查必填字段
        if not re.search(r'^name:', frontmatter_text, re.MULTILINE):
            errors.append("Frontmatter 缺少 'name' 字段")

        if not re.search(r'^description:', frontmatter_text, re.MULTILINE):
            errors.append("Frontmatter 缺少 'description' 字段")

        # 提取 name 值
        name_match = re.search(r'^name:\s*(.+?)\s*$', frontmatter_text, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            # 检查名称格式（连字符）
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name_value):
                warnings.append(f"name 字段应使用连字符格式（小写字母和数字），当前: {name_value}")

        # 检查 description 触发短语
        desc_match = re.search(r'^description:\s*(.+?)\s*$', frontmatter_text, re.MULTILINE)
        if desc_match:
            desc_value = desc_match.group(1)
            # 检查是否包含触发短语
            if "当用户" not in desc_value and "Use when" not in desc_value:
                warnings.append("description 应包含触发短语（如 '当用户...' 或 'Use when...'）")

    # 检查 frontmatter 之前是否有内容（应该只有 --- 在第一行）
    lines_before_frontmatter = content.split('\n')
    found_frontmatter_start = False
    for i, line in enumerate(lines_before_frontmatter):
        if line.strip() == '---' and not found_frontmatter_start:
            found_frontmatter_start = True
            continue
        if found_frontmatter_start:
            # 已经在 frontmatter 内，不检查
            break
        if line.strip() and not line.strip().startswith('#'):
            # 在 frontmatter 开始之前有非标题内容
            if i > 0:  # 第一行之后有内容
                warnings.append(f"Frontmatter 之前有内容: {line[:30]}...")

    # 读取并验证 _meta.json
    with open(meta_json, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")
            return errors, warnings

    # 检查必填字段
    if 'id' not in meta:
        errors.append("_meta.json 缺少 'id' 字段")
    elif not isinstance(meta['id'], int):
        errors.append("_meta.json 'id' 必须为整数")

    if 'version' not in meta:
        errors.append("_meta.json 缺少 'version' 字段")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        warnings.append("_meta.json 'version' 应遵循语义化版本格式（如 1.0.0）")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    errors, warnings = validate_skill(skill_path)

    if warnings:
        print("\n⚠️  警告:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")
        print("\n验证失败！")
        sys.exit(1)
    else:
        print("\n✅ 验证通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()
