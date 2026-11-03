#!/usr/bin/env python3
"""
Smart Memory Hub 技能验证脚本

验证内容：
1. Frontmatter 格式正确性
2. 必填字段完整性
3. 文件结构合理性
4. 脚本语法正确性
5. 防膨胀约束验证
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# 颜色定义
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_success(msg: str):
    print(f"{GREEN}✓{RESET} {msg}")


def print_error(msg: str):
    print(f"{RED}✗{RESET} {msg}")


def print_warning(msg: str):
    print(f"{YELLOW}⚠{RESET} {msg}")


def print_info(msg: str):
    print(f"{BOLD}→{RESET} {msg}")


def validate_frontmatter(skill_path: Path) -> Tuple[bool, Dict]:
    """验证 Frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, {"error": "SKILL.md 文件不存在"}

    content = skill_md.read_text(encoding='utf-8')

    if not content.startswith('---'):
        return False, {"error": "Frontmatter 必须以 --- 开头"}

    lines = content.split('\n')
    end_index = -1

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_index = i
            break

    if end_index == -1:
        return False, {"error": "Frontmatter 缺少结束标记 ---"}

    required_fields = ['name', 'description']
    missing_fields = []

    frontmatter = {}
    for line in lines[1:end_index]:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    for field in required_fields:
        if field not in frontmatter:
            missing_fields.append(field)

    # 检查 markdown 内容
    content_after_fm = '\n'.join(lines[end_index+1:]).strip()
    markdown_start = re.search(r'^#\s+\S+', content_after_fm)

    result = {
        "frontmatter": frontmatter,
        "has_content": len(content_after_fm) > 0,
        "markdown_start": bool(markdown_start),
        "missing_fields": missing_fields
    }

    if missing_fields:
        return False, result

    if not markdown_start:
        return False, {"error": "缺少 markdown 标题", "frontmatter": frontmatter}

    return True, result


def validate_meta(skill_path: Path) -> Tuple[bool, Dict]:
    """验证 _meta.json"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, {"error": "_meta.json 文件不存在"}

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, {"error": f"_meta.json 格式错误: {e}"}

    required_fields = ['id', 'version']
    missing_fields = [f for f in required_fields if f not in meta]

    if 'version' in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            return False, {"error": "version 格式错误", "meta": meta}

    result = {"meta": meta, "missing_fields": missing_fields}

    if missing_fields:
        return False, result

    return True, result


def validate_constraints(skill_path: Path) -> Tuple[bool, List[str]]:
    """验证防膨胀约束"""
    errors = []

    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        constraints = meta.get('constraints', {})

        # 检查关键约束
        expected_constraints = {
            'max_entries': 200,
            'max_chars_per_entry': 200,
            'inject_limit': 5,
            'cleanup_threshold': 180,
            'timeout_ms': 1000,
        }

        for key, expected in expected_constraints.items():
            actual = constraints.get(key)
            if actual is not None and actual != expected:
                errors.append(
                    f"约束 {key}: 期望 {expected}, 实际 {actual}"
                )

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> Tuple[bool, List[str]]:
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    missing_files = []
    warnings = []

    for file in required_files:
        if not (skill_path / file).exists():
            missing_files.append(file)

    if missing_files:
        return False, [f"缺少必需文件: {', '.join(missing_files)}"]

    return True, warnings


def validate_naming(skill_path: Path, frontmatter: Dict) -> Tuple[bool, List[str]]:
    """验证命名规范"""
    errors = []

    folder_name = skill_path.name
    if not re.match(r'^[a-z0-9][a-z0-9-]*$', folder_name):
        errors.append(f"文件夹名称应使用小写字母、数字和连字符")

    if 'name' in frontmatter:
        name = frontmatter['name']
        if name != folder_name:
            errors.append(f"name '{name}' 应与文件夹名称 '{folder_name}' 一致")

    # 仅检查 name/id 字段
    for key in ['name', 'id']:
        if key in frontmatter:
            if re.search(r'[\u4e00-\u9fff]', frontmatter[key]):
                errors.append(f"'{key}' 不应包含中文字符")

    return len(errors) == 0, errors


def validate_python_syntax(skill_path: Path) -> Tuple[bool, List[str]]:
    """验证 Python 语法"""
    scripts_dir = skill_path / "scripts"
    errors = []

    if not scripts_dir.exists():
        return True, []

    for py_file in scripts_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source = f.read()
            compile(source, py_file.name, 'exec')
            print_success(f"  {py_file.name} 语法正确")
        except SyntaxError as e:
            errors.append(f"{py_file.name}: {e}")

    return len(errors) == 0, errors


def run_validation(skill_path: str) -> bool:
    """运行所有验证"""
    skill_path = Path(skill_path)

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Smart Memory Hub 技能验证{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    all_passed = True

    # 1. Frontmatter
    print_info("验证 Frontmatter 格式...")
    passed, result = validate_frontmatter(skill_path)
    if passed:
        print_success("Frontmatter 格式正确")
        print_info(f"  - name: {result['frontmatter'].get('name', 'N/A')}")
    else:
        print_error(f"Frontmatter 验证失败: {result.get('error')}")
        all_passed = False
    print()

    # 2. _meta.json
    print_info("验证 _meta.json...")
    passed, result = validate_meta(skill_path)
    if passed:
        print_success("_meta.json 格式正确")
        print_info(f"  - id: {result['meta'].get('id', 'N/A')}")
        print_info(f"  - version: {result['meta'].get('version', 'N/A')}")
    else:
        print_error(f"_meta.json 验证失败: {result.get('error')}")
        all_passed = False
    print()

    # 3. 约束验证
    print_info("验证防膨胀约束...")
    passed, errors = validate_constraints(skill_path)
    if passed:
        print_success("约束配置正确")
    else:
        for error in errors:
            print_error(error)
        all_passed = False
    print()

    # 4. 目录结构
    print_info("验证目录结构...")
    passed, warnings = validate_structure(skill_path)
    if passed:
        print_success("目录结构正确")
    else:
        for error in warnings:
            print_error(error)
        all_passed = False
    print()

    # 5. 命名规范
    print_info("验证命名规范...")
    fm_result = validate_frontmatter(skill_path)[1]
    passed, errors = validate_naming(skill_path, fm_result.get('frontmatter', {}))
    if passed:
        print_success("命名规范符合要求")
    else:
        for error in errors:
            print_error(error)
        all_passed = False
    print()

    # 6. Python 语法
    print_info("验证 Python 脚本语法...")
    passed, errors = validate_python_syntax(skill_path)
    if passed:
        print_success("所有 Python 脚本语法正确")
    else:
        for error in errors:
            print_error(error)
        all_passed = False
    print()

    print(f"{BOLD}{'='*60}{RESET}")

    if all_passed:
        print(f"{GREEN}{BOLD}✓ 所有验证通过！{RESET}")
        return True
    else:
        print(f"{RED}{BOLD}✗ 存在验证失败项{RESET}")
        return False


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = run_validation(skill_path)
    sys.exit(0 if success else 1)
