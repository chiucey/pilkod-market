#!/usr/bin/env python3
"""
技能验证脚本 - 公共管理论文评阅技能
检查 SKILL.md 的 frontmatter 格式和基本结构
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证 SKILL.md 的 frontmatter 格式"""
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    content = skill_md.read_text(encoding='utf-8')

    # 检查 frontmatter 格式
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头（frontmatter 开始）"

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        return False, "frontmatter 格式不完整"

    # 找到 frontmatter 结束
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "frontmatter 缺少结束标记 ---"

    # 解析 frontmatter 内容
    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需的字段
    if 'name:' not in frontmatter_text:
        return False, "frontmatter 缺少 name 字段"

    if 'description:' not in frontmatter_text:
        return False, "frontmatter 缺少 description 字段"

    # 检查 name 格式（连字符）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name 字段格式错误: {name}，应使用小写字母和连字符"

    return True, "验证通过"

def validate_meta(skill_path):
    """验证 _meta.json 格式"""
    import json

    meta_file = Path(skill_path) / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, f"_meta.json 格式错误: {e}"

    if 'id' not in meta:
        return False, "_meta.json 缺少 id 字段"

    if 'version' not in meta:
        return False, "_meta.json 缺少 version 字段"

    return True, "验证通过"

def validate_structure(skill_path):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = Path(skill_path) / file
        if not file_path.exists():
            return False, f"缺少必需文件: {file}"

    return True, "验证通过"

def main():
    skill_path = "/workspace/temp-skills/public-management-paper-reviewer"

    checks = [
        ("结构验证", validate_structure),
        ("Frontmatter 验证", lambda p: validate_frontmatter(p)),
        ("_meta.json 验证", validate_meta),
    ]

    all_passed = True
    for name, check_func in checks:
        passed, message = check_func(skill_path)
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {message}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n所有验证通过!")
        return 0
    else:
        print("\n验证失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
