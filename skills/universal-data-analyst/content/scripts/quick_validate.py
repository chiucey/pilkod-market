#!/usr/bin/env python3
"""
Quick Validator - 快速验证技能结构和内容

检查：
1. SKILL.md frontmatter 格式
2. _meta.json 存在性和内容
3. 目录结构完整性
4. 路径和命名合规性（无中文）
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_pass(msg: str):
    print(f"{Colors.GREEN}✅ PASS{Colors.RESET} {msg}")


def print_fail(msg: str):
    print(f"{Colors.RED}❌ FAIL{Colors.RESET} {msg}")


def print_warn(msg: str):
    print(f"{Colors.YELLOW}⚠️  WARN{Colors.RESET} {msg}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  INFO{Colors.RESET} {msg}")


def validate_frontmatter(skill_path: Path) -> Tuple[bool, str]:
    """
    验证 SKILL.md frontmatter

    要求：
    1. 第一行必须是 ---
    2. 必须包含 name 和 description
    3. 不得在 --- 之前有 # 标题
    """
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    if not lines:
        return False, "SKILL.md 为空"

    # 检查第一行
    if lines[0].strip() != '---':
        # 检查是否有 markdown 标题
        for i, line in enumerate(lines[:5]):
            if line.strip().startswith('#'):
                return False, f"SKILL.md 第 {i+1} 行有 markdown 标题，应以 --- 开头"
        return False, "SKILL.md 应以 --- 开头"

    # 检查 frontmatter 结束
    try:
        end_idx = lines[1:].index('---') + 1
        frontmatter_text = '\n'.join(lines[:end_idx+1])
    except ValueError:
        return False, "SKILL.md 缺少结束 ---"

    # 解析 frontmatter - 使用 safe_load_all 只取第一个文档
    try:
        import yaml
        docs = list(yaml.safe_load_all(frontmatter_text))
        frontmatter = docs[0] if docs else None
    except yaml.YAMLError as e:
        return False, f"SKILL.md frontmatter YAML 格式错误: {str(e)[:100]}"
    except Exception as e:
        return False, f"SKILL.md frontmatter YAML 解析异常: {str(e)[:100]}"

    if not frontmatter:
        return False, "SKILL.md frontmatter 为空"

    # 检查必填字段
    if 'name' not in frontmatter:
        return False, "SKILL.md frontmatter 缺少 name 字段"

    if 'description' not in frontmatter:
        return False, "SKILL.md frontmatter 缺少 description 字段"

    # 检查 name 格式（连字符）
    name = frontmatter['name']
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        return False, f"SKILL.md name '{name}' 应使用连字符格式 (kebab-case)"

    return True, "SKILL.md frontmatter 验证通过"


def validate_meta_json(skill_path: Path) -> Tuple[bool, str]:
    """验证 _meta.json"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json 不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError:
        return False, "_meta.json JSON 格式错误"

    # 检查必填字段
    if 'id' not in meta:
        return False, "_meta.json 缺少 id 字段"

    if 'version' not in meta:
        return False, "_meta.json 缺少 version 字段"

    # 检查 id 是否为数字
    if not isinstance(meta['id'], (int, str)):
        return False, "_meta.json id 应为数字或字符串"

    # 检查 version 格式
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
        return False, f"_meta.json version '{version}' 应为 semver 格式 (x.y.z)"

    return True, "_meta.json 验证通过"


def validate_directory_structure(skill_path: Path) -> Tuple[bool, List[str]]:
    """验证目录结构"""
    errors = []

    # 检查顶层结构
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (skill_path / f).exists():
            errors.append(f"缺少必需文件: {f}")

    # 检查 layers 目录
    layers_dir = skill_path / "layers"
    if layers_dir.exists():
        required_layers = ['data_loader.py', 'data_validator.py', 'orchestrator.py']
        for f in required_layers:
            if not (layers_dir / f).exists():
                errors.append(f"layers/{f} 不存在")

    return len(errors) == 0, errors


def validate_naming(skill_path: Path) -> Tuple[bool, List[str]]:
    """验证命名合规性（无中文路径）"""
    errors = []

    # 检查所有文件和目录
    for root, dirs, files in os.walk(skill_path):
        root_path = Path(root)

        # 检查目录名
        for d in dirs:
            if re.search(r'[\u4e00-\u9fff]', d):
                errors.append(f"目录名包含中文: {root_path / d}")

        # 检查文件名
        for f in files:
            if re.search(r'[\u4e00-\u9fff]', f):
                errors.append(f"文件名包含中文: {root_path / f}")

    return len(errors) == 0, errors


def main():
    """主函数"""
    if len(sys.argv) < 2:
        skill_path = Path.cwd()
    else:
        skill_path = Path(sys.argv[1])

    print(f"\n{'='*60}")
    print(f"Universal Data Analyst - 技能验证")
    print(f"技能路径: {skill_path}")
    print(f"{'='*60}\n")

    all_passed = True

    # 1. Frontmatter 验证
    print_info("检查 SKILL.md frontmatter...")
    passed, msg = validate_frontmatter(skill_path)
    if passed:
        print_pass(msg)
    else:
        print_fail(msg)
        all_passed = False

    # 2. _meta.json 验证
    print_info("检查 _meta.json...")
    passed, msg = validate_meta_json(skill_path)
    if passed:
        print_pass(msg)
    else:
        print_fail(msg)
        all_passed = False

    # 3. 目录结构验证
    print_info("检查目录结构...")
    passed, errors = validate_directory_structure(skill_path)
    if passed:
        print_pass("目录结构完整")
    else:
        print_fail("目录结构不完整")
        for e in errors:
            print(f"   - {e}")
        all_passed = False

    # 4. 命名合规性验证
    print_info("检查命名合规性（无中文）...")
    passed, errors = validate_naming(skill_path)
    if passed:
        print_pass("命名合规")
    else:
        print_fail("存在中文路径")
        for e in errors:
            print(f"   - {e}")
        all_passed = False

    print(f"\n{'='*60}")
    if all_passed:
        print_pass("所有验证通过")
        return 0
    else:
        print_fail("存在验证失败项")
        return 1


if __name__ == '__main__':
    sys.exit(main())
