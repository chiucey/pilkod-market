#!/usr/bin/env python3
"""
供应商信息提取技能验证脚本
验证SKILL.md的frontmatter格式和结构完整性
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证frontmatter格式和必填字段"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, [f"SKILL.md not found at {skill_md}"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查frontmatter是否在第一行
    if not content.startswith("---"):
        errors.append("Frontmatter must start at line 1 (no markdown title before ---)")

    # 提取frontmatter
    frontmatter_pattern = r"^---\n(.*?)\n---"
    match = re.search(frontmatter_pattern, content, re.DOTALL)

    if not match:
        errors.append("Frontmatter not found or malformed")
        return False, errors

    frontmatter_content = match.group(1)

    # 验证必填字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf"^{field}:\s*.+", frontmatter_content, re.MULTILINE):
            errors.append(f"Missing required frontmatter field: {field}")

    # 验证name格式（连字符格式）
    name_match = re.search(r"^name:\s*(.+)", frontmatter_content, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name_value):
            errors.append(f"Invalid name format: '{name_value}' (use hyphen-case)")
        if len(name_value) > 64:
            errors.append(f"Name too long: {len(name_value)} chars (max 64)")

    # 验证description包含触发短语
    desc_match = re.search(r"^description:\s*(.+)", frontmatter_content, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if len(desc_value) < 20:
            errors.append("Description too short (min 20 chars)")
        if not any(keyword in desc_value.lower() for keyword in ["供应商", "vendor", "提取", "extract"]):
            errors.append("Description should mention 'vendor' or 'extract' related keywords")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证_meta.json文件"""
    import json
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json not found"]

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # 验证必填字段
    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required field in _meta.json: {field}")

    # 验证id是整数
    if "id" in meta and not isinstance(meta["id"], int):
        errors.append("Field 'id' must be an integer")

    # 验证version格式
    if "version" in meta:
        version = meta["version"]
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append(f"Invalid version format: {version} (expected X.Y.Z)")

    return len(errors) == 0, errors


def main():
    skill_path = "/workspace/temp-skills/vendor-info-extractor"

    print("=" * 50)
    print("供应商信息提取技能 - 验证脚本")
    print("=" * 50)

    all_passed = True

    # 验证frontmatter
    print("\n[1] 验证 Frontmatter 格式...")
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("    ✓ Frontmatter 格式正确")
    else:
        all_passed = False
        for err in errors:
            print(f"    ✗ {err}")

    # 验证meta.json
    print("\n[2] 验证 _meta.json 文件...")
    passed, errors = validate_meta_json(skill_path)
    if passed:
        print("    ✓ _meta.json 格式正确")
    else:
        all_passed = False
        for err in errors:
            print(f"    ✗ {err}")

    # 验证目录结构
    print("\n[3] 验证目录结构...")
    expected_dirs = ["scripts", "references", "assets"]
    for dir_name in expected_dirs:
        dir_path = Path(skill_path) / dir_name
        if dir_path.exists():
            print(f"    ✓ {dir_name}/ 目录存在")
        else:
            print(f"    ⚠ {dir_name}/ 目录不存在（非必需）")

    print("\n" + "=" * 50)
    if all_passed:
        print("验证结果: 全部通过 ✓")
        return 0
    else:
        print("验证结果: 存在问题 ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
