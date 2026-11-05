#!/usr/bin/env python3
"""
快速验证脚本 - 检查SKILL.md和_meta.json的基本格式
"""

import json
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: Path) -> tuple:
    """验证SKILL.md的frontmatter格式"""
    content = skill_md_path.read_text(encoding="utf-8")

    # 检查是否以---开头
    if not content.strip().startswith("---"):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # 提取frontmatter
    lines = content.split("\n")
    if len(lines) < 3:
        return False, "SKILL.md frontmatter incomplete"

    # 检查frontmatter结构
    frontmatter_lines = []
    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    # 检查必需字段
    frontmatter_text = "\n".join(frontmatter_lines)

    if "name:" not in frontmatter_text:
        return False, "Missing 'name:' field in frontmatter"

    if "description:" not in frontmatter_text:
        return False, "Missing 'description:' field in frontmatter"

    # 提取name值
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        # 检查名称是否使用连字符格式
        if not re.match(r'^[a-z0-9-]+$', name_value):
            return False, f"name '{name_value}' should use hyphen-case format (lowercase with hyphens)"

    return True, "Frontmatter validation passed"


def validate_meta_json(meta_path: Path) -> tuple:
    """验证_meta.json格式"""
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Cannot read file: {e}"

    # 检查必需字段
    if "id" not in meta:
        return False, "Missing 'id' field in _meta.json"

    if "version" not in meta:
        return False, "Missing 'version' field in _meta.json"

    # 验证id格式
    id_value = meta["id"]
    if not re.match(r'^[a-z0-9-]+$', id_value):
        return False, f"id '{id_value}' should use hyphen-case format"

    # 验证version格式
    version = meta["version"]
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"version '{version}' should use semver format (e.g., 1.0.0)"

    return True, "_meta.json validation passed"


def validate_directory_structure(skill_dir: Path) -> tuple:
    """验证目录结构"""
    required_dirs = ["scripts", "references"]

    for dir_name in required_dirs:
        dir_path = skill_dir / dir_name
        if not dir_path.exists():
            return False, f"Missing directory: {dir_name}"

    return True, "Directory structure validation passed"


def main():
    """主验证流程"""
    # 获取skill目录
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent

    print("=" * 50)
    print("JPAF Skill Quick Validation")
    print("=" * 50)
    print(f"Skill directory: {skill_dir}\n")

    all_passed = True

    # 验证SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        passed, msg = validate_frontmatter(skill_md)
        print(f"SKILL.md: {'✓' if passed else '✗'} {msg}")
        if not passed:
            all_passed = False
    else:
        print(f"SKILL.md: ✗ File not found")
        all_passed = False

    # 验证_meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        passed, msg = validate_meta_json(meta_json)
        print(f"_meta.json: {'✓' if passed else '✗'} {msg}")
        if not passed:
            all_passed = False
    else:
        print(f"_meta.json: ✗ File not found")
        all_passed = False

    # 验证目录结构
    passed, msg = validate_directory_structure(skill_dir)
    print(f"Structure: {'✓' if passed else '✗'} {msg}")
    if not passed:
        all_passed = False

    print("=" * 50)

    if all_passed:
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
