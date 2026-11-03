#!/usr/bin/env python3
"""
LangGraph 技能验证脚本
验证 SKILL.md 结构、frontmatter 和资源完整性
"""

import json
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_dir: Path) -> tuple[bool, list[str]]:
    """验证 frontmatter 格式和内容"""
    errors = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查 frontmatter 是否在文件开头
    if not content.strip().startswith("---"):
        errors.append("Frontmatter must start at the beginning of the file")

    # 提取 frontmatter
    frontmatter_match = re.match(
        r"^---\n(.*?)\n---",
        content,
        re.DOTALL
    )

    if not frontmatter_match:
        errors.append("Frontmatter not found or malformed")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # 验证必填字段
    if not re.search(r"^name:", frontmatter, re.MULTILINE):
        errors.append("Missing 'name' field in frontmatter")

    if not re.search(r"^description:", frontmatter, re.MULTILINE):
        errors.append("Missing 'description' field in frontmatter")

    # 验证 name 格式
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"Invalid name format: '{name}'. Use lowercase with hyphens only")

        if len(name) > 64:
            errors.append(f"Name too long: {len(name)} chars (max 64)")

    return len(errors) == 0, errors


def validate_meta_json(skill_dir: Path) -> tuple[bool, list[str]]:
    """验证 _meta.json 格式"""
    errors = []
    meta_file = skill_dir / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # 验证必填字段
    if "id" not in meta:
        errors.append("Missing 'id' field in _meta.json")

    if "version" not in meta:
        errors.append("Missing 'version' field in _meta.json")

    return len(errors) == 0, errors


def validate_structure(skill_dir: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查目录名是否为英文
    if not re.match(r"^[a-z0-9-]+$", skill_dir.name):
        errors.append(f"Invalid directory name: '{skill_dir.name}'. Use English only")

    # 检查必要的文件
    required_files = ["SKILL.md", "_meta.json"]
    for fname in required_files:
        if not (skill_dir / fname).exists():
            errors.append(f"Missing required file: {fname}")

    return len(errors) == 0, errors


def main():
    """主验证流程"""
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])

    all_errors = []
    all_passed = True

    # 1. 结构验证
    passed, errors = validate_structure(skill_dir)
    all_passed &= passed
    if not passed:
        all_errors.extend(["[Structure] " + e for e in errors])

    # 2. Frontmatter 验证
    if all_passed or (skill_dir / "SKILL.md").exists():
        passed, errors = validate_frontmatter(skill_dir)
        all_passed &= passed
        if not passed:
            all_errors.extend(["[Frontmatter] " + e for e in errors])

    # 3. Meta JSON 验证
    if all_passed or (skill_dir / "_meta.json").exists():
        passed, errors = validate_meta_json(skill_dir)
        all_passed &= passed
        if not passed:
            all_errors.extend(["[Meta] " + e for e in errors])

    # 输出结果
    if all_passed:
        print("✓ Validation passed")
        sys.exit(0)
    else:
        print("✗ Validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
