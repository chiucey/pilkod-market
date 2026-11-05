#!/usr/bin/env python3
"""
FCP Subtitle Maker Skill - Quick Validator
验证技能的 frontmatter、结构和脚本完整性
"""

import os
import re
import json
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证 SKILL.md 的 frontmatter"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, [f"Missing SKILL.md in {skill_path}"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查第一行是否为 ---
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        errors.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False, errors

    # 提取 frontmatter
    try:
        end_idx = content.index('---', 3)  # 找第二个 ---
        frontmatter_text = content[3:end_idx].strip()
    except ValueError:
        errors.append("Frontmatter not properly closed with ---")
        return False, errors

    # 检查必填字段
    if 'name:' not in frontmatter_text:
        errors.append("Missing 'name:' field in frontmatter")
    if 'description:' not in frontmatter_text:
        errors.append("Missing 'description:' field in frontmatter")

    # 提取 name 值
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        # 检查 name 格式（连字符）
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', name_value):
            errors.append(f"Invalid name format '{name_value}': must use lowercase with hyphens")
        # 检查 name 长度
        if len(name_value) > 64:
            errors.append(f"Name too long ({len(name_value)} chars): {name_value}")
        # 检查 name 是否与文件夹名匹配
        folder_name = skill_path.name
        if name_value != folder_name:
            errors.append(f"Name mismatch: frontmatter='{name_value}' but folder='{folder_name}'")

    # 提取 description
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 10:
            errors.append("description too short (need at least 10 chars)")
        if len(desc_value) > 500:
            errors.append(f"description too long ({len(desc_value)} chars): max 500")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """验证 _meta.json"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["Missing _meta.json"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in _meta.json: {e}"]

    # 检查必填字段
    if "id" not in meta:
        errors.append("Missing 'id' in _meta.json")
    if "version" not in meta:
        errors.append("Missing 'version' in _meta.json")

    # 验证 id 格式（应该是数字字符串）
    if "id" in meta:
        if not str(meta["id"]).isdigit():
            errors.append(f"Invalid id format: {meta['id']} (must be numeric string)")

    # 验证 version 格式（语义化版本）
    if "version" in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
            errors.append(f"Invalid version format: {meta['version']} (use semver like 1.0.0)")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查 scripts 目录
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        # 检查 generate_fcpxml.py 是否存在
        fcpxml_script = scripts_dir / "generate_fcpxml.py"
        if fcpxml_script.exists():
            # 检查脚本是否有 __main__ 或命令行入口
            content = fcpxml_script.read_text(encoding="utf-8")
            if "if __name__" not in content:
                errors.append("generate_fcpxml.py missing if __name__ == '__main__' block")

    return len(errors) == 0, errors


def validate_naming(skill_path: Path) -> tuple[bool, list[str]]:
    """验证所有文件名和路径都是英文"""
    errors = []
    forbidden_patterns = [
        r'[\u4e00-\u9fff]',  # 中文
        r'[\u3040-\u30ff]',  # 日文
        r'[\uac00-\ud7af]',  # 韩文
    ]

    for root, dirs, files in os.walk(skill_path):
        for d in dirs:
            for pattern in forbidden_patterns:
                if re.search(pattern, d):
                    errors.append(f"Non-ASCII directory name: {d}")
        for f in files:
            for pattern in forbidden_patterns:
                if re.search(pattern, f):
                    errors.append(f"Non-ASCII file name: {f}")

    return len(errors) == 0, errors


def validate_scripts(skill_path: Path) -> tuple[bool, list[str]]:
    """验证脚本语法和基本功能"""
    errors = []
    scripts_dir = skill_path / "scripts"

    if not scripts_dir.exists():
        return True, []  # 没有 scripts 目录也是可以的

    fcpxml_script = scripts_dir / "generate_fcpxml.py"
    if not fcpxml_script.exists():
        return True, []

    # 检查 Python 语法
    try:
        import ast
        content = fcpxml_script.read_text(encoding="utf-8")
        ast.parse(content)
    except SyntaxError as e:
        errors.append(f"Syntax error in generate_fcpxml.py: {e}")
    except Exception as e:
        errors.append(f"Error reading generate_fcpxml.py: {e}")

    return len(errors) == 0, errors


def run_validation(skill_path: str) -> bool:
    """运行所有验证"""
    skill = Path(skill_path)
    all_passed = True
    all_errors = []

    checks = [
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta_json),
        ("Structure", validate_structure),
        ("Naming (ASCII only)", validate_naming),
        ("Scripts", validate_scripts),
    ]

    for name, validator in checks:
        passed, errors = validator(skill)
        if not passed:
            all_passed = False
            all_errors.append(f"\n[{name}] FAILED:")
            for err in errors:
                all_errors.append(f"  - {err}")
        else:
            print(f"✓ [{name}] passed")

    if all_errors:
        print("\n".join(all_errors))

    return all_passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent  # 默认当前目录
    else:
        skill_path = sys.argv[1]

    print(f"Validating skill: {skill_path}")
    print("-" * 50)

    if run_validation(skill_path):
        print("-" * 50)
        print("✓ All validations PASSED")
        sys.exit(0)
    else:
        print("-" * 50)
        print("✗ Validation FAILED")
        sys.exit(1)
