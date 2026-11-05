#!/usr/bin/env python3
"""
快速验证脚本 - 检查 SKILL.md 格式和结构完整性
"""
import os
import re
import sys
import yaml

def validate_skill(path: str) -> list:
    """验证技能文件结构和格式"""
    errors = []
    warnings = []

    skill_md = os.path.join(path, "SKILL.md")
    meta_json = os.path.join(path, "_meta.json")

    # 1. 检查文件存在
    if not os.path.exists(skill_md):
        errors.append("SKILL.md 文件不存在")
        return errors

    if not os.path.exists(meta_json):
        errors.append("_meta.json 文件不存在")
        return errors

    # 2. 读取 SKILL.md 内容
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. Frontmatter 验证
    frontmatter_pattern = r'^---\n(.*?)\n---'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        errors.append("Frontmatter 格式错误：必须以 --- 开头和结尾")
    else:
        try:
            frontmatter = yaml.safe_load(match.group(1))

            # 检查必填字段
            if 'name' not in frontmatter:
                errors.append("Frontmatter 缺少 'name' 字段")
            elif not isinstance(frontmatter['name'], str):
                errors.append("'name' 必须是字符串")

            if 'description' not in frontmatter:
                errors.append("Frontmatter 缺少 'description' 字段")
            elif not isinstance(frontmatter['description'], str):
                errors.append("'description' 必须是字符串")
            elif len(frontmatter['description']) < 20:
                warnings.append("'description' 可能过于简短，建议至少20字符")
        except yaml.YAMLError as e:
            errors.append(f"Frontmatter YAML 解析错误: {e}")

    # 4. 检查 frontmatter 是否在第一行
    lines = content.split('\n')
    if not content.startswith('---'):
        errors.append("Frontmatter 必须在文件第一行开始")

    # 5. 检查是否在 frontmatter 之前有 markdown 标题
    frontmatter_end = content.find('---', 3)  # 找第二个 ---
    if frontmatter_end != -1:
        before_frontmatter = content[3:frontmatter_end]
        if '#' in before_frontmatter:
            errors.append("Frontmatter 之前不能有 markdown 标题 (#)")

    # 6. 验证 _meta.json
    with open(meta_json, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误：不是有效的 JSON")

    return errors, warnings

if __name__ == "__main__":
    import json

    path = sys.argv[1] if len(sys.argv) > 1 else "."
    errors, warnings = validate_skill(path)

    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    if warnings:
        print("⚠️ 有警告:")
        for w in warnings:
            print(f"  - {w}")

    print("✅ 验证通过")