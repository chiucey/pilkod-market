#!/usr/bin/env python3
"""播客助手技能验证脚本"""

import os
import json
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证SKILL.md的frontmatter格式"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以---开头
    if not content.strip().startswith("---"):
        errors.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False, errors

    # 提取frontmatter
    lines = content.split("\n")
    if len(lines) < 3:
        errors.append("Frontmatter too short")
        return False, errors

    # 解析frontmatter
    try:
        fm_end = content.index("---", 3) + 3
        fm_text = content[3:fm_end-3].strip()
    except ValueError:
        errors.append("Missing closing --- in frontmatter")
        return False, errors

    # 检查必需字段
    if "name:" not in fm_text:
        errors.append("Missing 'name:' field in frontmatter")
    if "description:" not in fm_text:
        errors.append("Missing 'description:' field in frontmatter")

    # 检查description触发短语
    desc_match = re.search(r'description:\s*(.+)', fm_text)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            errors.append("Description too short, should include trigger phrases")
        if "当用户" not in desc and "Use when" not in desc.lower():
            errors.append("Description should include trigger phrase like '当用户说...'"  )

    return len(errors) == 0, errors


def validate_meta(skill_path: Path) -> tuple[bool, list[str]]:
    """验证_meta.json"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    required_fields = ["id", "version", "name"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required field: {field}")

    # 验证版本格式
    if "version" in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta["version"]):
            errors.append("Version should follow semantic versioning (e.g., 1.0.0)")

    # 验证ID是整数
    if "id" in meta:
        if not isinstance(meta["id"], int):
            errors.append("ID should be an integer")

    return len(errors) == 0, errors


def validate_naming(skill_path: Path) -> tuple[bool, list[str]]:
    """验证命名规范"""
    errors = []
    folder_name = skill_path.name

    # 检查是否使用连字符格式
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', folder_name):
        errors.append("Folder name should use hyphen-case (e.g., podcast-assistant)")

    # SKILL.md中的name应该匹配文件夹名
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if name_match:
            yaml_name = name_match.group(1).strip()
            if yaml_name != folder_name:
                errors.append(f"SKILL.md name ({yaml_name}) should match folder name ({folder_name})")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    warnings = []

    # 检查scripts目录
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        if (scripts_dir / "package_skill.py").exists():
            print("  [OK] package_skill.py found")

    # 检查references目录
    if not (skill_path / "references").exists():
        warnings.append("No references/ directory (optional)")

    return True, warnings


def main():
    skill_path = Path("/workspace/temp-skills/podcast-assistant")

    print("=" * 50)
    print("播客助手 - 技能验证")
    print("=" * 50)

    all_passed = True

    # 1. Frontmatter验证
    print("\n[1] Frontmatter 验证...")
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("  [PASS] Frontmatter格式正确")
    else:
        print("  [FAIL]")
        for e in errors:
            print(f"    - {e}")
        all_passed = False

    # 2. Meta验证
    print("\n[2] _meta.json 验证...")
    passed, errors = validate_meta(skill_path)
    if passed:
        print("  [PASS] Meta配置正确")
    else:
        print("  [FAIL]")
        for e in errors:
            print(f"    - {e}")
        all_passed = False

    # 3. 命名验证
    print("\n[3] 命名规范验证...")
    passed, errors = validate_naming(skill_path)
    if passed:
        print("  [PASS] 命名规范正确")
    else:
        print("  [FAIL]")
        for e in errors:
            print(f"    - {e}")
        all_passed = False

    # 4. 结构验证
    print("\n[4] 目录结构验证...")
    passed, warnings = validate_structure(skill_path)
    if passed:
        print("  [PASS] 目录结构合理")
    for w in warnings:
        print(f"    [NOTE] {w}")

    print("\n" + "=" * 50)
    if all_passed:
        print("验证结果: 全部通过 ✓")
        return 0
    else:
        print("验证结果: 存在问题 ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
