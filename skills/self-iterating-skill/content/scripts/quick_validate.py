#!/usr/bin/env python3
"""
自我迭代技能 - 快速验证脚本
验证技能结构和 frontmatter 完整性
"""

import os
import json
import re
import sys

def check_frontmatter(skill_md_path: str) -> tuple:
    """检查 SKILL.md frontmatter"""
    if not os.path.exists(skill_md_path):
        return False, "SKILL.md 不存在"

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 frontmatter (---) 开头"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 frontmatter"

    frontmatter_text = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    missing_fields = []

    for field in required_fields:
        if not re.search(f'^{field}:', frontmatter_text, re.MULTILINE):
            missing_fields.append(field)

    if missing_fields:
        return False, f"缺少必需字段: {', '.join(missing_fields)}"

    # 验证 name 格式
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name 必须使用小写字母、数字和连字符: {name}"

    return True, "frontmatter 验证通过"

def check_meta_json(meta_path: str) -> tuple:
    """检查 _meta.json"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_fields = ['id', 'version']
        missing_fields = []

        for field in required_fields:
            if field not in meta:
                missing_fields.append(field)

        if missing_fields:
            return False, f"缺少必需字段: {', '.join(missing_fields)}"

        # 验证 version 格式
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            return False, f"version 必须符合语义化版本格式: {meta['version']}"

        return True, "_meta.json 验证通过"

    except json.JSONDecodeError as e:
        return False, f"_meta.json 格式错误: {e}"
    except Exception as e:
        return False, f"验证失败: {e}"

def check_directory_structure(skill_dir: str) -> tuple:
    """检查目录结构"""
    required_dirs = ['scripts', 'references', 'data']
    missing_dirs = []

    for d in required_dirs:
        if not os.path.exists(os.path.join(skill_dir, d)):
            missing_dirs.append(d)

    if missing_dirs:
        return False, f"缺少目录: {', '.join(missing_dirs)}"

    return True, "目录结构验证通过"

def check_scripts(skill_dir: str) -> tuple:
    """检查脚本文件"""
    scripts_dir = os.path.join(skill_dir, 'scripts')
    required_scripts = [
        'analyze_performance.py',
        'generate_improvements.py',
        'apply_upgrades.py'
    ]

    missing_scripts = []
    for script in required_scripts:
        if not os.path.exists(os.path.join(scripts_dir, script)):
            missing_scripts.append(script)

    if missing_scripts:
        return False, f"缺少脚本: {', '.join(missing_scripts)}"

    return True, f"脚本验证通过 ({len(required_scripts)} 个)"

def run_validation(skill_dir: str) -> bool:
    """运行完整验证"""
    print("\n" + "="*60)
    print("自我迭代技能 - 验证检查")
    print("="*60)

    checks = [
        ('Frontmatter', check_frontmatter, os.path.join(skill_dir, 'SKILL.md')),
        ('_meta.json', check_meta_json, os.path.join(skill_dir, '_meta.json')),
        ('目录结构', check_directory_structure, skill_dir),
        ('脚本文件', check_scripts, skill_dir),
    ]

    all_passed = True
    for name, check_func, path in checks:
        passed, message = check_func(path)
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"\n[{name}] {status}")
        print(f"  {message}")

        if not passed:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("验证结果: 全部通过 ✓")
    else:
        print("验证结果: 存在问题 ✗")

    print("="*60 + "\n")

    return all_passed

if __name__ == '__main__':
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    success = run_validation(skill_dir)
    sys.exit(0 if success else 1)
