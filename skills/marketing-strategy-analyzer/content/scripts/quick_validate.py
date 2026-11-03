#!/usr/bin/env python3
"""
快速验证脚本 - 检查 SKILL.md 的 frontmatter 和结构
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

    # 检查 SKILL.md 是否存在
    if not os.path.exists(skill_md):
        errors.append("SKILL.md 不存在")
        return errors, warnings

    # 读取 SKILL.md 内容
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 frontmatter 开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头，不能以 # 标题开头")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 frontmatter，请检查格式")
    else:
        frontmatter_text = frontmatter_match.group(1)

        # 检查必填字段
        if 'name:' not in frontmatter_text:
            errors.append("frontmatter 缺少 name 字段")
        if 'description:' not in frontmatter_text:
            errors.append("frontmatter 缺少 description 字段")

        # 检查 description 长度
        desc_match = re.search(r'description:\s*(.+)', frontmatter_text)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                warnings.append(f"description 较短（{len(desc)}字符），建议增加触发短语")
            if 'Use when' not in desc and '使用' not in desc and '当用户' not in desc:
                warnings.append("description 建议包含触发条件（如 'Use when...' 或 '当用户...'）")

    # 检查 _meta.json
    if not os.path.exists(meta_json):
        errors.append("_meta.json 不存在")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误，不是有效的 JSON")

    # 检查目录结构
    for subdir in ['scripts', 'references', 'assets']:
        subdir_path = os.path.join(skill_path, subdir)
        if os.path.exists(subdir_path):
            if not os.listdir(subdir_path):
                warnings.append(f"{subdir}/ 目录为空")

    return errors, warnings


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    errors, warnings = validate_skill(skill_path)

    print("=" * 50)
    print(f"验证路径: {skill_path}")
    print("=" * 50)

    if errors:
        print(f"\n❌ 错误 ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print(f"\n⚠️  警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("\n✅ 验证通过！")
    elif not errors:
        print("\n✅ 核心验证通过（有警告）")
    else:
        print("\n❌ 验证失败")
        sys.exit(1)
