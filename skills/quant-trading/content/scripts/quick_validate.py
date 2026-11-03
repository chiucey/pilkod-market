#!/usr/bin/env python3
"""量化交易技能验证脚本"""

import os
import json
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证 SKILL.md frontmatter"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md 文件不存在"]

    content = skill_md.read_text(encoding="utf-8")

    # 检查是否以 --- 开头
    if not content.startswith("---"):
        errors.append("SKILL.md 必须以 YAML frontmatter 开始（---），不能以 # 标题开头")
        return False, errors

    # 提取 frontmatter
    lines = content.split("\n")
    in_frontmatter = False
    frontmatter_lines = []

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = "\n".join(frontmatter_lines)

    # 检查必需字段
    if "name:" not in frontmatter_text:
        errors.append("frontmatter 必须包含 name 字段")

    if "description:" not in frontmatter_text:
        errors.append("frontmatter 必须包含 description 字段")

    # 检查 name 是否与目录名匹配
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        dir_name = Path(skill_path).name
        if name_value != dir_name:
            errors.append(f"name 字段值 '{name_value}' 必须与文件夹名称 '{dir_name}' 匹配")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json"""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json 文件不存在"]

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json 格式错误: {e}"]

    # 检查必需字段
    if "id" not in meta:
        errors.append("_meta.json 必须包含 id 字段")
    elif not isinstance(meta["id"], (int, str)):
        errors.append("id 必须是数字或字符串")

    if "version" not in meta:
        errors.append("_meta.json 必须包含 version 字段")
    elif not isinstance(meta["version"], str):
        errors.append("version 必须是字符串格式（如 '1.0.0'）")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []
    skill_name = Path(skill_path).name

    # 检查目录名是否为英文和连字符
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        errors.append(f"目录名 '{skill_name}' 必须只包含小写字母、数字和连字符")

    # 检查 references 目录
    refs_dir = Path(skill_path) / "references"
    if refs_dir.exists():
        ref_files = list(refs_dir.glob("*.md"))
        if len(ref_files) == 0:
            errors.append("references 目录存在但为空，建议添加参考文档")

    return len(errors) == 0, errors


def main():
    skill_path = "/workspace/temp-skills/quant-trading"

    all_errors = []

    # 验证 frontmatter
    fm_ok, fm_errors = validate_frontmatter(skill_path)
    all_errors.extend(fm_errors)

    # 验证 meta.json
    meta_ok, meta_errors = validate_meta_json(skill_path)
    all_errors.extend(meta_errors)

    # 验证结构
    struct_ok, struct_errors = validate_structure(skill_path)
    all_errors.extend(struct_errors)

    # 输出结果
    print("=" * 50)
    print("量化交易技能验证结果")
    print("=" * 50)

    print(f"\n[1] Frontmatter 验证: {'✓ 通过' if fm_ok else '✗ 失败'}")
    if fm_errors:
        for e in fm_errors:
            print(f"    - {e}")

    print(f"\n[2] _meta.json 验证: {'✓ 通过' if meta_ok else '✗ 失败'}")
    if meta_errors:
        for e in meta_errors:
            print(f"    - {e}")

    print(f"\n[3] 结构验证: {'✓ 通过' if struct_ok else '✗ 失败'}")
    if struct_errors:
        for e in struct_errors:
            print(f"    - {e}")

    print("\n" + "=" * 50)

    if all_errors:
        print("验证失败！请修复以上问题。")
        sys.exit(1)
    else:
        print("✓ 所有验证通过！技能结构正确。")
        sys.exit(0)


if __name__ == "__main__":
    main()
