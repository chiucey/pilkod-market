#!/usr/bin/env python3
"""内容调研技能验证脚本"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(file_path):
    """验证 frontmatter 格式"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行是否为 ---
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        return False, "SKILL.md 必须以 --- 开头"

    # 提取 frontmatter
    if content.count('---') < 2:
        return False, "缺少 frontmatter 结束标记 ---"

    end_idx = content.index('---', 3)
    frontmatter = content[3:end_idx].strip()

    # 检查必填字段
    if not re.search(r'^name:', frontmatter, re.MULTILINE):
        return False, "缺少 name 字段"
    if not re.search(r'^description:', frontmatter, re.MULTILINE):
        return False, "缺少 description 字段"

    return True, "Frontmatter 验证通过"

def validate_meta(meta_path):
    """验证 _meta.json"""
    import json
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        return False, "缺少 id 字段"
    if 'version' not in meta:
        return False, "缺少 version 字段"

    return True, "_meta.json 验证通过"

def validate_naming(path):
    """验证命名规范"""
    skill_dir = Path(path)
    name = skill_dir.name

    # 检查名称为英文
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"技能目录名 '{name}' 应为英文小写字母、数字和连字符"

    # 检查 SKILL.md 中 name 字段一致
    skill_md = skill_dir / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if match:
            frontmatter_name = match.group(1).strip()
            if frontmatter_name != name:
                return False, f"Frontmatter name '{frontmatter_name}' 应与目录名 '{name}' 一致"

    return True, "命名验证通过"

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'

    results = []

    # 验证 SKILL.md
    skill_md = Path(skill_path) / 'SKILL.md'
    if skill_md.exists():
        valid, msg = validate_frontmatter(skill_md)
        results.append((valid, f"Frontmatter: {msg}"))
    else:
        results.append((False, "SKILL.md 不存在"))

    # 验证 _meta.json
    meta_path = Path(skill_path) / '_meta.json'
    if meta_path.exists():
        valid, msg = validate_meta(meta_path)
        results.append((valid, f"Meta: {msg}"))
    else:
        results.append((False, "_meta.json 不存在"))

    # 验证命名
    valid, msg = validate_naming(skill_path)
    results.append((valid, f"命名: {msg}"))

    # 输出结果
    print("=" * 50)
    print("内容调研技能验证结果")
    print("=" * 50)
    for valid, msg in results:
        status = "✓" if valid else "✗"
        print(f"{status} {msg}")
    print("=" * 50)

    all_passed = all(r[0] for r in results)
    if all_passed:
        print("✓ 所有验证通过！")
        sys.exit(0)
    else:
        print("✗ 存在验证失败项")
        sys.exit(1)

if __name__ == '__main__':
    main()
