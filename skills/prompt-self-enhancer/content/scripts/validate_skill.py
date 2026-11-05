#!/usr/bin/env python3
"""
提示词自动提升技能验证脚本
检查技能结构和文件的完整性
"""

import os
import json
import sys

def validate_frontmatter(file_path: str) -> tuple[bool, str]:
    """验证frontmatter格式"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md必须以---开头"

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---' and not in_frontmatter:
            in_frontmatter = True
            continue
        elif line.strip() == '---' and in_frontmatter:
            break
        elif in_frontmatter:
            frontmatter_lines.append(line)

    # 解析frontmatter
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # 验证必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            return False, f"缺少必需字段: {field}"

    # 验证name格式
    name = frontmatter['name']
    if ' ' in name:
        return False, "name字段不能包含空格，应使用连字符格式（如: prompt-enhancer）"

    return True, "验证通过"

def validate_meta_json(meta_path: str) -> tuple[bool, str]:
    """验证_meta.json文件"""
    if not os.path.exists(meta_path):
        return False, "_meta.json文件不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必需字段
        required = ['id', 'version']
        for field in required:
            if field not in meta:
                return False, f"_meta.json缺少必需字段: {field}"

        # 验证版本格式
        version = meta['version']
        if not all(x.isdigit() for x in version.split('.')):
            return False, "version应遵循语义化版本格式（如: 1.0.0）"

        return True, "验证通过"

    except json.JSONDecodeError as e:
        return False, f"_meta.json格式错误: {e}"

def validate_directory_structure(base_path: str) -> tuple[bool, list]:
    """验证目录结构"""
    expected_dirs = ['scripts', 'references', 'assets']
    issues = []

    for dir_name in expected_dirs:
        dir_path = os.path.join(base_path, dir_name)
        if os.path.exists(dir_path):
            # 检查目录是否为空（除非是可选的）
            if not os.listdir(dir_path):
                issues.append(f"警告: {dir_name}/ 目录存在但为空")

    return len(issues) == 0, issues

def main():
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    print(f"技能目录: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # 1. 验证SKILL.md
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if os.path.exists(skill_md):
        passed, msg = validate_frontmatter(skill_md)
        print(f"✓ SKILL.md frontmatter: {msg}")
        if not passed:
            all_passed = False
    else:
        print("✗ SKILL.md不存在")
        all_passed = False

    # 2. 验证_meta.json
    meta_json = os.path.join(skill_dir, "_meta.json")
    passed, msg = validate_meta_json(meta_json)
    print(f"{'✓' if passed else '✗'} _meta.json: {msg}")
    if not passed:
        all_passed = False

    # 3. 验证目录结构
    passed, issues = validate_directory_structure(skill_dir)
    for issue in issues:
        print(f"  {issue}")
    print(f"✓ 目录结构: {'验证通过' if passed else '有问题'}")

    # 4. 检查脚本语法
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.exists(scripts_dir):
        for script_file in os.listdir(scripts_dir):
            if script_file.endswith('.py'):
                script_path = os.path.join(scripts_dir, script_file)
                try:
                    with open(script_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), script_path, 'exec')
                    print(f"✓ {script_file}: 语法正确")
                except SyntaxError as e:
                    print(f"✗ {script_file}: 语法错误 - {e}")
                    all_passed = False

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 存在验证失败项")
        return 1

if __name__ == "__main__":
    sys.exit(main())
