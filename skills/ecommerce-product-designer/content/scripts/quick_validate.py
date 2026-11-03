#!/usr/bin/env python3
"""
电商美工技能验证脚本
验证技能文件的完整性和格式正确性
"""

import os
import json
import re
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证 SKILL.md 的 frontmatter"""
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        return False, "SKILL.md 文件不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开头（---）"

    # 提取 frontmatter - 查找第二个 --- 的位置
    lines = content.split('\n')
    first_dash = -1
    second_dash = -1

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if first_dash == -1:
                first_dash = i
            else:
                second_dash = i
                break

    if second_dash == -1:
        return False, "frontmatter 缺少结束的 ---"

    # 解析 frontmatter 内容（第一行 --- 之后，第二行 --- 之前的内容）
    frontmatter = {}
    for line in lines[first_dash + 1:second_dash]:
        if ':' in line:
            key = line.split(':')[0].strip()
            if key:  # 确保不是空行
                frontmatter[key] = True

    # 检查必需字段
    required_fields = ['name', 'description']
    missing = [f for f in required_fields if f not in frontmatter]
    if missing:
        return False, f"缺少必需字段: {', '.join(missing)}"

    return True, "Frontmatter 验证通过"

def validate_meta_json(skill_path):
    """验证 _meta.json 文件"""
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "_meta.json 文件不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required = ['id', 'version']
        missing = [f for f in required if f not in meta]
        if missing:
            return False, f"_meta.json 缺少字段: {', '.join(missing)}"

        if not isinstance(meta['id'], int):
            return False, "_meta.json 的 id 必须是整数"

        return True, "_meta.json 验证通过"
    except json.JSONDecodeError as e:
        return False, f"_meta.json 格式错误: {str(e)}"

def validate_naming(skill_path):
    """验证命名规范"""
    # 获取技能目录名
    skill_name = os.path.basename(skill_path)

    # 检查是否包含中文字符
    if re.search(r'[\u4e00-\u9fff]', skill_name):
        return False, f"技能目录名 '{skill_name}' 包含中文字符，应使用英文"

    # 检查 frontmatter 中的 name 字段
    skill_md = os.path.join(skill_path, "SKILL.md")
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 name 字段值
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if name_value != skill_name:
            return False, f"SKILL.md frontmatter 中的 name '{name_value}' 与目录名 '{skill_name}' 不匹配"

    return True, "命名验证通过"

def validate_directory_structure(skill_path):
    """验证目录结构"""
    expected_dirs = ['scripts', 'references', 'assets']
    missing = []

    for d in expected_dirs:
        full_path = os.path.join(skill_path, d)
        if not os.path.exists(full_path):
            missing.append(d)

    if missing:
        return False, f"缺少目录: {', '.join(missing)}"

    return True, "目录结构验证通过"

def run_validation(skill_path):
    """运行所有验证"""
    validations = [
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta_json),
        ("命名规范", validate_naming),
        ("目录结构", validate_directory_structure),
    ]

    all_passed = True
    results = []

    for name, func in validations:
        passed, message = func(skill_path)
        results.append((name, passed, message))
        if not passed:
            all_passed = False

    print("=" * 50)
    print("电商美工技能验证结果")
    print("=" * 50)

    for name, passed, message in results:
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {message}")

    print("=" * 50)

    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项，请修复后重试")
        return 1

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    exit_code = run_validation(skill_path)
    sys.exit(exit_code)
