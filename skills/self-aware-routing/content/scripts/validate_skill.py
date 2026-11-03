#!/usr/bin/env python3
"""
Self-Aware Routing 技能验证脚本
验证 SKILL.md 和 _meta.json 的格式正确性
"""

import json
import os
import sys
import re
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.startswith("---"):
        return False, "SKILL.md must start with --- frontmatter delimiter"

    # 提取 frontmatter
    lines = content.split("\n")
    if len(lines) < 4:
        return False, "Frontmatter too short"

    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter not properly closed with ---"

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf"^{field}:", frontmatter_text, re.MULTILINE):
            return False, f"Missing required field: {field}"

    # 检查 name 格式
    name_match = re.search(r"^name:\s*(.+)$", frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, f"Invalid name format: {name}. Use lowercase with hyphens only"

    return True, "Frontmatter validated"


def validate_meta(skill_path: Path) -> tuple[bool, str]:
    """验证 _meta.json 格式"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json not found"

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # 检查必需字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field: {field}"

    # 验证 version 格式（语义化版本）
    version = meta["version"]
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        return False, f"Invalid version format: {version}. Use semantic versioning (e.g., 1.0.0)"

    return True, "_meta.json validated"


def validate_directory_structure(skill_path: Path) -> tuple[bool, str]:
    """验证目录结构"""
    required_files = ["SKILL.md", "_meta.json"]

    for filename in required_files:
        if not (skill_path / filename).exists():
            return False, f"Missing required file: {filename}"

    # 可选目录检查
    optional_dirs = ["references", "scripts", "assets"]
    for dirname in optional_dirs:
        dir_path = skill_path / dirname
        if dir_path.exists() and not dir_path.is_dir():
            return False, f"{dirname} should be a directory"

    return True, "Directory structure validated"


def main():
    # 支持命令行参数或默认路径
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 1. 目录结构验证
    result, msg = validate_directory_structure(skill_path)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    # 2. Frontmatter 验证
    result, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    # 3. Meta JSON 验证
    result, msg = validate_meta(skill_path)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        sys.exit(0)
    else:
        print("✗ Validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()