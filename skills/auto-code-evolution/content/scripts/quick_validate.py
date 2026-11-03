#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和内容完整性
"""

import os
import re
import json
import yaml
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证SKILL.md的frontmatter格式"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以---开头
    if not content.startswith("---"):
        errors.append("SKILL.md must start with frontmatter (---)")
        return False, errors

    # 提取frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
        return False, errors

    # 解析frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
    except:
        errors.append("Invalid YAML in frontmatter")
        return False, errors

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # 检查name格式（连字符）
    if "name" in frontmatter:
        if not re.match(r"^[a-z0-9-]+$", frontmatter["name"]):
            errors.append("name must be hyphen-case (lowercase with hyphens)")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """验证_meta.json的存在和格式"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, ["Invalid JSON in _meta.json"]

    # 检查必需字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required field: {field}")

    # 验证version格式 (semver)
    if "version" in meta:
        if not re.match(r"^\d+\.\d+\.\d+$", meta["version"]):
            errors.append("version must follow semantic versioning (x.y.z)")

    return len(errors) == 0, errors


def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查必需文件
    if not (skill_path / "SKILL.md").exists():
        errors.append("Missing SKILL.md")

    if not (skill_path / "_meta.json").exists():
        errors.append("Missing _meta.json")

    return len(errors) == 0, errors


def main():
    skill_path = Path(__file__).parent.parent
    print(f"Validating skill at: {skill_path}")

    all_errors = []

    # 运行所有验证
    checks = [
        ("Structure", validate_structure),
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta_json),
    ]

    all_passed = True
    for name, check_func in checks:
        passed, errors = check_func(skill_path)
        if passed:
            print(f"✅ {name}: PASS")
        else:
            print(f"❌ {name}: FAIL")
            for err in errors:
                print(f"   - {err}")
            all_passed = False
            all_errors.extend(errors)

    if all_passed:
        print("\n✅ All validations passed!")
        return 0
    else:
        print(f"\n❌ Validation failed with {len(all_errors)} errors")
        return 1


if __name__ == "__main__":
    exit(main())
