#!/usr/bin/env python3
"""
OpenClaw Expert 技能验证脚本
验证 SKILL.md 结构和 _meta.json 格式
"""

import os
import sys
import json
import re
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证 SKILL.md 的 frontmatter"""
    errors = []
    skillyaml_path = skill_path / "SKILL.md"

    if not skillyaml_path.exists():
        return False, ["SKILL.md 文件不存在"]

    content = skillyaml_path.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.startswith("---"):
        errors.append("SKILL.md 必须以 --- 开头（frontmatter 开始标记）")
        return False, errors

    # 提取 frontmatter
    lines = content.split("\n")
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append((i, line))

    # 检查必填字段
    frontmatter_text = "\n".join([line for _, line in frontmatter_lines])

    if "name:" not in frontmatter_text:
        errors.append("Frontmatter 必须包含 'name' 字段")

    if "description:" not in frontmatter_text:
        errors.append("Frontmatter 必须包含 'description' 字段")

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if " " in name_value or not name_value.replace("-", "").isalnum():
            errors.append(f"name 必须使用连字符格式: {name_value}")

    return len(errors) == 0, errors

def validate_meta(skill_path: Path) -> tuple[bool, list[str]]:
    """验证 _meta.json"""
    errors = []
    meta_path = skill_path / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json 格式错误: {e}"]

    if "id" not in meta:
        errors.append("_meta.json 必须包含 'id' 字段")

    if "version" not in meta:
        errors.append("_meta.json 必须包含 'version' 字段")

    return len(errors) == 0, errors

def validate_directory_name(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录名称"""
    errors = []
    name = skill_path.name

    if not name.replace("-", "").isalnum():
        errors.append(f"目录名应使用英文字母和连字符: {name}")

    if name != name.lower():
        errors.append(f"目录名应使用小写: {name}")

    return len(errors) == 0, errors

def main():
    if len(sys.argv) < 2:
        print("用法: python validate_skill.py <skill-path>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    all_passed = True

    print(f"验证技能: {skill_path.name}")
    print("-" * 40)

    # 验证目录名
    passed, errors = validate_directory_name(skill_path)
    if not passed:
        for err in errors:
            print(f"❌ 目录名: {err}")
        all_passed = False
    else:
        print("✓ 目录名格式正确")

    # 验证 frontmatter
    passed, errors = validate_frontmatter(skill_path)
    if not passed:
        for err in errors:
            print(f"❌ Frontmatter: {err}")
        all_passed = False
    else:
        print("✓ Frontmatter 格式正确")

    # 验证 _meta.json
    passed, errors = validate_meta(skill_path)
    if not passed:
        for err in errors:
            print(f"❌ _meta.json: {err}")
        all_passed = False
    else:
        print("✓ _meta.json 格式正确")

    print("-" * 40)

    if all_passed:
        print("✓ 所有验证通过!")
        sys.exit(0)
    else:
        print("❌ 验证失败，请修复以上问题")
        sys.exit(1)

if __name__ == "__main__":
    main()
