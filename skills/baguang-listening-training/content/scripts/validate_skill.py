#!/usr/bin/env python3
"""验证八桂听辨训练营技能的结构和内容"""

import os
import re
import sys

def validate_frontmatter(skill_md_path):
    """验证Frontmatter格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行必须是 ---
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        return False, "Frontmatter必须以---开头，第一行不是---"

    # 检查是否有闭合的 ---
    if content.count('---') < 2:
        return False, "Frontmatter必须有开始和结束---"

    # 提取frontmatter
    frontmatter_end = content.find('---', 3)
    frontmatter = content[3:frontmatter_end].strip()

    # 检查必填字段
    if 'name:' not in frontmatter:
        return False, "缺少name字段"
    if 'description:' not in frontmatter:
        return False, "缺少description字段"

    return True, "Frontmatter验证通过"

def validate_meta(meta_path):
    """验证_meta.json"""
    import json
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        return False, "缺少id字段"
    if 'version' not in meta:
        return False, "缺少version字段"

    return True, "_meta.json验证通过"

def validate_naming(path):
    """验证所有文件名和路径都是英文"""
    non_english = re.findall(r'[^a-zA-Z0-9/_.\-]', path)
    if non_english:
        return False, f"路径包含非英文字符: {non_english}"
    return True, "命名验证通过"

def main():
    skill_dir = "/workspace/temp-skills/baguang-listening-training"
    skill_md = os.path.join(skill_dir, "SKILL.md")
    meta_json = os.path.join(skill_dir, "_meta.json")

    results = []

    # 验证目录名
    valid, msg = validate_naming(skill_dir)
    results.append((valid, f"目录名: {msg}"))

    # 验证SKILL.md
    if os.path.exists(skill_md):
        valid, msg = validate_frontmatter(skill_md)
        results.append((valid, f"SKILL.md: {msg}"))
    else:
        results.append((False, "SKILL.md不存在"))

    # 验证_meta.json
    if os.path.exists(meta_json):
        valid, msg = validate_meta(meta_json)
        results.append((valid, f"_meta.json: {msg}"))
    else:
        results.append((False, "_meta.json不存在"))

    # 打印结果
    print("=" * 50)
    print("技能验证结果")
    print("=" * 50)
    all_passed = True
    for valid, msg in results:
        status = "✓" if valid else "✗"
        print(f"{status} {msg}")
        if not valid:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("所有验证通过！")
        return 0
    else:
        print("存在验证失败项")
        return 1

if __name__ == "__main__":
    sys.exit(main())