#!/usr/bin/env python3
"""验证金葵诗歌明信片技能的结构和内容"""

import os
import re
import json
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证 SKILL.md 的 frontmatter"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    content = skill_md.read_text(encoding='utf-8')

    # 检查 frontmatter 是否在第一行
    if not content.startswith('---'):
        errors.append("Frontmatter 必须从文件第一行开始（以 --- 开头）")
        return False, errors

    # 提取 frontmatter
    lines = content.split('\n')
    fm_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            fm_end = i
            break

    if fm_end == -1:
        errors.append("Frontmatter 缺少结束标记（---）")
        return False, errors

    fm_lines = lines[1:fm_end]

    # 检查必填字段
    fm_dict = {}
    for line in fm_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            fm_dict[key.strip()] = value.strip()

    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in fm_dict:
            errors.append(f"Frontmatter 缺少必填字段：{field}")

    # 检查 name 格式
    if 'name' in fm_dict:
        name = fm_dict['name']
        if not re.match(r'^[a-z0-9\-]+$', name):
            errors.append(f"name 字段格式错误：'{name}'，应使用小写字母、连字符（kebab-case）")

    return len(errors) == 0, errors

def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json"""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json JSON 格式错误：{e}"]

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必填字段：{field}")

    if 'version' in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append(f"version 字段格式错误：'{meta['version']}'，应使用语义化版本（x.y.z）")

    return len(errors) == 0, errors

def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []
    skill_dir = Path(skill_path)

    # 检查必要文件
    if not (skill_dir / "SKILL.md").exists():
        errors.append("缺少 SKILL.md")

    if not (skill_dir / "_meta.json").exists():
        errors.append("缺少 _meta.json")

    return len(errors) == 0, errors

def main():
    skill_path = "/workspace/temp-skills/golden-sunflower-poem-postcard"

    all_passed = True

    # 结构验证
    passed, errors = validate_structure(skill_path)
    if not passed:
        print("❌ 结构验证失败:")
        for e in errors:
            print(f"   - {e}")
        all_passed = False
    else:
        print("✅ 结构验证通过")

    # Frontmatter 验证
    passed, errors = validate_frontmatter(skill_path)
    if not passed:
        print("❌ Frontmatter 验证失败:")
        for e in errors:
            print(f"   - {e}")
        all_passed = False
    else:
        print("✅ Frontmatter 验证通过")

    # Meta JSON 验证
    passed, errors = validate_meta_json(skill_path)
    if not passed:
        print("❌ _meta.json 验证失败:")
        for e in errors:
            print(f"   - {e}")
        all_passed = False
    else:
        print("✅ _meta.json 验证通过")

    if all_passed:
        print("\n🎉 所有验证通过！技能结构正确。")
        return 0
    else:
        print("\n⚠️ 部分验证失败，请修复后重试。")
        return 1

if __name__ == "__main__":
    exit(main())