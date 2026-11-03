#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和内容
"""
import os
import re
import json
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> list:
    """验证 frontmatter 格式"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return ["SKILL.md 文件不存在"]

    content = skill_md.read_text(encoding='utf-8')

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter 开头（---）")
        return errors

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 YAML frontmatter")
        return errors

    try:
        import yaml
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
    except Exception as e:
        errors.append(f"YAML 格式错误: {e}")
        return errors

    # 检查必需字段
    if 'name' not in frontmatter:
        errors.append("缺少 name 字段")
    if 'description' not in frontmatter:
        errors.append("缺少 description 字段")

    # 检查 name 格式
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name 必须使用连字符格式（小写）：{name}")
        if name != skill_path.name:
            errors.append(f"name ({name}) 必须与文件夹名称 ({skill_path.name}) 匹配")

    return errors

def validate_meta(skill_path: Path) -> list:
    """验证 _meta.json"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return ["_meta.json 文件不存在"]

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except:
        return ["_meta.json 格式错误"]

    if 'id' not in meta:
        errors.append("缺少 id 字段")
    if 'version' not in meta:
        errors.append("缺少 version 字段")

    return errors

def validate_structure(skill_path: Path) -> list:
    """验证目录结构"""
    errors = []

    required_dirs = []
    optional_dirs = ['scripts', 'references', 'assets']

    for d in required_dirs:
        if not (skill_path / d).exists():
            errors.append(f"缺少必需目录: {d}")

    return errors

def main():
    import yaml

    skill_path = Path(__file__).parent.parent

    print(f"验证技能: {skill_path.name}")
    print("-" * 50)

    all_errors = []

    # 验证 frontmatter
    print("检查 frontmatter...")
    errors = validate_frontmatter(skill_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print("  ✅ frontmatter 格式正确")

    # 验证 meta
    print("检查 _meta.json...")
    errors = validate_meta(skill_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print("  ✅ _meta.json 格式正确")

    # 验证结构
    print("检查目录结构...")
    errors = validate_structure(skill_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print("  ✅ 目录结构正确")

    print("-" * 50)

    if all_errors:
        print(f"验证失败: {len(all_errors)} 个错误")
        return 1
    else:
        print("✅ 验证通过")
        return 0

if __name__ == "__main__":
    exit(main())
