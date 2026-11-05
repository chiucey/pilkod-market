#!/usr/bin/env python3
"""短剧导演技能验证脚本"""

import json
import os
from pathlib import Path

def validate_frontmatter(filepath):
    """验证SKILL.md的frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter格式
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头"

    # 提取frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, "frontmatter格式不完整"

    frontmatter = parts[1]

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if f'{field}:' not in frontmatter:
            return False, f"缺少必需字段: {field}"

    return True, "frontmatter验证通过"

def validate_meta_json(skill_dir):
    """验证_meta.json"""
    meta_path = Path(skill_dir) / '_meta.json'

    if not meta_path.exists():
        return False, "_meta.json不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 检查必需字段
    if 'id' not in meta:
        return False, "_meta.json缺少id字段"
    if 'version' not in meta:
        return False, "_meta.json缺少version字段"

    return True, "_meta.json验证通过"

def validate_naming(skill_dir):
    """验证命名规范"""
    skill_name = Path(skill_dir).name

    # 检查是否包含中文字符
    if any('\u4e00' <= c <= '\u9fff' for c in skill_name):
        return False, "文件夹名称不能包含中文字符"

    # 检查格式（连字符）
    if not all(c.islower() or c.isdigit() or c == '-' for c in skill_name):
        return False, "文件夹名称只能包含小写字母、数字和连字符"

    return True, "命名规范验证通过"

def main():
    skill_dir = '/workspace/temp-skills/multi-character-drama-director'

    # 验证SKILL.md
    skill_md = Path(skill_dir) / 'SKILL.md'
    if not skill_md.exists():
        print("❌ SKILL.md不存在")
        return

    valid, msg = validate_frontmatter(skill_md)
    print(f"{'✅' if valid else '❌'} SKILL.md frontmatter: {msg}")

    # 验证_meta.json
    valid, msg = validate_meta_json(skill_dir)
    print(f"{'✅' if valid else '❌'} _meta.json: {msg}")

    # 验证命名
    valid, msg = validate_naming(skill_dir)
    print(f"{'✅' if valid else '❌'} 命名规范: {msg}")

    # 验证目录结构
    expected_dirs = ['references', 'assets', 'scripts']
    for d in expected_dirs:
        dir_path = Path(skill_dir) / d
        if dir_path.exists():
            print(f"✅ 目录 {d} 存在")
        else:
            print(f"⚠️  目录 {d} 不存在（可选）")

if __name__ == '__main__':
    main()
