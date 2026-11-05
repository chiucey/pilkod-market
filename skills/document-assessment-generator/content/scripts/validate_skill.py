#!/usr/bin/env python3
"""
技能验证脚本 - 智能文档解析与考核系统
验证目录结构、frontmatter格式和命名规范
"""

import os
import re
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL)
REQUIRED_FIELDS = ['name', 'description']
REQUIRED_META = ['id', 'version']

def validate_frontmatter(content):
    """验证frontmatter格式和必填字段"""
    match = FRONTMATTER_PATTERN.match(content.strip())
    if not match:
        return False, "Frontmatter未找到或格式错误（必须以---开头和结尾）"

    try:
        frontmatter = {}
        for line in match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
    except Exception as e:
        return False, f"Frontmatter解析失败: {e}"

    missing = [f for f in REQUIRED_FIELDS if f not in frontmatter]
    if missing:
        return False, f"缺少必填字段: {', '.join(missing)}"

    return True, "Frontmatter验证通过"

def validate_meta_json(meta_path):
    """验证_meta.json文件"""
    if not meta_path.exists():
        return False, "_meta.json文件不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json格式错误: {e}"

    missing = [f for f in REQUIRED_META if f not in meta]
    if missing:
        return False, f"_meta.json缺少字段: {', '.join(missing)}"

    if not isinstance(meta.get('id'), int):
        return False, "_meta.json中id必须是整数"

    return True, "_meta.json验证通过"

def validate_structure():
    """验证整体目录结构"""
    errors = []

    # 检查根目录
    if not SKILL_DIR.exists():
        errors.append(f"技能目录不存在: {SKILL_DIR}")
        return errors

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = SKILL_DIR / file
        if not path.exists():
            errors.append(f"缺少必需文件: {file}")

    # 检查SKILL.md是否以frontmatter开头
    skill_md = SKILL_DIR / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')

        # 检查第一行是否是---
        first_line = content.strip().split('\n')[0]
        if first_line.strip() != '---':
            errors.append("SKILL.md必须以---开头（frontmatter必须放在最前面）")

        # 验证frontmatter
        valid, msg = validate_frontmatter(content)
        if not valid:
            errors.append(msg)

    # 检查_meta.json
    meta_json = SKILL_DIR / '_meta.json'
    if meta_json.exists():
        valid, msg = validate_meta_json(meta_json)
        if not valid:
            errors.append(msg)

    return errors

def validate_naming():
    """验证命名规范"""
    errors = []

    # 目录名应为连字符格式
    dir_name = SKILL_DIR.name
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', dir_name):
        errors.append(f"目录名应使用连字符格式（当前: {dir_name}）")

    # 检查frontmatter中的name字段
    skill_md = SKILL_DIR / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        match = FRONTMATTER_PATTERN.match(content.strip())
        if match:
            for line in match.group(1).strip().split('\n'):
                if line.startswith('name:'):
                    name = line.split(':', 1)[1].strip()
                    if name != dir_name:
                        errors.append(f"name字段({name})应与目录名({dir_name})一致")
                    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                        errors.append(f"name字段应使用连字符格式（当前: {name}）")

    return errors

def main():
    """主验证流程"""
    print(f"🔍 验证技能: {SKILL_DIR.name}")
    print("-" * 50)

    all_errors = []

    # 结构验证
    print("📁 检查目录结构...")
    struct_errors = validate_structure()
    all_errors.extend(struct_errors)
    for err in struct_errors:
        print(f"   ❌ {err}")
    if not struct_errors:
        print("   ✅ 目录结构验证通过")

    # 命名验证
    print("\n🏷️  检查命名规范...")
    naming_errors = validate_naming()
    all_errors.extend(naming_errors)
    for err in naming_errors:
        print(f"   ❌ {err}")
    if not naming_errors:
        print("   ✅ 命名规范验证通过")

    # 结果汇总
    print("\n" + "=" * 50)
    if all_errors:
        print(f"❌ 验证失败，发现 {len(all_errors)} 个错误")
        sys.exit(1)
    else:
        print("✅ 所有验证通过！")
        sys.exit(0)

if __name__ == '__main__':
    main()
